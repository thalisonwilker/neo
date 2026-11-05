"""Criação e publicação de repositórios locais e edição de descrição remota."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from neo.config import get_credential, get_git_config_value
from neo.git_context import select_repo
from neo.integrations.git.resolver import (
    detect_git_remote_details,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)


def _run_git(path: Path, *args: str, env: dict[str, str] | None = None) -> None:
    """Executa Git sem incluir mensagens possivelmente sensíveis na saída."""
    result = subprocess.run(
        ["git", "-C", str(path), *args], capture_output=True, text=True, check=False, env=env
    )
    if result.returncode:
        raise RuntimeError(
            "O comando Git falhou. Verifique a configuração local de Git e acesso remoto."
        )


def _validate_remote_url(provider: str, remote_url: str) -> None:
    """Aceita apenas URLs HTTPS sem credenciais pertencentes ao provedor esperado."""
    parsed = urlsplit(remote_url)
    expected_host = "github.com" if provider == "github" else "bitbucket.org"
    if (
        parsed.scheme != "https"
        or parsed.hostname != expected_host
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in (None, 443)
    ):
        raise ValueError("O provedor não retornou uma URL HTTPS válida para o repositório.")


def _push_with_credential(path: Path, provider: str, remote_url: str) -> None:
    """Entrega a credencial ao Git via askpass temporário, sem expô-la nos argumentos."""
    _validate_remote_url(provider, remote_url)
    credential = get_credential(provider)
    if not credential:
        raise ValueError("Credencial do provedor não encontrada para o envio.")
    if provider == "bitbucket" and ":" in credential:
        username, password = credential.split(":", 1)
    else:
        username, password = "x-access-token", credential
    with tempfile.TemporaryDirectory(prefix="neo-git-askpass-") as temp_dir:
        script = Path(temp_dir) / "askpass"
        script.write_text(
            '#!/bin/sh\ncase "$1" in\n  *sername*) printf "%s\\n" "$NEO_PUSH_USERNAME" ;;\n'
            '  *) printf "%s\\n" "$NEO_PUSH_PASSWORD" ;;\nesac\n',
            encoding="utf-8",
        )
        script.chmod(0o700)
        env = os.environ.copy()
        env.update(
            {
                "GIT_ASKPASS": str(script),
                "GIT_TERMINAL_PROMPT": "0",
                "GIT_CONFIG_NOSYSTEM": "1",
                "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_CONFIG_COUNT": "0",
                "NEO_PUSH_USERNAME": username,
                "NEO_PUSH_PASSWORD": password,
            }
        )
        _run_git(
            path,
            "-c",
            "credential.helper=",
            "-c",
            "http.followRedirects=false",
            "push",
            "--set-upstream",
            "origin",
            "HEAD",
            env=env,
        )


__all__ = [
    "detect_git_remote_details",
    "get_git_config_value",
    "resolve_git_provider",
    "resolve_git_workspace_and_source",
    "select_repo",
]
