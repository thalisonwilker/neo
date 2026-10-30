"""Comandos CLI de micro gerenciamento financeiro pessoal (`neo fin`)."""

from __future__ import annotations

import typer
from rich.panel import Panel
from rich.table import Table
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.config import ExitCode
from neo.output import console, print_error, print_json, print_panel, print_success, print_table
from neo.services.finance import (
    AccountInUseError,
    AccountNotFoundError,
    CategoryInUseError,
    CategoryNotFoundError,
    DuplicateEntityError,
    FinanceService,
    TransactionNotFoundError,
)

fin_app = typer.Typer(
    name="fin",
    help="Micro gerenciamento financeiro pessoal local com SQLite (bancos, categorias, despesas e receitas).",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

bank_app = typer.Typer(
    name="bank",
    help="Gerenciamento de contas bancárias e carteiras (create, get, list, update, delete).",
    no_args_is_help=True,
)

category_app = typer.Typer(
    name="category",
    help="Gerenciamento de categorias de despesas e receitas (create, get, list, delete).",
    no_args_is_help=True,
)

tx_app = typer.Typer(
    name="tx",
    help="Gerenciamento de transações financeiras (create, get, list, update, delete).",
    no_args_is_help=True,
)

fin_app.add_typer(bank_app, name="bank")
fin_app.add_typer(category_app, name="category")
fin_app.add_typer(tx_app, name="tx")


def _get_service() -> FinanceService:
    return FinanceService()


# -----------------------------------------------------------------------------
# Subcomando: neo fin bank
# -----------------------------------------------------------------------------


@bank_app.command("create")
@bank_app.command("add", hidden=True)
def bank_create(
    ctx: typer.Context,
    slug: str = Argument(..., help="Identificador único da conta (ex: nubank, inter, carteira)."),
    name: str = Option(..., "--name", "-n", help="Nome de exibição da conta."),
    account_type: str = Option(
        "checking",
        "--type",
        "-t",
        help="Tipo de conta (checking, savings, investment, credit, cash, other).",
    ),
    balance: float = Option(0.0, "--balance", "-b", help="Saldo inicial da conta (default: 0.0)."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Cadastra uma nova conta bancária ou carteira."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        acc = service.create_account(
            slug=slug, name=name, account_type=account_type, initial_balance=balance
        )
    except DuplicateEntityError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR))
    except ValueError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))

    if as_json:
        print_json(acc.to_dict())
    else:
        print_success(
            f"Conta '{acc.name}' ({acc.slug}) criada com saldo inicial de R$ {acc.initial_balance:.2f}."
        )


@bank_app.command("get")
@bank_app.command("show", hidden=True)
def bank_get(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da conta bancária."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe detalhes de uma conta bancária específica."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        acc = service.get_account(slug)
    except AccountNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    if as_json:
        print_json(acc.to_dict())
    else:
        cor_saldo = "green" if acc.current_balance >= 0 else "red"
        text = (
            f"[bold]Slug:[/bold] {acc.slug}\n"
            f"[bold]Nome:[/bold] {acc.name}\n"
            f"[bold]Tipo:[/bold] {acc.account_type}\n"
            f"[bold]Saldo Inicial:[/bold] R$ {acc.initial_balance:.2f}\n"
            f"[bold]Saldo Atual:[/bold] [{cor_saldo}]R$ {acc.current_balance:.2f}[/{cor_saldo}]\n"
            f"[bold]Criado em:[/bold] {acc.created_at}"
        )
        print_panel(f"Conta: {acc.name}", text)


@bank_app.command("list")
def bank_list(
    ctx: typer.Context,
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Lista todas as contas bancárias cadastradas e seus saldos atuais."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()
    accounts = service.list_accounts()

    if as_json:
        print_json([a.to_dict() for a in accounts])
    else:
        if not accounts:
            console.print(
                "[yellow]Nenhuma conta bancária cadastrada. Use 'neo fin bank create' para criar uma.[/yellow]"
            )
            return

        rows = [
            [
                a.slug,
                a.name,
                a.account_type,
                f"R$ {a.initial_balance:.2f}",
                f"R$ {a.current_balance:.2f}",
            ]
            for a in accounts
        ]
        print_table(
            "Contas Bancárias e Carteiras",
            ["Slug", "Nome", "Tipo", "Saldo Inicial", "Saldo Atual"],
            rows,
        )


@bank_app.command("update")
@bank_app.command("edit", hidden=True)
def bank_update(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da conta a editar."),
    name: str | None = Option(None, "--name", "-n", help="Novo nome de exibição da conta."),
    account_type: str | None = Option(None, "--type", "-t", help="Novo tipo da conta."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Atualiza metadados de uma conta existente."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        acc = service.update_account(slug=slug, name=name, account_type=account_type)
    except AccountNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    if as_json:
        print_json(acc.to_dict())
    else:
        print_success(
            f"Conta '{acc.slug}' atualizada com sucesso para '{acc.name}' ({acc.account_type})."
        )


@bank_app.command("delete")
@bank_app.command("rm", hidden=True)
def bank_delete(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da conta a remover."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Remove uma conta bancária sem movimentações associadas."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        service.delete_account(slug=slug)
    except AccountNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    except AccountInUseError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR))

    if as_json:
        print_json({"status": "success", "message": f"Conta '{slug}' removida com sucesso."})
    else:
        print_success(f"Conta '{slug}' removida com sucesso.")


# -----------------------------------------------------------------------------
# Subcomando: neo fin category
# -----------------------------------------------------------------------------


@category_app.command("create")
@category_app.command("add", hidden=True)
def category_create(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug único da categoria (ex: jogos, cursos, mercado)."),
    name: str = Option(..., "--name", "-n", help="Nome de exibição da categoria."),
    category_type: str = Option(
        ..., "--type", "-t", help="Tipo da categoria: 'expense' ou 'income'."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Cadastra uma nova categoria de despesa ou receita."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    if category_type not in ("expense", "income"):
        print_error(
            "Tipo de categoria inválido. Use 'expense' ou 'income'.",
            as_json=as_json,
            code=int(ExitCode.USAGE_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))

    try:
        cat = service.create_category(slug=slug, name=name, category_type=category_type)
    except DuplicateEntityError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR))

    if as_json:
        print_json(cat.to_dict())
    else:
        tipo_lbl = "Despesa" if cat.category_type == "expense" else "Receita"
        print_success(f"Categoria '{cat.name}' ({cat.slug}) criada para {tipo_lbl}.")


@category_app.command("get")
@category_app.command("show", hidden=True)
def category_get(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da categoria."),
    category_type: str | None = Option(
        None, "--type", "-t", help="Tipo da categoria ('expense' ou 'income')."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe detalhes de uma categoria específica."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        cat = service.get_category(slug, category_type=category_type)
    except CategoryNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    if as_json:
        print_json(cat.to_dict())
    else:
        tipo_lbl = "Despesa" if cat.category_type == "expense" else "Receita"
        text = (
            f"[bold]Slug:[/bold] {cat.slug}\n"
            f"[bold]Nome:[/bold] {cat.name}\n"
            f"[bold]Tipo:[/bold] {tipo_lbl}\n"
            f"[bold]Categoria Padrão:[/bold] {'Sim' if cat.is_default else 'Não'}\n"
            f"[bold]Criado em:[/bold] {cat.created_at}"
        )
        print_panel(f"Categoria: {cat.name}", text)


@category_app.command("list")
def category_list(
    ctx: typer.Context,
    category_type: str | None = Option(
        None, "--type", "-t", help="Filtrar por tipo: 'expense' ou 'income'."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Lista as categorias de despesas e receitas cadastradas."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    if category_type and category_type not in ("expense", "income"):
        print_error(
            "Tipo de categoria inválido. Use 'expense' ou 'income'.",
            as_json=as_json,
            code=int(ExitCode.USAGE_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))

    categories = service.list_categories(category_type=category_type)

    if as_json:
        print_json([c.to_dict() for c in categories])
    else:
        rows = [
            [
                c.slug,
                c.name,
                "Despesa" if c.category_type == "expense" else "Receita",
                "Sim" if c.is_default else "Não",
            ]
            for c in categories
        ]
        titulo = f"Categorias ({category_type})" if category_type else "Categorias de Transações"
        print_table(titulo, ["Slug", "Nome", "Tipo", "Padrão"], rows)


@category_app.command("delete")
@category_app.command("rm", hidden=True)
def category_delete(
    ctx: typer.Context,
    slug: str = Argument(..., help="Slug da categoria a remover."),
    category_type: str | None = Option(
        None, "--type", "-t", help="Tipo da categoria ('expense' ou 'income')."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Remove uma categoria que não possua transações vinculadas."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        service.delete_category(slug=slug, category_type=category_type)
    except CategoryNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    except CategoryInUseError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR))

    if as_json:
        print_json({"status": "success", "message": f"Categoria '{slug}' removida com sucesso."})
    else:
        print_success(f"Categoria '{slug}' removida com sucesso.")


# -----------------------------------------------------------------------------
# Subcomando: neo fin tx
# -----------------------------------------------------------------------------


@tx_app.command("create")
@tx_app.command("add", hidden=True)
def tx_create(
    ctx: typer.Context,
    amount: float = Argument(..., help="Valor da movimentação (positivo)."),
    description: str = Argument(..., help="Descrição da transação."),
    transaction_type: str = Option(
        ..., "--type", "-t", help="Tipo de transação: 'expense' ou 'income'."
    ),
    account: str | None = Option(
        None, "--account", "-a", help="Slug da conta bancária (padrão: primeira conta)."
    ),
    category: str | None = Option(
        None, "--category", "-c", help="Slug da categoria (padrão: 'outros')."
    ),
    date_str: str | None = Option(
        None, "--date", "-d", help="Data da transação no formato YYYY-MM-DD (padrão: hoje)."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Registra uma transação genérica de despesa ou receita."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        tx = service.create_transaction(
            amount=amount,
            description=description,
            transaction_type=transaction_type,
            account_slug=account,
            category_slug=category,
            date_str=date_str,
        )
    except ValueError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    except AccountNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    except CategoryNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    if as_json:
        print_json(tx.to_dict())
    else:
        tipo_lbl = "Despesa" if tx.transaction_type == "expense" else "Receita"
        cor = "red" if tx.transaction_type == "expense" else "green"
        print_success(
            f"{tipo_lbl} de [{cor}]R$ {tx.amount:.2f}[/{cor}] registrada na conta '{tx.account_name}' ({tx.category_name})."
        )


@tx_app.command("get")
@tx_app.command("show", hidden=True)
def tx_get(
    ctx: typer.Context,
    tx_id: int = Argument(..., help="ID numérico da transação."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe detalhes completos de uma transação específica."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        tx = service.get_transaction(tx_id)
    except TransactionNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    if as_json:
        print_json(tx.to_dict())
    else:
        tipo_lbl = (
            "[red]Despesa[/red]" if tx.transaction_type == "expense" else "[green]Receita[/green]"
        )
        val_str = (
            f"[red]-R$ {tx.amount:.2f}[/red]"
            if tx.transaction_type == "expense"
            else f"[green]+R$ {tx.amount:.2f}[/green]"
        )
        text = (
            f"[bold]ID:[/bold] #{tx.id}\n"
            f"[bold]Data:[/bold] {tx.date}\n"
            f"[bold]Tipo:[/bold] {tipo_lbl}\n"
            f"[bold]Valor:[/bold] {val_str}\n"
            f"[bold]Descrição:[/bold] {tx.description}\n"
            f"[bold]Conta:[/bold] {tx.account_name} ({tx.account_slug})\n"
            f"[bold]Categoria:[/bold] {tx.category_name} ({tx.category_slug})\n"
            f"[bold]Registrado em:[/bold] {tx.created_at}"
        )
        print_panel(f"Transação #{tx.id}", text)


@tx_app.command("list")
def tx_list(
    ctx: typer.Context,
    month: str | None = Option(None, "--month", "-m", help="Filtrar por mês no formato YYYY-MM."),
    account: str | None = Option(None, "--account", "-a", help="Filtrar pelo slug da conta."),
    category: str | None = Option(None, "--category", "-c", help="Filtrar pelo slug da categoria."),
    transaction_type: str | None = Option(
        None, "--type", "-t", help="Filtrar por tipo: 'expense' ou 'income'."
    ),
    limit: int = Option(50, "--limit", "-l", help="Quantidade máxima de registros a exibir."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Lista transações financeiras com opções de filtros."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()
    txs = service.list_transactions(
        month=month,
        account_slug=account,
        category_slug=category,
        transaction_type=transaction_type,
        limit=limit,
    )

    if as_json:
        print_json([t.to_dict() for t in txs])
    else:
        if not txs:
            console.print(
                "[yellow]Nenhuma transação encontrada para os filtros especificados.[/yellow]"
            )
            return

        table = Table(title="Extrato de Transações", show_header=True, header_style="bold cyan")
        table.add_column("ID", justify="right")
        table.add_column("Data")
        table.add_column("Tipo")
        table.add_column("Valor", justify="right")
        table.add_column("Descrição")
        table.add_column("Conta")
        table.add_column("Categoria")

        for t in txs:
            if t.transaction_type == "expense":
                tipo_str = "[red]Despesa[/red]"
                val_str = f"[red]-R$ {t.amount:.2f}[/red]"
            else:
                tipo_str = "[green]Receita[/green]"
                val_str = f"[green]+R$ {t.amount:.2f}[/green]"

            table.add_row(
                str(t.id),
                t.date,
                tipo_str,
                val_str,
                t.description,
                t.account_name or "",
                t.category_name or "",
            )
        console.print(table)


@tx_app.command("update")
@tx_app.command("edit", hidden=True)
def tx_update(
    ctx: typer.Context,
    tx_id: int = Argument(..., help="ID da transação a ser editada."),
    amount: float | None = Option(None, "--amount", help="Novo valor da transação."),
    desc: str | None = Option(None, "--desc", help="Nova descrição da transação."),
    account: str | None = Option(None, "--account", "-a", help="Novo slug de conta."),
    category: str | None = Option(None, "--category", "-c", help="Novo slug de categoria."),
    date_str: str | None = Option(None, "--date", "-d", help="Nova data no formato YYYY-MM-DD."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Edita uma transação existente recalculando os saldos."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        tx = service.update_transaction(
            tx_id=tx_id,
            amount=amount,
            description=desc,
            date_str=date_str,
            account_slug=account,
            category_slug=category,
        )
    except TransactionNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    except (AccountNotFoundError, CategoryNotFoundError) as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))
    except ValueError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))

    if as_json:
        print_json(tx.to_dict())
    else:
        print_success(
            f"Transação #{tx.id} atualizada com sucesso (R$ {tx.amount:.2f} - {tx.description})."
        )


@tx_app.command("delete")
@tx_app.command("rm", hidden=True)
def tx_delete(
    ctx: typer.Context,
    tx_id: int = Argument(..., help="ID da transação a ser removida."),
    yes: bool = Option(False, "--yes", "-y", help="Pula confirmação interativa."),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exclui uma transação financeira existente."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        tx = service.get_transaction(tx_id)
    except TransactionNotFoundError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    if not yes and not as_json:
        confirm = typer.confirm(
            f"Deseja realmente remover a transação #{tx.id} ({tx.description} - R$ {tx.amount:.2f})?"
        )
        if not confirm:
            console.print("[yellow]Operação cancelada pelo usuário.[/yellow]")
            return

    service.delete_transaction(tx_id)

    if as_json:
        print_json({"status": "success", "message": f"Transação #{tx_id} removida com sucesso."})
    else:
        print_success(f"Transação #{tx_id} excluída com sucesso.")


# -----------------------------------------------------------------------------
# Atalhos rápidos e resumos diretos sob `neo fin`
# -----------------------------------------------------------------------------


@fin_app.command("expense")
def shortcut_expense(
    ctx: typer.Context,
    amount: float = Argument(..., help="Valor da despesa (positivo)."),
    description: str = Argument(..., help="Descrição da despesa."),
    account: str | None = Option(
        None, "--account", "-a", help="Slug da conta bancária (padrão: primeira conta)."
    ),
    category: str | None = Option(
        None, "--category", "-c", help="Slug da categoria de despesa (padrão: 'outros')."
    ),
    date_str: str | None = Option(
        None, "--date", "-d", help="Data no formato YYYY-MM-DD (padrão: hoje)."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Atalho rápido para registrar uma despesa."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        tx = service.create_transaction(
            amount=amount,
            description=description,
            transaction_type="expense",
            account_slug=account,
            category_slug=category,
            date_str=date_str,
        )
    except ValueError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    except (AccountNotFoundError, CategoryNotFoundError) as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    if as_json:
        print_json(tx.to_dict())
    else:
        print_success(
            f"Despesa registrada: [red]-R$ {tx.amount:.2f}[/red] na conta '{tx.account_name}' ({tx.category_name} - {tx.description})."
        )


@fin_app.command("income")
def shortcut_income(
    ctx: typer.Context,
    amount: float = Argument(..., help="Valor da receita (positivo)."),
    description: str = Argument(..., help="Descrição da receita."),
    account: str | None = Option(
        None, "--account", "-a", help="Slug da conta bancária (padrão: primeira conta)."
    ),
    category: str | None = Option(
        None,
        "--category",
        "-c",
        help="Slug da categoria de receita (padrão: 'salario' ou 'outros').",
    ),
    date_str: str | None = Option(
        None, "--date", "-d", help="Data no formato YYYY-MM-DD (padrão: hoje)."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Atalho rápido para registrar uma receita."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()

    try:
        tx = service.create_transaction(
            amount=amount,
            description=description,
            transaction_type="income",
            account_slug=account,
            category_slug=category,
            date_str=date_str,
        )
    except ValueError as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.USAGE_ERROR))
        raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
    except (AccountNotFoundError, CategoryNotFoundError) as err:
        print_error(str(err), as_json=as_json, code=int(ExitCode.NOT_FOUND))
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))

    if as_json:
        print_json(tx.to_dict())
    else:
        print_success(
            f"Receita registrada: [green]+R$ {tx.amount:.2f}[/green] na conta '{tx.account_name}' ({tx.category_name} - {tx.description})."
        )


@fin_app.command("balance")
def fin_balance(
    ctx: typer.Context,
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe o balanço financeiro consolidado de todas as contas."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()
    bal = service.get_balance_summary()

    if as_json:
        print_json(bal.to_dict())
    else:
        table = Table(
            title="Balanço Consolidado por Conta", show_header=True, header_style="bold cyan"
        )
        table.add_column("Slug")
        table.add_column("Nome")
        table.add_column("Tipo")
        table.add_column("Saldo Inicial", justify="right")
        table.add_column("Saldo Atual", justify="right")

        for a in bal.accounts:
            cor_saldo = "green" if a.current_balance >= 0 else "red"
            table.add_row(
                a.slug,
                a.name,
                a.account_type,
                f"R$ {a.initial_balance:.2f}",
                f"[{cor_saldo}]R$ {a.current_balance:.2f}[/{cor_saldo}]",
            )
        console.print(table)

        cor_patr = "green" if bal.total_current >= 0 else "red"
        totais_text = (
            f"[bold]Total Inicial:[/bold] R$ {bal.total_initial:.2f}\n"
            f"[bold]Total Receitas:[/bold] [green]+R$ {bal.total_income:.2f}[/green]\n"
            f"[bold]Total Despesas:[/bold] [red]-R$ {bal.total_expense:.2f}[/red]\n"
            f"[bold]Patrimônio Consolidado:[/bold] [{cor_patr}]R$ {bal.total_current:.2f}[/{cor_patr}]"
        )
        console.print(
            Panel(totais_text, title="[bold cyan]Totais Gerais[/bold cyan]", border_style="cyan")
        )


@fin_app.command("summary")
def fin_summary(
    ctx: typer.Context,
    month: str | None = Option(
        None, "--month", "-m", help="Mês de apuração no formato YYYY-MM (padrão: mês atual)."
    ),
    json_output: bool = Option(
        False, "--json", help="Emite a saída estruturada em JSON no stdout."
    ),
) -> None:
    """Exibe o resumo consolidado de um mês com detalhamento de despesas por categoria."""
    as_json = is_json_mode(ctx, json_output)
    service = _get_service()
    summary = service.get_monthly_summary(month=month)

    if as_json:
        print_json(summary.to_dict())
    else:
        cor_liq = "green" if summary.net_balance >= 0 else "red"
        resumo_text = (
            f"[bold]Mês de Referência:[/bold] {summary.month}\n"
            f"[bold]Receitas:[/bold] [green]+R$ {summary.total_income:.2f}[/green]\n"
            f"[bold]Despesas:[/bold] [red]-R$ {summary.total_expense:.2f}[/red]\n"
            f"[bold]Resultado Líquido:[/bold] [{cor_liq}]R$ {summary.net_balance:.2f}[/{cor_liq}]"
        )
        console.print(
            Panel(
                resumo_text,
                title=f"[bold cyan]Resumo Mensal ({summary.month})[/bold cyan]",
                border_style="cyan",
            )
        )

        if summary.expenses_by_category:
            cat_table = Table(
                title="Despesas por Categoria", show_header=True, header_style="bold cyan"
            )
            cat_table.add_column("Categoria")
            cat_table.add_column("Total Gasto", justify="right")
            cat_table.add_column("Participação", justify="right")

            for c in summary.expenses_by_category:
                cat_table.add_row(
                    c.category_name,
                    f"[red]R$ {c.total:.2f}[/red]",
                    f"{c.percentage:.1f}%",
                )
            console.print(cat_table)
        else:
            console.print("[dim]Nenhuma despesa registrada para este mês.[/dim]")
