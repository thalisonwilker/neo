"""Comandos de gerenciamento e seleção de workspace Git (`neo git workspace`)."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.config import (
    ExitCode,
    get_default_workspace_config,
    set_default_workspace_config,
)
from neo.integrations.bitbucket import BitbucketError
from neo.integrations.resolver import (
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import print_error, print_json, print_panel, print_success, print_table

workspace_app = typer.Typer(
    name="workspace",
    help="Lista, seleciona e exibe o workspace ativo no GitHub ou Bitbucket Cloud (list, select, show).",
    no_args_is_help=True,
)


@workspace_app.command("list")
def workspace_list(
    ctx: typer.Context,
    provider: str | None = Option(
        None,
        "--provider",
        help="Provedor Git: 'github' ou 'bitbucket'.",
    ),
    limit: int | None = Option(
        None,
        "--limit",
        help="Quantidade máxima de workspaces a exibir.",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Lista os workspaces disponíveis para a conta autenticada."""
    as_json = is_json_mode(ctx, json_output)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)

    try:
        workspaces = client.list_workspaces()
    except BitbucketError as e:
        handle_git_provider_error(e, as_json=as_json)

    active_ws = get_default_workspace_config(provider=prov_name)
    if not active_ws and workspaces:
        active_ws = workspaces[0].slug

    if limit is not None and limit > 0:
        workspaces = workspaces[:limit]

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
            print_panel("Workspaces", f"Nenhum workspace encontrado no {prov_title}.")
            return

        columns = ["Nome", "Slug", "Admin", "Status"]
        rows: list[list[str]] = []
        for w in workspaces:
            admin_str = "[green]Sim[/green]" if w.is_admin else "Não"
            status_str = (
                "[bold green]● Ativo[/bold green]" if w.slug == active_ws else "[dim]-[/dim]"
            )
            rows.append([w.name, w.slug, admin_str, status_str])

        print_table(f"Workspaces no {prov_title}", columns, rows)


@workspace_app.command("select")
def workspace_select(
    ctx: typer.Context,
    workspace: str | None = Option(
        None,
        "--workspace",
        help="Slug do workspace a ser definido como ativo.",
    ),
    provider: str | None = Option(
        None,
        "--provider",
        help="Provedor Git: 'github' ou 'bitbucket'.",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Seleciona o workspace ativo de forma interativa ou via --workspace."""
    as_json = is_json_mode(ctx, json_output)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)

    prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
    try:
        workspaces = client.list_workspaces()
    except BitbucketError as e:
        handle_git_provider_error(e, as_json=as_json)

    if not workspaces:
        print_error(
            f"Nenhum workspace disponível no {prov_title} para seleção.",
            as_json=as_json,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    target_slug: str
    if workspace:
        target_slug = workspace.strip()
    else:
        if as_json:
            print_error(
                "A opção `--workspace <slug>` é obrigatória quando o modo `--json` está ativo.",
                as_json=True,
                code=int(ExitCode.USAGE_ERROR),
            )
            raise typer.Exit(code=int(ExitCode.USAGE_ERROR))

        typer.echo(f"\nWorkspaces disponíveis no {prov_title}:")
        for idx, w in enumerate(workspaces, start=1):
            admin_tag = " (Admin)" if w.is_admin else ""
            typer.echo(f"  [{idx}] {w.name} ({w.slug}){admin_tag}")

        choice = typer.prompt(
            "\nEscolha o número da opção desejada",
            type=int,
            default=1,
        )
        if choice < 1 or choice > len(workspaces):
            print_error(
                "Opção inválida selecionada.",
                as_json=as_json,
                code=int(ExitCode.USAGE_ERROR),
            )
            raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
        target_slug = workspaces[choice - 1].slug

    found = next((w for w in workspaces if w.slug == target_slug), None)
    if not found:
        valid_slugs = ", ".join(w.slug for w in workspaces)
        print_error(
            f"Workspace '{target_slug}' não encontrado no {prov_title}. Opções disponíveis: {valid_slugs}",
            as_json=as_json,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

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


@workspace_app.command("show")
def workspace_show(
    ctx: typer.Context,
    workspace: str | None = Option(
        None,
        "--workspace",
        help="Slug do workspace para inspecionar (usa o workspace ativo se omitido).",
    ),
    provider: str | None = Option(
        None,
        "--provider",
        help="Provedor Git: 'github' ou 'bitbucket'.",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Exibe os detalhes do workspace ativo ou especificado."""
    as_json = is_json_mode(ctx, json_output)
    prov_name, client = resolve_git_provider(provider, as_json=as_json)
    prov_title = "GitHub" if prov_name == "github" else "Bitbucket"

    resolved_ws, source = resolve_git_workspace_and_source(prov_name, workspace)
    try:
        workspaces = client.list_workspaces()
    except BitbucketError as e:
        handle_git_provider_error(e, as_json=as_json)

    if not resolved_ws:
        if not workspaces:
            print_error(
                f"Nenhum workspace encontrado para a conta autenticada no {prov_title}.",
                as_json=as_json,
                code=int(ExitCode.NOT_FOUND),
            )
            raise typer.Exit(code=int(ExitCode.NOT_FOUND))
        resolved_ws = workspaces[0].slug
        source = "default"

    found = next((w for w in workspaces if w.slug == resolved_ws), None)
    if workspace and not found:
        print_error(
            f"Workspace '{resolved_ws}' não encontrado no {prov_title}.",
            as_json=as_json,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    ws_name = found.name if found else resolved_ws
    ws_uuid = found.uuid if found else ""
    is_admin = found.is_admin if found else False

    source_labels = {
        "cli": "Opção de linha de comando (--workspace)",
        "env": "Variável de ambiente (NEO_GIT_WORKSPACE)",
        "config": "Configuração local (~/.config/neo/config.toml)",
        "remote": "Auto-detectado pelo remote origin local",
        "default": f"Detectado automaticamente via API do {prov_title}",
    }
    source_label = source_labels.get(source, source)

    if as_json:
        print_json(
            {
                "workspace": resolved_ws,
                "name": ws_name,
                "uuid": ws_uuid,
                "is_admin": is_admin,
                "provider": prov_name,
                "source": source,
            }
        )
    else:
        admin_label = "Sim" if is_admin else "Não"
        print_panel(
            f"Workspace Ativo ({prov_title})",
            f"[bold]Nome:[/bold] {ws_name}\n"
            f"[bold]Slug:[/bold] [cyan]{resolved_ws}[/cyan]\n"
            f"[bold]Admin:[/bold] {admin_label}\n"
            f"[bold]Origem:[/bold] {source_label}",
        )


# Bloqueios orientativos para comandos legados removidos
@workspace_app.command(
    "current",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def _legacy_workspace_current(ctx: typer.Context) -> None:
    as_json = is_json_mode(ctx)
    print_error(
        "O comando `neo git workspace current` foi removido. Use `neo git workspace show`.",
        as_json=as_json,
        code=int(ExitCode.USAGE_ERROR),
    )
    raise typer.Exit(code=int(ExitCode.USAGE_ERROR))


@workspace_app.command(
    "set",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def _legacy_workspace_set(ctx: typer.Context) -> None:
    as_json = is_json_mode(ctx)
    print_error(
        "O comando `neo git workspace set` foi removido. "
        "Use `neo git config set workspace <slug>` ou `neo git workspace select --workspace <slug>`.",
        as_json=as_json,
        code=int(ExitCode.USAGE_ERROR),
    )
    raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
