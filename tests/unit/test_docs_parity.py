"""Teste automatizado de paridade entre a CLI (Typer) e as páginas de documentação."""

import re
from pathlib import Path

import typer

from neo.cli import app

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_all_typer_commands() -> list[str]:
    """Extrai recursivamente todos os comandos visíveis e ativos do Typer."""
    root = typer.main.get_command(app)
    commands: list[str] = []

    def walk(cmd, path: str = "neo"):
        if hasattr(cmd, "commands"):
            for name, sub in sorted(cmd.commands.items()):
                if getattr(sub, "hidden", False):
                    continue
                walk(sub, f"{path} {name}")
        else:
            if not getattr(cmd, "hidden", False):
                commands.append(path)

    walk(root)
    return commands


def test_every_typer_command_is_documented():
    """Garante que todo comando visível em `neo --help` tem cobertura nas páginas de documentação."""
    commands = get_all_typer_commands()

    docs_dir = PROJECT_ROOT / "docs" / "cli"
    markdown_files = list(docs_dir.rglob("*.md"))
    all_content = "\n".join(f.read_text(encoding="utf-8") for f in markdown_files)

    missing: list[str] = []
    for cmd in commands:
        if cmd not in all_content:
            missing.append(cmd)

    assert not missing, f"Comandos da CLI sem documentação encontrada: {missing}"


def test_AC_3_command_tree_matches_visible_cli():
    """0026 AC-3: a árvore mantém todos os comandos visíveis na hierarquia correta."""
    content = (PROJECT_ROOT / "docs" / "cli" / "comandos.md").read_text(encoding="utf-8")
    stack: list[tuple[int, str]] = []
    paths: set[str] = set()
    for line in content.splitlines():
        match = re.match(r"^(\s*)- .*?`([^`]+)`", line)
        if not match:
            continue
        indent, name = len(match.group(1)), match.group(2)
        if indent and name.startswith("neo "):
            continue
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = name if not indent else f"{stack[-1][1]} {name}"
        stack.append((indent, path))
        paths.add(path)
    assert set(get_all_typer_commands()) <= paths
    assert "neo git pr" in paths


def test_every_doc_page_corresponds_to_real_command_or_topic():
    """Garante que toda página em docs/cli/ corresponde a um recurso ou comando real."""
    docs_dir = PROJECT_ROOT / "docs" / "cli"
    doc_paths = [p.relative_to(docs_dir).as_posix() for p in docs_dir.rglob("*.md")]

    expected_pages = {
        "index.md",
        "comandos.md",
        "config/index.md",
        "git/index.md",
        "git/auth.md",
        "git/config.md",
        "git/status.md",
        "git/workspace.md",
        "git/repo/index.md",
        "git/repo/list.md",
        "git/repo/select.md",
        "git/repo/remote-list.md",
        "git/repo/local-list.md",
        "git/repo/search.md",
        "git/repo/show.md",
        "git/repo/create.md",
        "git/repo/edit.md",
        "git/branch/index.md",
        "git/branch/list.md",
        "git/branch/create.md",
        "git/branch/select.md",
        "git/branch/delete.md",
        "git/commits/index.md",
        "git/commits/list.md",
        "git/commits/search.md",
        "git/commits/show.md",
        "git/pr/index.md",
        "git/pr/list.md",
        "git/pr/open.md",
        "git/pr/approve.md",
        "git/pr/decline.md",
        "git/pr/search.md",
        "git/planejado.md",
        "tasks/index.md",
        "tasks/create.md",
        "tasks/check.md",
        "tasks/comment.md",
        "tasks/resume.md",
        "tasks/whoami.md",
        "tasks/iterations.md",
        "tasks/list.md",
        "tasks/search.md",
        "tasks/show.md",
        "tasks/analyze.md",
        "tasks/config.md",
        "agent/index.md",
        "agent/config.md",
        "agent/status.md",
        "agent/setup.md",
        "agent/run.md",
        "fin/index.md",
        "fin/bank.md",
        "fin/category.md",
        "fin/tx.md",
        "fin/summary.md",
    }

    assert set(doc_paths) == expected_pages, (
        f"Divergência nas páginas de documentação: {set(doc_paths) ^ expected_pages}"
    )
