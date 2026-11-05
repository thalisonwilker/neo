"""Ação de repositório local."""

from __future__ import annotations

from pathlib import Path

import httpx
import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.git import local_repo as common
from neo.config import ExitCode
from neo.integrations.git.errors import GitProviderError
from neo.output import print_error, print_success


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
    if not name.strip() or name in (".", "..") or "/" in name or ("\\" in name):
        print_error("Informe um nome válido para o repositório.", as_json=as_json, code=2)
        raise typer.Exit(code=2)
    if target.exists():
        print_error(
            "O caminho de destino já existe; nada foi sobrescrito.", as_json=as_json, code=2
        )
        raise typer.Exit(code=2)
    provider, client = common.resolve_git_provider(as_json=as_json)
    workspace, _ = common.resolve_git_workspace_and_source(provider)
    stage = "criação local"
    remote_created = False
    try:
        target.mkdir()
        _, branch, _ = common.get_git_config_value("default-branch")
        common._run_git(target, "init", "--initial-branch", branch or "main")
        (target / "README.md").write_text(f"# {name.strip()}\n", encoding="utf-8")
        (target / "AGENTS.md").write_text("# AGENTS.md\n", encoding="utf-8")
        common._run_git(target, "add", "--", "README.md", "AGENTS.md")
        common._run_git(target, "commit", "-m", "Initial commit")
        common.select_repo(target)
        stage = "criação do repositório remoto"
        remote = client.create_repository(
            name.strip(), workspace=workspace, is_private=not public, description=description
        )
        remote_created = True
        remote_url = remote.https_clone_url
        if not remote_url:
            raise ValueError("O provedor não retornou URL HTTPS de clonagem.")
        common._validate_remote_url(provider, remote_url)
        stage = "configuração do origin"
        common._run_git(target, "remote", "add", "origin", remote_url)
        stage = "envio da branch inicial"
        common._push_with_credential(target, provider, remote_url)
    except (OSError, RuntimeError, ValueError, GitProviderError, httpx.HTTPError) as exc:
        state = "criado" if remote_created else "não confirmado"
        print_error(
            f"Falha na etapa: {stage}. Repositório local preservado em {target}; repositório remoto: {state}. Verifique o provedor e retome a operação manualmente.",
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
