"""Comandos financeiros."""

import typer

from neo.commands.fin.balance import fin_balance
from neo.commands.fin.bank.create import bank_create
from neo.commands.fin.bank.delete import bank_delete
from neo.commands.fin.bank.get import bank_get
from neo.commands.fin.bank.list import bank_list
from neo.commands.fin.bank.update import bank_update
from neo.commands.fin.category.create import category_create
from neo.commands.fin.category.delete import category_delete
from neo.commands.fin.category.get import category_get
from neo.commands.fin.category.list import category_list
from neo.commands.fin.expense import shortcut_expense
from neo.commands.fin.income import shortcut_income
from neo.commands.fin.summary import fin_summary
from neo.commands.fin.tx.create import tx_create
from neo.commands.fin.tx.delete import tx_delete
from neo.commands.fin.tx.get import tx_get
from neo.commands.fin.tx.list import tx_list
from neo.commands.fin.tx.update import tx_update

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

bank_app.command("add", hidden=True)(bank_create)
bank_app.command("create")(bank_create)
bank_app.command("show", hidden=True)(bank_get)
bank_app.command("get")(bank_get)
bank_app.command("list")(bank_list)
bank_app.command("edit", hidden=True)(bank_update)
bank_app.command("update")(bank_update)
bank_app.command("rm", hidden=True)(bank_delete)
bank_app.command("delete")(bank_delete)
category_app.command("add", hidden=True)(category_create)
category_app.command("create")(category_create)
category_app.command("show", hidden=True)(category_get)
category_app.command("get")(category_get)
category_app.command("list")(category_list)
category_app.command("rm", hidden=True)(category_delete)
category_app.command("delete")(category_delete)
tx_app.command("add", hidden=True)(tx_create)
tx_app.command("create")(tx_create)
tx_app.command("show", hidden=True)(tx_get)
tx_app.command("get")(tx_get)
tx_app.command("list")(tx_list)
tx_app.command("edit", hidden=True)(tx_update)
tx_app.command("update")(tx_update)
tx_app.command("rm", hidden=True)(tx_delete)
tx_app.command("delete")(tx_delete)
fin_app.command("expense")(shortcut_expense)
fin_app.command("income")(shortcut_income)
fin_app.command("balance")(fin_balance)
fin_app.command("summary")(fin_summary)
