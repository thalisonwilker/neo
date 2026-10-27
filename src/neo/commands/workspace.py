"""Comandos de gerenciamento e seleção de workspace no Bitbucket (`neo workspace`)."""

from __future__ import annotations

import typer
from typer import Argument, Option

from neo.config import (
    get_credential,
    get_default_workspace_config,
    set_default_workspace_config,
)
from neo.integrations.bitbucket import (
    BitbucketClient,
    BitbucketError,
)
from neo.output import print_error, print_json, print_panel, print_success, print_table

workspace_app = typer.Typer(
    name="workspace",
    help="Gerenciamento e seleção do workspace ativo do Bitbucket.",
    no_args_is_help=True,
)


def _get_bitbucket_client(as_json: bool) -> BitbucketClient:
    token = get_credential("bitbucket")
    if not token:
        msg = "Credenciais do Bitbucket não configuradas. Execute `neo config auth set bitbucket`."
        print_error(msg, as_json=as_json, code=1)
        raise typer.Exit(code=1)
    return BitbucketClient(token=token)


@workspace_app.command("list")
def workspace_list(ctx: typer.Context) -> None:
    """Lista todos os workspaces do Bitbucket acessíveis à conta autenticada."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_bitbucket_client(as_json)

    try:
        workspaces = client.list_workspaces()
    except BitbucketError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    active_ws = get_default_workspace_config()
    # Se não houver workspace configurado, o primeiro da lista é o fallback ativo
    if not active_ws and workspaces:
        active_ws = workspaces[0].slug

    if as_json:
        payload = [
            {
                "name": w.name,
                "slug": w.slug,
                "uuid": w.uuid,
                "is_admin": w.is_admin,
                "is_active": w.slug == active_ws,
            }
            for w in workspaces
        ]
        print_json(payload)
    else:
        if not workspaces:
            print_panel("Workspaces", "Nenhum workspace encontrado para a conta.")
            return

        columns = ["Nome", "Slug", "Admin", "Status"]
        rows: list[list[str]] = []
        for w in workspaces:
            admin_str = "[green]Sim[/green]" if w.is_admin else "Não"
            status_str = (
                "[bold green]● Ativo[/bold green]" if w.slug == active_ws else "[dim]-[/dim]"
            )
            rows.append([w.name, w.slug, admin_str, status_str])

        print_table("Workspaces no Bitbucket", columns, rows)


@workspace_app.command("current")
def workspace_current(ctx: typer.Context) -> None:
    """Exibe o workspace atualmente selecionado como padrão."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_bitbucket_client(as_json)

    cfg_ws = get_default_workspace_config()
    source: str
    workspace_slug: str

    if cfg_ws:
        workspace_slug = cfg_ws
        source = "config"
        source_label = "Configuração local (~/.config/neo/config.toml)"
    else:
        try:
            workspace_slug = client.get_default_workspace(ignore_config=True)
            source = "api_auto"
            source_label = "Detectado automaticamente via API do Bitbucket"
        except BitbucketError as e:
            print_error(str(e), as_json=as_json, code=1)
            raise typer.Exit(code=1) from e

    if as_json:
        print_json({"workspace": workspace_slug, "source": source})
    else:
        print_panel(
            "Workspace Ativo",
            f"[bold]Slug:[/bold] [cyan]{workspace_slug}[/cyan]\n"
            f"[bold]Origem:[/bold] {source_label}",
        )


@workspace_app.command("select")
def workspace_select(
    ctx: typer.Context,
    slug: str | None = Option(None, "--slug", "-s", help="Slug do workspace a ser ativado."),
) -> None:
    """Seleciona o workspace ativo de forma interativa ou diretamente via --slug."""
    as_json = getattr(ctx.obj, "json_mode", False) if ctx.obj else False
    client = _get_bitbucket_client(as_json)

    try:
        workspaces = client.list_workspaces()
    except BitbucketError as e:
        print_error(str(e), as_json=as_json, code=1)
        raise typer.Exit(code=1) from e

    if not workspaces:
        print_error("Nenhum workspace disponível para seleção.", as_json=as_json, code=1)
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

        typer.echo("\nWorkspaces disponíveis:")
        for idx, w in enumerate(workspaces, start=1):
            admin_tag = " (Admin)" if w.is_admin else ""
            typer.echo(f"  [{idx}] {w.name} ({w.slug}){admin_tag}")

        choice = typer.prompt(
            "\nEscolha o número do workspace",
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
            f"Workspace '{target_slug}' não encontrado. Opções disponíveis: {valid_slugs}",
            as_json=as_json,
            code=1,
        )
        raise typer.Exit(code=1)

    set_default_workspace_config(found.slug)
    print_success(
        f"Workspace ativo definido com sucesso: [cyan]{found.slug}[/cyan] ({found.name})",
        as_json=as_json,
        json_payload={"status": "success", "workspace": found.slug, "name": found.name},
    )


@workspace_app.command("set")
def workspace_set(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug do workspace a ser configurado como padrão."),
) -> None:
    """Atalho para definir diretamente o workspace padrão por slug."""
    workspace_select(ctx, slug=slug)
