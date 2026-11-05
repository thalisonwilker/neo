"""Ação de configuração Git."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.git import _common as common
from neo.config import (
    get_credential_source,
)
from neo.git_context import (
    get_task,
    selected_repo,
)
from neo.integrations.git.resolver import (
    detect_git_remote_details,
    resolve_git_provider_and_source,
    resolve_git_workspace_and_source,
)
from neo.output import (
    print_json,
    print_panel,
)


def git_status(
    ctx: typer.Context,
    json_output: bool = Option(
        False, "--json", help="Emite a saída em formato JSON estruturado no stdout."
    ),
) -> None:
    """Exibe o diagnóstico do repositório Git local, provedor resolvido e autenticação."""
    as_json = is_json_mode(ctx, json_output)
    local_info = common._inspect_local_git_status()
    try:
        provider, provider_source = resolve_git_provider_and_source()
    except ValueError as e:
        common._fail_usage(str(e), as_json=as_json)
    workspace, workspace_source = resolve_git_workspace_and_source(provider)
    _rem_prov, _rem_ws, detected_repo = detect_git_remote_details()
    auth_source = get_credential_source(provider)
    authenticated = auth_source is not None
    try:
        task = get_task()
        selected_path = selected_repo()
    except ValueError:
        task = None
        selected_path = None
    payload = {
        "local": local_info,
        "provider": provider,
        "provider_source": provider_source,
        "workspace": workspace,
        "workspace_source": workspace_source,
        "repo": detected_repo,
        "authenticated": authenticated,
        "auth_source": auth_source or "none",
        "task": task,
        "selected_repo": str(selected_path) if selected_path else None,
    }
    if as_json:
        print_json(payload)
    else:
        is_repo = bool(local_info["is_git_repo"])
        tree_state = (
            "working tree limpa"
            if local_info["clean"]
            else f"{local_info['modified_files']} arquivo(s) alterado(s)"
        )
        repo_line = (
            f"[green]Sim[/green] (branch: [cyan]{local_info['current_branch']}[/cyan], {tree_state})"
            if is_repo
            else "[dim]Não (diretório fora de um repositório Git)[/dim]"
        )
        auth_line = (
            f"[bold green]Autenticado[/bold green] ({auth_source})"
            if authenticated
            else "[bold red]Não autenticado[/bold red] (execute `neo git config set api-key`)"
        )
        ws_line = (
            f"[cyan]{workspace}[/cyan] ({workspace_source})"
            if workspace
            else "[dim]auto (API)[/dim]"
        )
        rem_repo_line = f"[cyan]{detected_repo}[/cyan]" if detected_repo else "[dim]-[/dim]"
        print_panel(
            "Status do Contexto Git",
            f"[bold]Repositório Local:[/bold] {repo_line}\n[bold]Remote Origin:[/bold] {local_info['remote_url'] or '-'}\n[bold]Provedor Ativo:[/bold] [cyan]{provider}[/cyan] ({provider_source})\n[bold]Workspace Ativo:[/bold] {ws_line}\n[bold]Repositório Detectado:[/bold] {rem_repo_line}\n[bold]Repositório Selecionado:[/bold] {selected_path or '-'}\n[bold]Task:[/bold] {task or '-'}\n[bold]Autenticação:[/bold] {auth_line}",
        )
