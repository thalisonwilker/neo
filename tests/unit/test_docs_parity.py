"""Teste automatizado de paridade entre a CLI (Typer) e as páginas de documentação."""

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
    assert len(commands) == 36, f"Esperado 36 comandos na CLI, encontrado {len(commands)}"

    docs_dir = PROJECT_ROOT / "docs" / "cli"
    markdown_files = list(docs_dir.rglob("*.md"))
    all_content = "\n".join(f.read_text(encoding="utf-8") for f in markdown_files)

    missing: list[str] = []
    for cmd in commands:
        if cmd not in all_content:
            missing.append(cmd)

    assert not missing, f"Comandos da CLI sem documentação encontrada: {missing}"


def test_every_doc_page_corresponds_to_real_command_or_topic():
    """Garante que toda página em docs/cli/ corresponde a um recurso ou comando real."""
    docs_dir = PROJECT_ROOT / "docs" / "cli"
    doc_paths = [p.relative_to(docs_dir).as_posix() for p in docs_dir.rglob("*.md")]

    expected_pages = {
        "index.md",
        "git/index.md",
        "git/auth.md",
        "git/config.md",
        "git/status.md",
        "git/workspace.md",
        "git/repo.md",
        "git/commits.md",
        "git/planejado.md",
        "tasks/index.md",
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
    }

    assert set(doc_paths) == expected_pages, (
        f"Divergência nas páginas de documentação: {set(doc_paths) ^ expected_pages}"
    )
