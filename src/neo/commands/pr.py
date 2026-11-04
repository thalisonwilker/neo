"""Comandos de pull request para GitHub e Bitbucket Cloud."""

from __future__ import annotations

from typing import NoReturn

import httpx
import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.branch import current_branch
from neo.commands.commits import _resolve_target_repo
from neo.config import ExitCode
from neo.integrations.bitbucket import BitbucketError
from neo.integrations.pr_models import PullRequest
from neo.integrations.resolver import (
    GitProviderProtocol,
    handle_git_provider_error,
    resolve_git_provider,
    resolve_git_workspace_and_source,
)
from neo.output import console, print_error, print_json, print_success, print_table

pr_app = typer.Typer(
    name="pr",
    help="Lista, abre, aprova, recusa e pesquisa pull requests.",
    invoke_without_command=True,
)


def _fail(message: str, as_json: bool, code: ExitCode = ExitCode.USAGE_ERROR) -> NoReturn:
    print_error(message, as_json=as_json, code=int(code))
    raise typer.Exit(code=int(code))


def _context(
    provider: str | None, workspace: str | None, repo: str | None, as_json: bool
) -> tuple[str, str | None, GitProviderProtocol]:
    target = _resolve_target_repo(repo, as_json)
    provider_name, client = resolve_git_provider(provider, as_json=as_json)
    resolved_workspace, _ = resolve_git_workspace_and_source(provider_name, workspace)
    return target, resolved_workspace, client


def _network_error(exc: httpx.HTTPError, as_json: bool) -> NoReturn:
    print_error(
        "Falha de rede ao consultar o provedor Git.", as_json=as_json, code=int(ExitCode.ERROR)
    )
    raise typer.Exit(code=int(ExitCode.ERROR)) from exc


def _render_results(results: list[PullRequest], as_json: bool) -> None:
    if as_json:
        print_json([result.model_dump() for result in results])
    elif not results:
        print_success("Nenhum pull request encontrado.", as_json=False)
    else:
        print_table(
            "Pull requests",
            ["ID", "Título", "Estado", "Origem", "Destino", "URL"],
            [[str(r.id), r.title, r.state, r.source, r.destination, r.url] for r in results],
        )


@pr_app.callback()
def pr_list_open(
    ctx: typer.Context,
    repo: str | None = Option(None, "--repo", help="Slug do repositório."),
    workspace: str | None = Option(None, "--workspace", help="Workspace do repositório."),
    provider: str | None = Option(None, "--provider", help="Provedor Git."),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Lista os pull requests abertos quando nenhum subcomando é informado."""
    if ctx.invoked_subcommand is not None:
        return
    as_json = is_json_mode(ctx, json_output)
    target, ws, client = _context(provider, workspace, repo, as_json)
    try:
        results = client.list_open_pull_requests(target, workspace=ws)
    except BitbucketError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        _network_error(exc, as_json)
    _render_results(results, as_json)


@pr_app.command("open")
def pr_open(
    ctx: typer.Context,
    base: str | None = Option(None, "--base", help="Branch remota de destino."),
    title: str | None = Option(None, "--title", help="Título do pull request."),
    description: str | None = Option(None, "--description", help="Descrição do pull request."),
    repo: str | None = Option(None, "--repo", help="Slug do repositório."),
    workspace: str | None = Option(None, "--workspace", help="Workspace do repositório."),
    provider: str | None = Option(None, "--provider", help="Provedor Git."),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Abre pull request usando a branch local atual como origem."""
    as_json = is_json_mode(ctx, json_output)
    try:
        source = current_branch()
    except ValueError as exc:
        _fail(str(exc), as_json, ExitCode.NOT_FOUND)
    if not source:
        _fail("Nenhuma branch ativa. Selecione uma branch antes de abrir o pull request.", as_json)
    if as_json and (base is None or title is None or description is None):
        _fail("Em modo JSON informe --base, --title e --description.", True)
    target, ws, client = _context(provider, workspace, repo, as_json)
    try:
        branches = client.list_pr_branches(target, workspace=ws)
        if source not in branches:
            _fail(
                f"A branch '{source}' não existe no provedor. Publique a branch antes de abrir o PR.",
                as_json,
                ExitCode.NOT_FOUND,
            )
        if base is None:
            choices = [name for name in branches if name != source]
            if not choices:
                _fail("Nenhuma branch remota de destino disponível.", as_json, ExitCode.NOT_FOUND)
            for i, name in enumerate(choices, 1):
                console.print(f"{i}. {name}")
            selected = typer.prompt("Número da branch de destino", type=int)
            if selected < 1 or selected > len(choices):
                _fail("Seleção de branch inválida.", as_json)
            base = choices[selected - 1]
        if base not in branches or base == source:
            _fail(
                "A branch de destino deve existir no provedor e ser diferente da origem.", as_json
            )
        if title is None:
            title = typer.prompt("Título")
        if not title.strip():
            _fail("O título não pode ser vazio.", as_json)
        if description is None:
            description = typer.prompt("Descrição", default="", show_default=False)
        result = client.create_pull_request(
            target, source, base, title.strip(), description, workspace=ws
        )
    except BitbucketError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        _network_error(exc, as_json)
    if as_json:
        print_json(result.model_dump())
    else:
        print_success(f"Pull request #{result.id} criado: {result.url}", as_json=False)


@pr_app.command("approve")
def pr_approve(
    ctx: typer.Context,
    pr_id: int = Argument(..., help="ID do pull request."),
    message: str | None = Option(None, "--message", help="Mensagem de aprovação."),
    repo: str | None = Option(None, "--repo"),
    workspace: str | None = Option(None, "--workspace"),
    provider: str | None = Option(None, "--provider"),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Aprova um pull request com mensagem."""
    as_json = is_json_mode(ctx, json_output)
    if pr_id < 1:
        _fail("O ID deve ser positivo.", as_json)
    if message is None:
        if as_json:
            _fail("Em modo JSON informe --message.", True)
        message = typer.prompt("Mensagem de aprovação")
    if not message.strip():
        _fail("A mensagem não pode ser vazia.", as_json)
    target, ws, client = _context(provider, workspace, repo, as_json)
    try:
        client.approve_pull_request(target, pr_id, message.strip(), workspace=ws)
    except BitbucketError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        _network_error(exc, as_json)
    print_success(
        f"Pull request #{pr_id} aprovado.",
        as_json=as_json,
        json_payload={"id": pr_id, "status": "approved"},
    )


@pr_app.command("decline")
def pr_decline(
    ctx: typer.Context,
    pr_id: int = Argument(..., help="ID do pull request."),
    yes: bool = Option(False, "--yes", help="Confirma a recusa."),
    repo: str | None = Option(None, "--repo"),
    workspace: str | None = Option(None, "--workspace"),
    provider: str | None = Option(None, "--provider"),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Recusa ou fecha um pull request sem fazer merge."""
    as_json = is_json_mode(ctx, json_output)
    if pr_id < 1:
        _fail("O ID deve ser positivo.", as_json)
    if not yes:
        if as_json:
            _fail("Em modo JSON informe --yes.", True)
        if not typer.confirm(f"Recusar o pull request #{pr_id}?"):
            _fail("Operação cancelada.", as_json, ExitCode.ERROR)
    target, ws, client = _context(provider, workspace, repo, as_json)
    try:
        client.decline_pull_request(target, pr_id, workspace=ws)
    except BitbucketError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        _network_error(exc, as_json)
    print_success(
        f"Pull request #{pr_id} recusado.",
        as_json=as_json,
        json_payload={"id": pr_id, "status": "declined"},
    )


@pr_app.command("search")
def pr_search(
    ctx: typer.Context,
    query: str = Argument(..., help="ID exato ou trecho do título."),
    repo: str | None = Option(None, "--repo"),
    workspace: str | None = Option(None, "--workspace"),
    provider: str | None = Option(None, "--provider"),
    json_output: bool = Option(False, "--json", help="Emite saída JSON."),
) -> None:
    """Pesquisa pull requests pelo ID ou título."""
    as_json = is_json_mode(ctx, json_output)
    if not query.strip():
        _fail("Informe um ID ou trecho do título.", as_json)
    target, ws, client = _context(provider, workspace, repo, as_json)
    try:
        results = client.search_pull_requests(target, query.strip(), workspace=ws)
    except BitbucketError as exc:
        handle_git_provider_error(exc, as_json=as_json)
    except httpx.HTTPError as exc:
        _network_error(exc, as_json)
    _render_results(results, as_json)
