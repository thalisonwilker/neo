"""Utilitários de saída e formatação visual (Rich e JSON)."""

from __future__ import annotations

import json
import sys
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
error_console = Console(stderr=True, soft_wrap=True)


def print_json(data: Any) -> None:
    """Imprime dados serializados em JSON estrito no stdout."""
    sys.stdout.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def print_success(message: str, as_json: bool = False, json_payload: Any = None) -> None:
    """Emite mensagem de sucesso no formato apropriado."""
    if as_json:
        payload = (
            json_payload if json_payload is not None else {"status": "success", "message": message}
        )
        print_json(payload)
    else:
        console.print(f"[bold green]✓[/bold green] {message}")


def print_error(
    message: str, as_json: bool = False, json_payload: Any = None, code: int = 1
) -> None:
    """Emite mensagem de erro no formato apropriado."""
    if as_json:
        payload = (
            json_payload
            if json_payload is not None
            else {"status": "error", "code": code, "message": message}
        )
        print_json(payload)
    else:
        error_console.print(f"[bold red]✗ Erro:[/bold red] {message}")


def print_table(title: str, columns: list[str], rows: list[list[str]]) -> None:
    """Renderiza uma tabela estilizada com Rich."""
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*row)
    console.print(table)


def print_panel(title: str, text: str) -> None:
    """Renderiza um painel estilizado com Rich."""
    console.print(Panel(text, title=f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))
