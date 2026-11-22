"""Seleção e validação do workspace Git."""

from typing import cast

import httpx
import typer

from neo.commands.git._common import _configured_provider, _fail_usage
from neo.config import ExitCode, set_bitbucket_workspace_project, set_git_config_value
from neo.integrations.git.api.bitbucket.client import BitbucketClient
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import handle_git_provider_error, resolve_git_provider
from neo.output import console, print_error, print_success


def _set_workspace(value: str | None, as_json: bool) -> None:
    """Configura o workspace validando na API do provedor ou selecionando interativamente."""
    provider = _configured_provider(as_json)
    if provider == "bitbucket" and as_json:
        _fail_usage(
            "A seleção de projeto Bitbucket requer modo interativo, sem --json.", as_json=True
        )
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

    if provider == "bitbucket":
        try:
            projects = cast(BitbucketClient, client).list_projects(selected_slug)
        except GitProviderError as exc:
            handle_git_provider_error(exc, as_json=as_json)
        except (httpx.HTTPError, OSError) as exc:
            print_error("Erro ao consultar projetos no Bitbucket.", as_json=as_json, code=1)
            raise typer.Exit(code=1) from exc
        if not projects:
            print_error("Nenhum projeto acessível no workspace selecionado.", as_json=False, code=4)
            raise typer.Exit(code=4)
        console.print("\n[bold cyan]Projetos disponíveis:[/bold cyan]")
        for i, project in enumerate(projects, 1):
            from rich.text import Text

            console.print(Text(f"  {i}. {project.name} ({project.key})"))
        try:
            project_idx = typer.prompt("\nNúmero do projeto", type=int)
        except typer.Abort:
            raise typer.Exit(code=int(ExitCode.ERROR)) from None
        if project_idx < 1 or project_idx > len(projects):
            _fail_usage(f"Seleção inválida. Escolha um número entre 1 e {len(projects)}.", False)
        try:
            set_bitbucket_workspace_project(selected_slug, projects[project_idx - 1].key)
        except (OSError, ValueError) as exc:
            print_error("Não foi possível salvar workspace e projeto.", as_json=False, code=1)
            raise typer.Exit(code=1) from exc
        print_success(
            f"Configuração Git atualizada: workspace = {selected_slug}; projeto = {projects[project_idx - 1].key}"
        )
        return

    try:
        valid_key, clean_val = set_git_config_value("workspace", selected_slug)
    except ValueError as e:
        _fail_usage(str(e), as_json=as_json)

    print_success(
        f"Configuração Git atualizada: [bold]{valid_key}[/bold] = [cyan]{clean_val}[/cyan]",
        as_json=as_json,
        json_payload={"status": "success", "key": valid_key, "value": clean_val},
    )
