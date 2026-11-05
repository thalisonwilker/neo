"""Funções compartilhadas dos comandos Git."""

from __future__ import annotations

import subprocess
from typing import NoReturn
from urllib.parse import urlsplit, urlunsplit

import typer

from neo.config import (
    ExitCode,
    GitProviderType,
    get_credential_source,
    get_git_config_value,
    validate_git_provider,
)
from neo.git_context import (
    resolve_repo_path,
    selected_repo,
)
from neo.output import (
    print_error,
)


def _fail_usage(message: str, as_json: bool) -> NoReturn:
    print_error(message, as_json=as_json, code=int(ExitCode.USAGE_ERROR))
    raise typer.Exit(code=int(ExitCode.USAGE_ERROR))


def _configured_provider(as_json: bool) -> GitProviderType:
    """Obtém apenas um provedor explicitamente configurado, sem inferir do remote."""
    try:
        _, provider, source = get_git_config_value("provider")
        if not provider or source not in ("config", "env"):
            _fail_usage(
                "Configure primeiro o provedor com `neo git config set provider <github|bitbucket>`.",
                as_json=as_json,
            )
        return validate_git_provider(provider)
    except ValueError as exc:
        _fail_usage(str(exc), as_json=as_json)


def _api_key_info() -> dict[str, str | None]:
    """Retorna estado e origem, sem ler ou expor o segredo."""
    try:
        _, provider, source = get_git_config_value("provider")
        if not provider or source not in ("env", "config"):
            return {"value": None, "source": "none"}
        valid_provider = validate_git_provider(provider)
        credential_source = get_credential_source(valid_provider)
    except ValueError:
        credential_source = None
    return {
        "value": "Configurado" if credential_source else None,
        "source": credential_source or "none",
    }


def _inspect_local_git_status() -> dict[str, object]:
    """Inspeciona o diretório atual via comandos git locais."""
    try:
        selected = selected_repo()
        cwd = resolve_repo_path() if selected else None
        res_inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )
        if res_inside.returncode != 0 or res_inside.stdout.strip().lower() != "true":
            return {
                "is_git_repo": False,
                "current_branch": None,
                "clean": None,
                "modified_files": 0,
                "remote_url": None,
            }

        res_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )
        branch = res_branch.stdout.strip() if res_branch.returncode == 0 else None

        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )
        lines = (
            [ln for ln in res_status.stdout.splitlines() if ln.strip()]
            if res_status.returncode == 0
            else []
        )

        res_remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )
        remote_url = res_remote.stdout.strip() if res_remote.returncode == 0 else None
        if remote_url and "://" in remote_url:
            parts = urlsplit(remote_url)
            remote_url = urlunsplit(
                (parts.scheme, parts.netloc.rsplit("@", 1)[-1], parts.path, "", "")
            )

        return {
            "is_git_repo": True,
            "current_branch": branch or "HEAD (detached)",
            "clean": len(lines) == 0,
            "modified_files": len(lines),
            "remote_url": remote_url or None,
        }
    except (subprocess.SubprocessError, OSError, ValueError):
        return {
            "is_git_repo": False,
            "current_branch": None,
            "clean": None,
            "modified_files": 0,
            "remote_url": None,
        }
