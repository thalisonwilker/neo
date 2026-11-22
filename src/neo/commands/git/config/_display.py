"""Apresentação das configurações Git para o terminal."""

from pathlib import Path

from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def git_config_panel(values: dict[str, dict[str, str | None]]) -> Panel:
    """Monta o painel de configurações sem interpretar os valores como markup."""
    provider = values["provider"]["value"]
    workspace = values["workspace"]["value"]
    api_key = values["api-key"]["value"]
    repo = values["repo"]["value"]
    task = values["task"]["value"] if repo else None

    rows: list[tuple[str, str, str]] = [
        (
            "provider",
            f"{provider} (Configurado)" if provider else "Não configurado",
            "green" if provider else "white",
        ),
        ("workspace", workspace or "Não configurado", "green" if workspace else "white"),
        ("branch", values["default-branch"]["value"] or "-", "white"),
        ("branch-pattern", values["branch-pattern"]["value"] or "-", "white"),
        ("commit-format", values["commit-format"]["value"] or "-", "white"),
        (
            "api-key",
            "Configurado" if api_key else "Não configurado",
            "green" if api_key else "white",
        ),
        ("repo", Path(repo).name if repo else "Não configurado", "green" if repo else "white"),
        (
            "task",
            f"#{task.strip().lstrip('#')}" if task else "Sem task definida",
            "green" if task else "white",
        ),
    ]
    if provider == "bitbucket":
        project = values.get("project", {}).get("value")
        rows.insert(2, ("project", project or "Não configurado", "green" if project else "white"))
    table = Table.grid(padding=(0, 2))
    table.add_column()
    table.add_column()
    for label, value, style in rows:
        table.add_row(Text(f"{label}:"), Text(value, style=style))
    return Panel(table, title="Git", border_style="cyan", expand=False)
