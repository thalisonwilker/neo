"""Resolvedor de provedores Git (Bitbucket e GitHub) com auto-detecção e precedência."""

from __future__ import annotations

import logging
import re
import subprocess
from typing import Protocol, runtime_checkable

import typer

from neo.config import (
    GitProviderType,
    get_credential,
    get_default_provider_config,
    validate_git_provider,
)
from neo.integrations.bitbucket import BitbucketClient
from neo.integrations.bitbucket_models import (
    BitbucketCommit,
    BitbucketRepo,
    BitbucketWorkspace,
)
from neo.integrations.github import GitHubClient
from neo.output import print_error

logger = logging.getLogger(__name__)


@runtime_checkable
class GitProviderProtocol(Protocol):
    """Protocolo comum que qualquer provedor Git (Bitbucket, GitHub) deve implementar."""

    def list_repositories(self, workspace: str | None = None) -> list[BitbucketRepo]: ...

    def search_repositories(
        self, query: str, workspace: str | None = None
    ) -> list[BitbucketRepo]: ...

    def get_repository(self, repo_slug: str, workspace: str | None = None) -> BitbucketRepo: ...

    def create_repository(
        self,
        name: str,
        workspace: str | None = None,
        is_private: bool = True,
        description: str | None = None,
    ) -> BitbucketRepo: ...

    def list_commits(
        self,
        repo_slug: str,
        workspace: str | None = None,
        author: str | None = None,
        query: str | None = None,
        limit: int = 20,
    ) -> list[BitbucketCommit]: ...

    def list_workspaces(self) -> list[BitbucketWorkspace]: ...

    def get_default_workspace(self, ignore_config: bool = False) -> str: ...


def detect_git_remote_info() -> tuple[GitProviderType | None, str | None]:
    """Detecta o provedor Git e o slug do repositório a partir do remote origin local."""
    try:
        res = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and isinstance(res.stdout, str):
            url = res.stdout.strip()
            # GitHub: git@github.com:owner/repo.git ou https://github.com/owner/repo.git
            m_gh = re.search(r"github\.com[:/][^/]+/([^/.]+)(?:\.git)?", url)
            if m_gh:
                return "github", m_gh.group(1)

            # Bitbucket: git@bitbucket.org:workspace/repo.git ou https://bitbucket.org/workspace/repo.git
            m_bb = re.search(r"bitbucket\.org[:/][^/]+/([^/.]+)(?:\.git)?", url)
            if m_bb:
                return "bitbucket", m_bb.group(1)
    except (subprocess.SubprocessError, OSError) as exc:
        logger.debug("Falha ao consultar git remote: %s", exc)

    return None, None


def resolve_git_provider(
    provider_arg: str | None = None, as_json: bool = False
) -> tuple[GitProviderType, GitProviderProtocol]:
    """Resolve o provedor Git e instancia o cliente correspondente seguindo a precedência:

    1. Flag explícita (`--provider` / `-p`)
    2. Auto-detecção a partir do remote `origin` do git local
    3. Preferência persistida em `config.toml` (`default_provider`)
    4. Fallback (serviço com credenciais ativas ou bitbucket por padrão)
    """
    provider_name: GitProviderType

    # 1. Flag explícita
    if provider_arg:
        try:
            provider_name = validate_git_provider(provider_arg)
        except ValueError as err:
            print_error(str(err), as_json=as_json, code=1)
            raise typer.Exit(code=1) from err
    else:
        # 2. Auto-detecção via git local
        detected_prov, _ = detect_git_remote_info()
        if detected_prov:
            provider_name = detected_prov
        else:
            # 3. Configuração salva em config.toml
            cfg_prov = get_default_provider_config()
            if cfg_prov:
                provider_name = cfg_prov
            else:
                # 4. Fallback para quem tiver token configurado ou bitbucket
                has_github = get_credential("github") is not None
                has_bitbucket = get_credential("bitbucket") is not None
                if has_github and not has_bitbucket:
                    provider_name = "github"
                else:
                    provider_name = "bitbucket"

    # Obtém credenciais e instancia o cliente
    token = get_credential(provider_name)
    if not token:
        service_label = "GitHub" if provider_name == "github" else "Bitbucket"
        msg = (
            f"Credenciais do {service_label} não configuradas. "
            f"Execute `neo config auth set {provider_name}`."
        )
        print_error(msg, as_json=as_json, code=1)
        raise typer.Exit(code=1)

    client: GitProviderProtocol
    if provider_name == "github":
        client = GitHubClient(token=token)
    else:
        client = BitbucketClient(token=token)

    return provider_name, client
