"""Resolvedor de provedores e contexto Git (Bitbucket e GitHub) com precedência estrita."""

from __future__ import annotations

import logging
import os
import re
import subprocess
from typing import NoReturn

import typer

from neo.config import (
    ExitCode,
    GitProviderType,
    get_credential,
    get_default_provider_config,
    get_default_workspace_config,
    validate_git_provider,
)
from neo.git_context import resolve_repo_path, selected_repo
from neo.integrations.git.api.bitbucket.client import BitbucketClient
from neo.integrations.git.api.github.client import GitHubClient
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.provider import GitProvider
from neo.output import print_error

logger = logging.getLogger(__name__)


def detect_git_remote_details() -> tuple[GitProviderType | None, str | None, str | None]:
    """Detecta (provedor, workspace/owner, slug do repositório) a partir do remote origin local."""
    try:
        selected = selected_repo()
        cwd = resolve_repo_path() if selected else None
        res = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )
        if res.returncode == 0 and isinstance(res.stdout, str):
            url = res.stdout.strip()
            m_gh = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?", url)
            if m_gh:
                return "github", m_gh.group(1), m_gh.group(2)

            m_bb = re.search(r"bitbucket\.org[:/]([^/]+)/([^/.]+)(?:\.git)?", url)
            if m_bb:
                return "bitbucket", m_bb.group(1), m_bb.group(2)
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        logger.debug("Falha ao consultar git remote: %s", exc)

    return None, None, None


def detect_git_remote_info() -> tuple[GitProviderType | None, str | None]:
    """Detecta o provedor Git e o slug do repositório a partir do remote origin local."""
    prov, _ws, slug = detect_git_remote_details()
    return prov, slug


def resolve_git_provider_and_source(
    provider_arg: str | None = None,
) -> tuple[GitProviderType, str]:
    """Resolve o provedor Git e sua fonte seguindo a precedência estrita:

    1. Opção de linha de comando (`--provider`) -> 'cli'
    2. Variável de ambiente (`NEO_GIT_PROVIDER`) -> 'env'
    3. Seção `[git]` do `config.toml` (`provider`) -> 'config'
    4. Auto-detecção pelo `remote origin` local -> 'remote'
    5. Padrão -> 'default'
    """
    if provider_arg:
        return validate_git_provider(provider_arg), "cli"

    env_prov = os.environ.get("NEO_GIT_PROVIDER", "").strip()
    if env_prov:
        return validate_git_provider(env_prov), "env"

    cfg_prov = get_default_provider_config()
    if cfg_prov:
        return cfg_prov, "config"

    detected_prov, _ = detect_git_remote_info()
    if detected_prov:
        return detected_prov, "remote"

    has_github = get_credential("github") is not None
    has_bitbucket = get_credential("bitbucket") is not None
    if has_github and not has_bitbucket:
        return "github", "default"
    return "bitbucket", "default"


def resolve_git_workspace_and_source(
    provider: GitProviderType,
    workspace_arg: str | None = None,
) -> tuple[str | None, str]:
    """Resolve o workspace configurado/detectado (sem chamar API) seguindo a precedência:

    1. Opção de linha de comando (`--workspace`) -> 'cli'
    2. Variável de ambiente (`NEO_GIT_WORKSPACE`) -> 'env'
    3. Seção `[git]` do `config.toml` (`workspace`) -> 'config'
    4. Auto-detecção pelo `remote origin` local -> 'remote'
    5. Não definido localmente -> 'default'
    """
    if workspace_arg and workspace_arg.strip():
        return workspace_arg.strip(), "cli"

    env_ws = os.environ.get("NEO_GIT_WORKSPACE", "").strip()
    if env_ws:
        return env_ws, "env"

    cfg_ws = get_default_workspace_config(provider=provider)
    if cfg_ws:
        return cfg_ws, "config"

    rem_prov, rem_ws, _rem_repo = detect_git_remote_details()
    if rem_prov == provider and rem_ws:
        return rem_ws, "remote"

    return None, "default"


def create_git_provider(provider: GitProviderType, token: str) -> GitProvider:
    """Compõe o adapter sem consultar nem persistir credenciais."""
    if provider == "github":
        return GitHubClient(token=token)
    return BitbucketClient(token=token)


def resolve_git_provider(
    provider_arg: str | None = None, as_json: bool = False
) -> tuple[GitProviderType, GitProvider]:
    """Resolve o provedor Git e instancia o cliente autenticado correspondente."""
    try:
        provider_name, _source = resolve_git_provider_and_source(provider_arg)
    except ValueError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR)) from err

    token = get_credential(provider_name)
    if not token:
        service_label = "GitHub" if provider_name == "github" else "Bitbucket"
        msg = (
            f"Credenciais do {service_label} não configuradas. "
            "Configure o provedor e execute `neo git config set api-key`."
        )
        print_error(msg, as_json=as_json, code=int(ExitCode.AUTH_ERROR))
        raise typer.Exit(code=int(ExitCode.AUTH_ERROR))

    return provider_name, create_git_provider(provider_name, token)


def handle_git_provider_error(exc: GitProviderError, as_json: bool = False) -> NoReturn:
    """Emite erro com o código de saída semântico da exceção (`3`, `4`, `5` ou `1`)."""
    exit_code = getattr(exc, "exit_code", int(ExitCode.ERROR))
    print_error(str(exc), as_json=as_json, code=exit_code)
    raise typer.Exit(code=exit_code) from exc
