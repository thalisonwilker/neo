"""Operações de branches locais no repositório selecionado."""

from __future__ import annotations

import subprocess
from pathlib import Path

import typer
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.git_context import resolve_repo_path
from neo.output import print_error, print_json, print_success, print_table

branch_app = typer.Typer(
    name="branch",
    help="Lista, seleciona, cria e exclui branches locais do repositório selecionado.",
    no_args_is_help=True,
)


def _git(path: Path, *args: str) -> str:
    """Executa Git sem shell e transforma erros em mensagens de uso."""
    try:
        result = subprocess.run(
            ["git", *args], cwd=path, capture_output=True, text=True, check=False
        )
    except OSError as exc:
        raise ValueError("Não foi possível executar o Git no repositório selecionado.") from exc
    if result.returncode:
        raise ValueError(
            result.stderr.strip() or "Falha ao executar Git no repositório selecionado."
        )
    return result.stdout.strip()


def current_branch() -> str | None:
    """Retorna a branch local ativa ou None para HEAD destacado."""
    path = resolve_repo_path()
    return _git(path, "branch", "--show-current") or None


def select_branch(name: str) -> None:
    """Faz checkout de uma branch local existente."""
    branch = name.strip()
    if not branch or branch.startswith("-"):
        raise ValueError("Informe um nome de branch válido.")
    path = resolve_repo_path()
    # Exige branch local; não cria branch de rastreamento implícita para uma remota.
    _git(path, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
    _git(path, "switch", "--", branch)


def _fail(exc: ValueError, as_json: bool) -> None:
    print_error(str(exc), as_json=as_json, code=int(ExitCode.ERROR))
    raise typer.Exit(code=int(ExitCode.ERROR)) from exc


@branch_app.command("list")
def branch_list(
    ctx: typer.Context,
    json_output: bool = Option(False, "--json", help="Emite JSON estruturado."),
) -> None:
    """Lista branches locais e identifica a branch ativa."""
    as_json = is_json_mode(ctx, json_output)
    try:
        path = resolve_repo_path()
        names = _git(path, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
        active = _git(path, "branch", "--show-current") or None
    except ValueError as exc:
        _fail(exc, as_json)
    data = [{"name": name, "active": name == active} for name in names]
    if as_json:
        print_json(data)
    else:
        print_table(
            "Branches locais",
            ["Branch", "Ativa"],
            [[name, "Sim" if name == active else "-"] for name in names],
        )


@branch_app.command("select")
def branch_select(
    ctx: typer.Context, name: str = Argument(..., help="Nome da branch local.")
) -> None:
    """Seleciona a branch local com checkout."""
    as_json = is_json_mode(ctx)
    try:
        select_branch(name)
    except ValueError as exc:
        _fail(exc, as_json)
    print_success(f"Branch selecionada: {name}", as_json=as_json, json_payload={"branch": name})


@branch_app.command("create")
def branch_create(
    ctx: typer.Context, name: str = Argument(..., help="Nome da nova branch local.")
) -> None:
    """Cria uma branch local sem alterar a branch ativa."""
    as_json = is_json_mode(ctx)
    try:
        if not name.strip() or name.startswith("-"):
            raise ValueError("Informe um nome de branch válido.")
        _git(resolve_repo_path(), "branch", "--", name)
    except ValueError as exc:
        _fail(exc, as_json)
    print_success(f"Branch criada: {name}", as_json=as_json, json_payload={"branch": name})


@branch_app.command("delete")
def branch_delete(
    ctx: typer.Context,
    name: str = Argument(..., help="Nome da branch local a excluir."),
    yes: bool = Option(False, "--yes", help="Confirma a exclusão sem perguntar."),
) -> None:
    """Exclui uma branch local já mesclada, mediante confirmação."""
    as_json = is_json_mode(ctx)
    try:
        if not name.strip() or name.startswith("-"):
            raise ValueError("Informe um nome de branch válido.")
        path = resolve_repo_path()
        active = _git(path, "branch", "--show-current")
        if name == active:
            raise ValueError("Não é possível excluir a branch ativa.")
        if not yes:
            if as_json:
                raise ValueError("Use --yes para confirmar a exclusão em modo JSON.")
            if not typer.confirm(f"Excluir a branch local '{name}'?"):
                raise ValueError("Operação cancelada pelo usuário.")
        _git(path, "branch", "-d", "--", name)
    except ValueError as exc:
        _fail(exc, as_json)
    print_success(f"Branch excluída: {name}", as_json=as_json, json_payload={"branch": name})
