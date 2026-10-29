"""Testes E2E para transações e atalhos rápidos (`neo fin tx`, `expense`, `income`)."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_file = tmp_path / "finance_tx_test.db"
    monkeypatch.setenv("NEO_FINANCE_DB", str(db_file))


def test_transactions_lifecycle_and_shortcuts() -> None:
    # 1. Setup account
    runner.invoke(
        app,
        ["fin", "bank", "add", "nubank", "--name", "Nubank Principal", "--balance", "1000.0"],
    )

    # 2. Add expense using shortcut `neo fin expense`
    res_exp = runner.invoke(
        app,
        [
            "fin",
            "expense",
            "45.50",
            "Almoço no restaurante",
            "-a",
            "nubank",
            "-c",
            "alimentacao",
            "-d",
            "2026-10-15",
        ],
    )
    assert res_exp.exit_code == int(ExitCode.SUCCESS)
    assert "Despesa registrada" in res_exp.output

    # 3. Add income using shortcut `neo fin income`
    res_inc = runner.invoke(
        app,
        [
            "fin",
            "income",
            "3500.00",
            "Salário da empresa",
            "-a",
            "nubank",
            "-c",
            "salario",
            "-d",
            "2026-10-05",
        ],
    )
    assert res_inc.exit_code == int(ExitCode.SUCCESS)
    assert "Receita registrada" in res_inc.output

    # 4. Add generic transaction `neo fin tx add`
    res_tx_add = runner.invoke(
        app,
        [
            "fin",
            "tx",
            "add",
            "120.00",
            "Internet Fibra",
            "--type",
            "expense",
            "-a",
            "nubank",
            "-c",
            "moradia",
        ],
    )
    assert res_tx_add.exit_code == int(ExitCode.SUCCESS)

    # 5. List transactions with filters (JSON)
    res_list = runner.invoke(app, ["fin", "tx", "list", "--type", "expense", "--json"])
    assert res_list.exit_code == int(ExitCode.SUCCESS)
    txs = json.loads(res_list.output)
    assert len(txs) == 2
    tx_ids = [t["id"] for t in txs]

    # Filter by month
    res_month = runner.invoke(app, ["fin", "tx", "list", "--month", "2026-10", "--json"])
    assert res_month.exit_code == int(ExitCode.SUCCESS)
    txs_month = json.loads(res_month.output)
    assert len(txs_month) >= 2

    # 6. Edit transaction
    tx_to_edit = tx_ids[0]
    res_edit = runner.invoke(
        app,
        [
            "fin",
            "tx",
            "edit",
            str(tx_to_edit),
            "--amount",
            "150.00",
            "--desc",
            "Internet Fibra Turbo",
        ],
    )
    assert res_edit.exit_code == int(ExitCode.SUCCESS)
    assert "atualizada" in res_edit.output

    # 7. Remove transaction
    res_rm = runner.invoke(app, ["fin", "tx", "rm", str(tx_to_edit), "--yes"])
    assert res_rm.exit_code == int(ExitCode.SUCCESS)

    # Removing again should fail with NOT_FOUND
    res_rm_nf = runner.invoke(app, ["fin", "tx", "rm", str(tx_to_edit), "--yes"])
    assert res_rm_nf.exit_code == int(ExitCode.NOT_FOUND)


def test_transactions_validation_errors() -> None:
    runner.invoke(app, ["fin", "bank", "add", "itau", "--name", "Itaú"])

    # Zero or negative amount
    res_zero = runner.invoke(app, ["fin", "expense", "0", "Inválido"])
    assert res_zero.exit_code == int(ExitCode.USAGE_ERROR)

    res_neg = runner.invoke(app, ["fin", "expense", "-10", "Inválido"])
    assert res_neg.exit_code == int(ExitCode.USAGE_ERROR)

    # Invalid date
    res_date = runner.invoke(app, ["fin", "expense", "10", "Teste", "-d", "2026/10/29"])
    assert res_date.exit_code == int(ExitCode.USAGE_ERROR)

    # Inexistent account
    res_acc = runner.invoke(app, ["fin", "expense", "10", "Teste", "-a", "conta-inexistente"])
    assert res_acc.exit_code == int(ExitCode.NOT_FOUND)

    # Inexistent category
    res_cat = runner.invoke(
        app, ["fin", "expense", "10", "Teste", "-a", "itau", "-c", "categoria-fantasma"]
    )
    assert res_cat.exit_code == int(ExitCode.NOT_FOUND)
