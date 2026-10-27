"""Comandos de gerenciamento de repositórios Git (Bitbucket e GitHub) (`neo repo`)."""

from __future__ import annotations

import subprocess

import typer
from typer import Argument, Option

from neo.integrations.bitbucket import (
    BitbucketError,
    BitbucketNotFoundError,
)
from neo.integrations.resolver import resolve_git_provider
from neo.output import print_error, print_json, print_panel, print_success, print_table

repo_app = typer.Typer(
    name="repo",
    help="Gerenciamento e busca de repositórios no Bitbucket e GitHub.",
    no_args_is_help=True,
)


@repo_app.command("list")
def repo_list(
    ctx: typer.Context,
    workspace: str | None = Option(
        None, "--workspace", "-w", help="Workspace ou organização/usuário de destino."
    ),
    provider: str | None = Option(
        None, "--provider", "-p", help="Provedor Git: 'bitbucket' ou 'github'."
    ),
) -> None:
    """Lista todos os repositórios disponíveis no workspace ou organização."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    prov_name, client = resolve_git_provider(provider, as_json=as_json)

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

        prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
        print_table(f"Repositórios no {prov_title}", columns, rows)


@repo_app.command("search")
def repo_search(
    ctx: typer.Context,
    query: str = Argument(..., help="Termo de pesquisa (nome, slug ou descrição)."),
    workspace: str | None = Option(
        None, "--workspace", "-w", help="Workspace ou organização/usuário de destino."
    ),
    provider: str | None = Option(
        None, "--provider", "-p", help="Provedor Git: 'bitbucket' ou 'github'."
    ),
) -> None:
    """Pesquisa repositórios por nome, slug ou descrição."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    prov_name, client = resolve_git_provider(provider, as_json=as_json)

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

        prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
        print_table(f"Repositórios no {prov_title} encontrados para '{query}'", columns, rows)


@repo_app.command("clone")
def repo_clone(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug ou nome do repositório a clonar."),
    workspace: str | None = Option(
        None, "--workspace", "-w", help="Workspace ou organização/usuário de destino."
    ),
    provider: str | None = Option(
        None, "--provider", "-p", help="Provedor Git: 'bitbucket' ou 'github'."
    ),
    use_ssh: bool = Option(False, "--ssh", help="Força clonagem via protocolo SSH."),
    use_https: bool = Option(False, "--https", help="Força clonagem via protocolo HTTPS."),
) -> None:
    """Clona um repositório para o diretório atual."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    prov_name, client = resolve_git_provider(provider, as_json=as_json)

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

    prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
    if as_json:
        print_json(
            {
                "status": "cloning",
                "provider": prov_name,
                "repo": repo.slug,
                "clone_url": clone_url,
            }
        )
    else:
        print_success(
            f"Iniciando clone de [bold]{repo.name}[/bold] ({prov_title}) via [cyan]{clone_url}[/cyan]..."
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
    workspace: str | None = Option(
        None, "--workspace", "-w", help="Workspace ou organização/usuário de destino."
    ),
    provider: str | None = Option(
        None, "--provider", "-p", help="Provedor Git: 'bitbucket' ou 'github'."
    ),
    is_private: bool = Option(
        True, "--private/--public", help="Define se o repositório é privado ou público."
    ),
    description: str | None = Option(None, "--description", "-d", help="Descrição do repositório."),
    yes: bool = Option(False, "--yes", "-y", help="Pula confirmação interativa."),
) -> None:
    """Cria um novo repositório no provedor Git (Bitbucket ou GitHub)."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    prov_name, client = resolve_git_provider(provider, as_json=as_json)

    prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
    if not yes and not as_json:
        confirmed = typer.confirm(f"Deseja criar o repositório '{name}' no {prov_title}?")
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
            f"Repositório '{repo.name}' criado com sucesso no {prov_title} ({repo.workspace})!",
            as_json=as_json,
            json_payload=repo.model_dump(),
        )
    except BitbucketError as e:
        print_error(f"Falha ao criar repositório: {e}", as_json=as_json, code=1)
        raise typer.Exit(code=1) from e
