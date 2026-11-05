"""Operações de branches locais no repositório selecionado."""

from __future__ import annotations

import subprocess
from pathlib import Path

import typer

from neo.config import ExitCode
from neo.git_context import resolve_repo_path
from neo.output import print_error

__all__ = ["resolve_repo_path"]


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
