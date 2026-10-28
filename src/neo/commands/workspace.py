"""Comandos de gerenciamento e seleção de workspace/organização Git (Bitbucket e GitHub) (`neo git workspace`)."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.config import (
    get_default_workspace_config,
    set_default_workspace_config,
)
from neo.integrations.bitbucket import BitbucketError
from neo.integrations.resolver import resolve_git_provider
from neo.output import print_error, print_json, print_panel, print_success, print_table

workspace_app = typer.Typer(
    name="workspace",
    help="Gerenciamento e seleção do workspace/organização ativo do Bitbucket ou GitHub.",
    no_args_is_help=True,
)


@workspace_app.command("list")
def workspace_list(
    ctx: typer.Context,
    provider: str | None = Option(
        None, "--provider", "-p", help="Provedor Git: 'bitbucket' ou 'github'."
    ),
) -> None:
    """Lista todos os workspaces ou organizações acessíveis à conta autenticada."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    prov_name, client = resolve_git_provider(provider, as_json=as_json)

    try:
        workspaces = client.list_workspaces()
    except BitbucketError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    active_ws = get_default_workspace_config(provider=prov_name)
    # Se não houver workspace configurado, o primeiro da lista é o fallback ativo
    if not active_ws and workspaces:
        active_ws = workspaces[0].slug

    prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
    if as_json:
        payload = [
            {
                "name": w.name,
                "slug": w.slug,
                "uuid": w.uuid,
                "is_admin": w.is_admin,
                "is_active": w.slug == active_ws,
                "provider": prov_name,
            }
            for w in workspaces
        ]
        print_json(payload)
    else:
        if not workspaces:
            print_panel("Workspaces", f"Nenhum workspace/organização encontrado no {prov_title}.")
            return

        columns = ["Nome", "Slug", "Admin", "Status"]
        rows: list[list[str]] = []
        for w in workspaces:
            admin_str = "[green]Sim[/green]" if w.is_admin else "Não"
            status_str = (
                "[bold green]● Ativo[/bold green]" if w.slug == active_ws else "[dim]-[/dim]"
            )
            rows.append([w.name, w.slug, admin_str, status_str])

        print_table(f"Workspaces / Organizações no {prov_title}", columns, rows)


@workspace_app.command("current")
def workspace_current(
    ctx: typer.Context,
    provider: str | None = Option(
        None, "--provider", "-p", help="Provedor Git: 'bitbucket' ou 'github'."
    ),
) -> None:
    """Exibe o workspace ou organização atualmente selecionado como padrão."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    prov_name, client = resolve_git_provider(provider, as_json=as_json)

    prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
    cfg_ws = get_default_workspace_config(provider=prov_name)
    source: str
    workspace_slug: str

    if cfg_ws:
        workspace_slug = cfg_ws
        source = "config"
        source_label = f"Configuração local (~/.config/neo/config.toml) [{prov_name}]"
    else:
        try:
            workspace_slug = client.get_default_workspace(ignore_config=True)
            source = "api_auto"
            source_label = f"Detectado automaticamente via API do {prov_title}"
        except BitbucketError as e:
            print_error(str(e), as_json=as_json, code=1)
            raise typer.Exit(code=1) from e

    if as_json:
        print_json({"workspace": workspace_slug, "provider": prov_name, "source": source})
    else:
        print_panel(
            f"Workspace / Organização Ativo ({prov_title})",
            f"[bold]Slug:[/bold] [cyan]{workspace_slug}[/cyan]\n"
            f"[bold]Origem:[/bold] {source_label}",
        )


@workspace_app.command("select")
def workspace_select(
    ctx: typer.Context,
    slug: str | None = Option(
        None, "--slug", "-s", help="Slug do workspace ou organização a ser ativado."
    ),
    provider: str | None = Option(
        None, "--provider", "-p", help="Provedor Git: 'bitbucket' ou 'github'."
    ),
) -> None:
    """Seleciona o workspace/organização ativo de forma interativa ou diretamente via --slug."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    prov_name, client = resolve_git_provider(provider, as_json=as_json)

    prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
    try:
        workspaces = client.list_workspaces()
    except BitbucketError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if not workspaces:
        print_error(
            f"Nenhum workspace/organização disponível no {prov_title} para seleção.",
            as_json=as_json,
            code=1,
        )
        raise typer.Exit(code=1)

    target_slug: str
    if slug:
        target_slug = slug.strip()
    else:
        if as_json:
            print_error(
                "A flag `--slug <nome>` é obrigatória quando o modo --json está ativo.",
                as_json=True,
                code=1,
            )
            raise typer.Exit(code=1)

        typer.echo(f"\nWorkspaces / Organizações disponíveis no {prov_title}:")
        for idx, w in enumerate(workspaces, start=1):
            admin_tag = " (Admin)" if w.is_admin else ""
            typer.echo(f"  [{idx}] {w.name} ({w.slug}){admin_tag}")

        choice = typer.prompt(
            "\nEscolha o número da opção desejada",
            type=int,
            default=1,
        )
        if choice < 1 or choice > len(workspaces):
            print_error("Opção inválida selecionada.", as_json=as_json, code=1)
            raise typer.Exit(code=1)
        target_slug = workspaces[choice - 1].slug

    # Valida se o slug existe na lista de workspaces
    found = next((w for w in workspaces if w.slug == target_slug), None)
    if not found:
        valid_slugs = ", ".join(w.slug for w in workspaces)
        print_error(
            f"Workspace '{target_slug}' não encontrado no {prov_title}. Opções disponíveis: {valid_slugs}",
            as_json=as_json,
            code=1,
        )
        raise typer.Exit(code=1)

    set_default_workspace_config(found.slug, provider=prov_name)
    print_success(
        f"Workspace ativo no {prov_title} definido com sucesso: [cyan]{found.slug}[/cyan] ({found.name})",
        as_json=as_json,
        json_payload={
            "status": "success",
            "provider": prov_name,
            "workspace": found.slug,
            "name": found.name,
        },
    )


@workspace_app.command("set")
def workspace_set(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug do workspace ou organização a ser configurado."),
    provider: str | None = Option(
        None, "--provider", "-p", help="Provedor Git: 'bitbucket' ou 'github'."
    ),
) -> None:
    """Atalho para definir diretamente o workspace padrão por slug."""
    workspace_select(ctx, slug=slug, provider=provider)
