"""Seleção e validação do workspace Git."""

import httpx
import typer

from neo.commands.git._common import _configured_provider, _fail_usage
from neo.config import ExitCode, set_git_config_value
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import handle_git_provider_error, resolve_git_provider
from neo.output import console, print_error, print_success


def _set_workspace(value: str | None, as_json: bool) -> None:
    """Configura o workspace validando na API do provedor ou selecionando interativamente."""
    provider = _configured_provider(as_json)
    _prov_name, client = resolve_git_provider(provider, as_json=as_json)

    try:
        workspaces = client.list_workspaces()
    except GitProviderError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except (httpx.HTTPError, OSError) as exc:
        print_error(
            f"Erro ao consultar workspaces no provedor: {exc}",
            as_json=as_json,
            code=int(ExitCode.ERROR),
        )
        raise typer.Exit(code=int(ExitCode.ERROR)) from exc

    if not workspaces:
        print_error(
            "Nenhum workspace encontrado para a conta autenticada.",
            as_json=as_json,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    if value is not None and value.strip():
        target_val = value.strip().lower()
        matched = next(
            (w for w in workspaces if w.slug.lower() == target_val or w.name.lower() == target_val),
            None,
        )
        if not matched:
            print_error(
                f"Workspace '{value}' não encontrado na conta autenticada.",
                as_json=as_json,
                code=int(ExitCode.NOT_FOUND),
            )
            raise typer.Exit(code=int(ExitCode.NOT_FOUND))
        selected_slug = matched.slug
    else:
        if as_json:
            _fail_usage(
                "`config set workspace` sem argumento requer entrada interativa.",
                as_json=True,
            )

        console.print("\n[bold cyan]Workspaces disponíveis:[/bold cyan]")
        for i, w in enumerate(workspaces, 1):
            display_name = f" ({w.name})" if w.name and w.name != w.slug else ""
            console.print(f"  [bold cyan]{i}.[/bold cyan] [bold]{w.slug}[/bold]{display_name}")

        try:
            chosen_idx = typer.prompt("\nNúmero do workspace", type=int)
        except typer.Abort:
            raise typer.Exit(code=int(ExitCode.ERROR))

        if chosen_idx < 1 or chosen_idx > len(workspaces):
            _fail_usage(
                f"Seleção inválida. Escolha um número entre 1 e {len(workspaces)}.",
                as_json=False,
            )
        selected_slug = workspaces[chosen_idx - 1].slug

    try:
        valid_key, clean_val = set_git_config_value("workspace", selected_slug)
    except ValueError as e:
        _fail_usage(str(e), as_json=as_json)

    print_success(
        f"Configuração Git atualizada: [bold]{valid_key}[/bold] = [cyan]{clean_val}[/cyan]",
        as_json=as_json,
        json_payload={"status": "success", "key": valid_key, "value": clean_val},
    )
