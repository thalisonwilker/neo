"""Testes E2E para comandos de balanço e resumo mensal (`neo fin balance` e `neo fin summary`)."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_file = tmp_path / "finance_summary_test.db"
    monkeypatch.setenv("NEO_FINANCE_DB", str(db_file))


def test_balance_and_summary_commands() -> None:
    # 1. Setup accounts
    runner.invoke(
        app,
        ["fin", "bank", "add", "nubank", "--name", "Nubank", "--balance", "1000.0"],
    )
    runner.invoke(
        app,
        ["fin", "bank", "add", "inter", "--name", "Inter", "--balance", "500.0"],
    )

    # 2. Add transactions
    runner.invoke(
        app,
        [
            "fin",
            "expense",
            "200.0",
            "Compras de supermercado",
            "-a",
            "nubank",
            "-c",
            "alimentacao",
            "-d",
            "2026-10-10",
        ],
    )
    runner.invoke(
        app,
        ["fin", "expense", "100.0", "Uber", "-a", "inter", "-c", "transporte", "-d", "2026-10-12"],
    )
    runner.invoke(
        app,
        [
            "fin",
            "income",
            "4000.0",
            "Salário Dev",
            "-a",
            "nubank",
            "-c",
            "salario",
            "-d",
            "2026-10-01",
        ],
    )

    # 3. Test `neo fin balance`
    res_bal = runner.invoke(app, ["fin", "balance"])
    assert res_bal.exit_code == int(ExitCode.SUCCESS)
    assert "Balanço Consolidado" in res_bal.output
    assert "Nubank" in res_bal.output
    assert "Inter" in res_bal.output

    # Test `neo fin balance --json`
    res_bal_json = runner.invoke(app, ["fin", "balance", "--json"])
    assert res_bal_json.exit_code == int(ExitCode.SUCCESS)
    bal_data = json.loads(res_bal_json.output)
    assert bal_data["total_initial"] == 1500.0
    assert bal_data["total_income"] == 4000.0
    assert bal_data["total_expense"] == 300.0
    assert bal_data["total_current"] == 5200.0  # 1500 + 4000 - 300
    assert len(bal_data["accounts"]) == 2

    # 4. Test `neo fin summary`
    res_sum = runner.invoke(app, ["fin", "summary", "--month", "2026-10"])
    assert res_sum.exit_code == int(ExitCode.SUCCESS)
    assert "Resumo Mensal" in res_sum.output
    assert "Receitas" in res_sum.output
    assert "Despesas" in res_sum.output

    # Test `neo fin summary --json`
    res_sum_json = runner.invoke(app, ["fin", "summary", "--month", "2026-10", "--json"])
    assert res_sum_json.exit_code == int(ExitCode.SUCCESS)
    sum_data = json.loads(res_sum_json.output)
    assert sum_data["month"] == "2026-10"
    assert sum_data["total_income"] == 4000.0
    assert sum_data["total_expense"] == 300.0
    assert sum_data["net_balance"] == 3700.0
    assert len(sum_data["expenses_by_category"]) == 2
