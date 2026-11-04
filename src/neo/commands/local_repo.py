"""Criação e publicação de repositórios locais e edição de descrição remota."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode, get_credential, get_git_config_value
from neo.git_context import select_repo
from neo.integrations.bitbucket import BitbucketError
from neo.integrations.resolver import (
    detect_git_remote_details,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import print_error, print_success


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


def create_repo(
    ctx: typer.Context,
    name: str = Argument(..., help="Nome do repositório remoto."),
    path: Path = Option(..., "--path", help="Caminho inexistente do novo repositório local."),  # noqa: B008
    public: bool = Option(False, "--public", help="Cria o repositório remoto público."),
    description: str | None = Option(None, "--description", help="Descrição do repositório."),
) -> None:
    """Cria e publica um repositório Git local."""
    as_json = is_json_mode(ctx)
    target = path.expanduser().absolute()
    if not name.strip() or name in (".", "..") or "/" in name or "\\" in name:
        print_error("Informe um nome válido para o repositório.", as_json=as_json, code=2)
        raise typer.Exit(code=2)
    if target.exists():
        print_error(
            "O caminho de destino já existe; nada foi sobrescrito.", as_json=as_json, code=2
        )
        raise typer.Exit(code=2)

    provider, client = resolve_git_provider(as_json=as_json)
    workspace, _ = resolve_git_workspace_and_source(provider)
    stage = "criação local"
    remote_created = False
    try:
        target.mkdir()
        _, branch, _ = get_git_config_value("default-branch")
        _run_git(target, "init", "--initial-branch", branch or "main")
        (target / "README.md").write_text(f"# {name.strip()}\n", encoding="utf-8")
        (target / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        _run_git(target, "add", "--", "README.md", "AGENTS.md")
        _run_git(target, "commit", "-m", "Initial commit")
        select_repo(target)
        stage = "criação do repositório remoto"
        remote = client.create_repository(
            name.strip(), workspace=workspace, is_private=not public, description=description
        )
        remote_created = True
        remote_url = remote.https_clone_url
        if not remote_url:
            raise ValueError("O provedor não retornou URL HTTPS de clonagem.")
        _validate_remote_url(provider, remote_url)
        stage = "configuração do origin"
        _run_git(target, "remote", "add", "origin", remote_url)
        stage = "envio da branch inicial"
        _push_with_credential(target, provider, remote_url)
    except (OSError, RuntimeError, ValueError, BitbucketError, httpx.HTTPError) as exc:
        # Não incluir erros externos, que podem conter URL ou credencial.
        state = "criado" if remote_created else "não confirmado"
        print_error(
            f"Falha na etapa: {stage}. Repositório local preservado em {target}; "
            f"repositório remoto: {state}. Verifique o provedor e retome a operação manualmente.",
            as_json=as_json,
            code=int(ExitCode.ERROR),
        )
        raise typer.Exit(code=int(ExitCode.ERROR)) from exc

    print_success(
        f"Repositório criado e publicado: {target}",
        as_json=as_json,
        json_payload={
            "status": "success",
            "path": str(target),
            "provider": provider,
            "repo": remote.slug,
        },
    )


def edit_repo(
    ctx: typer.Context,
    description: str = Option(..., "--description", help="Nova descrição no provedor Git."),
) -> None:
    """Altera a descrição do repositório selecionado no provedor."""
    as_json = is_json_mode(ctx)
    provider, workspace, repo = detect_git_remote_details()
    if not provider or not workspace or not repo:
        print_error(
            "O repositório selecionado não tem um origin GitHub ou Bitbucket reconhecido.",
            as_json=as_json,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    _, client = resolve_git_provider(provider, as_json=as_json)
    try:
        client.update_repository_description(repo, description, workspace=workspace)
    except (BitbucketError, httpx.HTTPError) as exc:
        print_error("Não foi possível atualizar a descrição no provedor.", as_json=as_json, code=1)
        raise typer.Exit(code=1) from exc
    print_success(
        f"Descrição de {workspace}/{repo} atualizada.",
        as_json=as_json,
        json_payload={
            "status": "success",
            "provider": provider,
            "repo": repo,
            "description": description,
        },
    )
