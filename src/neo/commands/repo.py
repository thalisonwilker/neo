"""Comandos de gerenciamento de repositórios no Bitbucket (`neo repo`)."""

from __future__ import annotations

import subprocess

import typer
from typer import Argument, Option

from neo.config import get_credential
from neo.integrations.bitbucket import (
    BitbucketClient,
    BitbucketError,
    BitbucketNotFoundError,
)
from neo.output import print_error, print_json, print_panel, print_success, print_table

repo_app = typer.Typer(
    name="repo",
    help="Gerenciamento e busca de repositórios no Bitbucket.",
    no_args_is_help=True,
)


def _get_bitbucket_client(as_json: bool) -> BitbucketClient:
    token = get_credential("bitbucket")
    if not token:
        msg = "Credenciais do Bitbucket não configuradas. Execute `neo config auth set bitbucket`."
        print_error(msg, as_json=as_json, code=1)
        raise typer.Exit(code=1)
    return BitbucketClient(token=token)


@repo_app.command("list")
def repo_list(
    ctx: typer.Context,
    workspace: str | None = Option(None, "--workspace", "-w", help="Workspace do Bitbucket."),
) -> None:
    """Lista todos os repositórios disponíveis no workspace."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_bitbucket_client(as_json)

    try:
        repos = client.list_repositories(workspace=workspace)
    except BitbucketError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json([r.model_dump() for r in repos])
    else:
        if not repos:
            print_panel("Repositórios", "Nenhum repositório encontrado no workspace informado.")
            return

        columns = ["Nome", "Slug", "Visibilidade", "Branch Padrão", "Atualizado em"]
        rows: list[list[str]] = []
        for r in repos:
            vis = "[red]Privado[/red]" if r.is_private else "[green]Público[/green]"
            updated = r.updated_on.split("T")[0] if "T" in r.updated_on else r.updated_on
            rows.append([r.name, r.slug, vis, r.main_branch, updated])

        print_table("Repositórios no Bitbucket", columns, rows)


@repo_app.command("search")
def repo_search(
    ctx: typer.Context,
    query: str = Argument(..., help="Termo de pesquisa (nome, slug ou descrição)."),
    workspace: str | None = Option(None, "--workspace", "-w", help="Workspace do Bitbucket."),
) -> None:
    """Pesquisa repositórios por nome, slug ou descrição."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_bitbucket_client(as_json)

    try:
        repos = client.search_repositories(query=query, workspace=workspace)
    except BitbucketError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if as_json:
        print_json([r.model_dump() for r in repos])
    else:
        if not repos:
            print_panel(
                f"Busca: '{query}'", "Nenhum repositório encontrado para o termo pesquisado."
            )
            return

        columns = ["Nome", "Slug", "Visibilidade", "Descrição"]
        rows: list[list[str]] = []
        for r in repos:
            vis = "[red]Privado[/red]" if r.is_private else "[green]Público[/green]"
            desc = r.description or "-"
            rows.append([r.name, r.slug, vis, desc])

        print_table(f"Repositórios encontrados para '{query}'", columns, rows)


@repo_app.command("clone")
def repo_clone(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug ou nome do repositório a clonar."),
    workspace: str | None = Option(None, "--workspace", "-w", help="Workspace do Bitbucket."),
    use_ssh: bool = Option(False, "--ssh", help="Força clonagem via protocolo SSH."),
    use_https: bool = Option(False, "--https", help="Força clonagem via protocolo HTTPS."),
) -> None:
    """Clona um repositório do Bitbucket para o diretório atual."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_bitbucket_client(as_json)

    try:
        repo = client.get_repository(repo_slug=slug, workspace=workspace)
    except BitbucketNotFoundError as e:
        print_error(f"Repositório '{slug}' não encontrado: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
    except BitbucketError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    # Resolução de URL
    clone_url: str | None = None
    if use_ssh:
        clone_url = repo.ssh_clone_url
    elif use_https:
        clone_url = repo.https_clone_url
    else:
        clone_url = repo.ssh_clone_url or repo.https_clone_url

    if not clone_url:
        print_error(
            f"Não foi possível obter uma URL de clone válida para o repositório '{slug}'.",
            as_json=as_json,
            code=1,
        )
        raise typer.Exit(code=1)

    if as_json:
        print_json(
            {
                "status": "cloning",
                "repo": repo.slug,
                "clone_url": clone_url,
            }
        )
    else:
        print_success(
            f"Iniciando clone de [bold]{repo.name}[/bold] via [cyan]{clone_url}[/cyan]..."
        )

    proc = subprocess.run(["git", "clone", clone_url], check=False)
    if proc.returncode != 0:
        print_error(
            f"Falha ao executar git clone (código {proc.returncode}).",
            as_json=as_json,
            code=proc.returncode,
        )
        raise typer.Exit(code=proc.returncode)

    print_success(f"Repositório '{repo.slug}' clonado com sucesso!", as_json=as_json)


@repo_app.command("create")
def repo_create(
    ctx: typer.Context,
    name: str = Argument(..., help="Nome do repositório a ser criado."),
    workspace: str | None = Option(None, "--workspace", "-w", help="Workspace do Bitbucket."),
    is_private: bool = Option(
        True, "--private/--public", help="Define se o repositório é privado ou público."
    ),
    description: str | None = Option(None, "--description", "-d", help="Descrição do repositório."),
    yes: bool = Option(False, "--yes", "-y", help="Pula confirmação interativa."),
) -> None:
    """Cria um novo repositório no Bitbucket Cloud."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_bitbucket_client(as_json)

    if not yes and not as_json:
        confirmed = typer.confirm(f"Deseja criar o repositório '{name}' no Bitbucket?")
        if not confirmed:
            print_error("Operação cancelada pelo usuário.", as_json=as_json, code=1)
            raise typer.Exit(code=1)

    try:
        repo = client.create_repository(
            name=name,
            workspace=workspace,
            is_private=is_private,
            description=description,
        )
        print_success(
            f"Repositório '{repo.name}' criado com sucesso no workspace '{repo.workspace}'!",
            as_json=as_json,
            json_payload=repo.model_dump(),
        )
    except BitbucketError as e:
        print_error(f"Falha ao criar repositório: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
