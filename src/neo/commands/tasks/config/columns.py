"""Ação de tarefas."""

from __future__ import annotations

import typer
from typer import Option

from neo.commands._credentials import is_json_mode
from neo.commands.tasks import _common as common
from neo.config import (
    set_task_columns_config,
)
from neo.output import print_error, print_success


def config_columns(
    ctx: typer.Context,
    service: str = common._service_option(),
    todo: str | None = Option(
        None,
        "--todo",
        help="Coluna(s) para 'A fazer' separadas por vírgula (ex: 'Backlog de Sprint, Bug').",
    ),
    doing: str | None = Option(
        None, "--doing", help="Coluna(s) para 'Fazendo' separadas por vírgula (ex: 'Em Progresso')."
    ),
    done: str | None = Option(
        None, "--done", help="Coluna(s) para 'Feito' separadas por vírgula (ex: 'Finalizado')."
    ),
) -> None:
    """Configura quais colunas do serviço correspondem a 'A fazer', 'Fazendo' e 'Feito'."""
    as_json = is_json_mode(ctx)
    svc = common._resolve_service(ctx, service)
    if todo is not None or doing is not None or done is not None:
        if not (todo and doing and done):
            print_error(
                "Para configurar via flags, informe simultaneamente `--todo`, `--doing` e `--done`.",
                as_json=as_json,
                code=1,
            )
            raise typer.Exit(code=1)
        todo_list = [c.strip() for c in todo.split(",") if c.strip()]
        doing_list = [c.strip() for c in doing.split(",") if c.strip()]
        done_list = [c.strip() for c in done.split(",") if c.strip()]
        try:
            set_task_columns_config(todo=todo_list, doing=doing_list, done=done_list, service=svc)
        except ValueError as e:
            print_error(str(e), as_json=as_json, code=1)
            raise typer.Exit(code=1) from e
        mapping = {"todo": todo_list, "doing": doing_list, "done": done_list}
        print_success(
            f"Colunas de '{svc}' atualizadas com sucesso!",
            as_json=as_json,
            json_payload={"status": "success", "service": svc, "columns": mapping},
        )
        return
    if as_json:
        print_error(
            "No modo `--json`, informe `--todo`, `--doing` e `--done` para configurar as colunas.",
            as_json=True,
            code=1,
        )
        raise typer.Exit(code=1)
    client = common._get_client(svc, as_json)
    common._interactive_configure_columns(client, svc, as_json=as_json)
