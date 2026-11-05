"""Comandos de consulta e histórico de commits Git (`neo git commits`: `list`, `search`, `show`)."""

from __future__ import annotations

import typer

from neo.config import ExitCode
from neo.integrations.git.models import GitCommit
from neo.integrations.git.resolver import (
    detect_git_remote_info,
)
from neo.output import print_error, print_json, print_panel, print_table


def _infer_repo_slug_from_git() -> str | None:
    """Tenta inferir o slug do repositório a partir do remote origin do diretório local."""
    return detect_git_remote_info()[1]


def _resolve_target_repo(repo_opt: str | None, as_json: bool) -> str:
    target_repo = (repo_opt or _infer_repo_slug_from_git() or "").strip()
    if not target_repo:
        msg = (
            "Repositório não informado e não foi possível inferir do Git local. "
            "Use a opção `--repo <slug>` para especificar o repositório."
        )
        print_error(msg, as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    return target_repo


def _render_commits_output(
    commits: list[GitCommit],
    target_repo: str,
    prov_name: str,
    as_json: bool,
) -> None:
    if as_json:
        print_json([c.model_dump() for c in commits])
        return

    prov_title = "GitHub" if prov_name == "github" else "Bitbucket"
    if not commits:
        print_panel(
            "Commits",
            f"Nenhum commit encontrado para os filtros informados em '{target_repo}' ({prov_title}).",
        )
        return

    columns = ["Hash", "Autor", "Data", "Mensagem"]
    rows: list[list[str]] = []
    for c in commits:
        date_str = c.date.split("T")[0] if "T" in c.date else c.date
        rows.append(
            [
                f"[bold yellow]{c.short_hash}[/bold yellow]",
                c.author.author_name,
                date_str,
                c.summary,
            ]
        )

    print_table(f"Histórico de Commits ({target_repo} via {prov_title})", columns, rows)
