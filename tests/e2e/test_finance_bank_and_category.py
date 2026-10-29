"""Testes E2E para gerenciamento de bancos e categorias (`neo fin bank` e `neo fin category`)."""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from neo.cli import app
from neo.config import ExitCode

runner = CliRunner()


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db_file = tmp_path / "finance_test.db"
    monkeypatch.setenv("NEO_FINANCE_DB", str(db_file))


def test_bank_lifecycle_and_json() -> None:
    # 1. Add bank
    res_add = runner.invoke(
        app,
        [
            "fin",
            "bank",
            "add",
            "nubank",
            "--name",
            "Nubank Principal",
            "--type",
            "checking",
            "--balance",
            "1250.50",
        ],
    )
    assert res_add.exit_code == int(ExitCode.SUCCESS)
    assert "Nubank Principal" in res_add.output

    # Duplicate bank fails with ExitCode.ERROR
    res_dup = runner.invoke(
        app,
        ["fin", "bank", "add", "nubank", "--name", "Outro Nubank"],
    )
    assert res_dup.exit_code == int(ExitCode.ERROR)

    # 2. List banks (JSON)
    res_list_json = runner.invoke(app, ["fin", "bank", "list", "--json"])
    assert res_list_json.exit_code == int(ExitCode.SUCCESS)
    data = json.loads(res_list_json.output)
    assert len(data) == 1
    assert data[0]["slug"] == "nubank"
    assert data[0]["initial_balance"] == 1250.50
    assert data[0]["current_balance"] == 1250.50

    # 3. Edit bank
    res_edit = runner.invoke(
        app,
        ["fin", "bank", "edit", "nubank", "--name", "Nubank PJ", "--type", "savings"],
    )
    assert res_edit.exit_code == int(ExitCode.SUCCESS)
    assert "Nubank PJ" in res_edit.output

    # Edit non-existent fails with NOT_FOUND
    res_edit_nf = runner.invoke(app, ["fin", "bank", "edit", "itau", "--name", "Itau"])
    assert res_edit_nf.exit_code == int(ExitCode.NOT_FOUND)

    # 4. Remove bank
    res_rm = runner.invoke(app, ["fin", "bank", "rm", "nubank"])
    assert res_rm.exit_code == int(ExitCode.SUCCESS)

    # Remove non-existent fails with NOT_FOUND
    res_rm_nf = runner.invoke(app, ["fin", "bank", "rm", "nubank"])
    assert res_rm_nf.exit_code == int(ExitCode.NOT_FOUND)


def test_category_lifecycle_and_json() -> None:
    # 1. List default categories
    res_list = runner.invoke(app, ["fin", "category", "list", "--type", "expense", "--json"])
    assert res_list.exit_code == int(ExitCode.SUCCESS)
    cats = json.loads(res_list.output)
    slugs = [c["slug"] for c in cats]
    assert "alimentacao" in slugs
    assert "transporte" in slugs

    # 2. Add custom category
    res_add = runner.invoke(
        app,
        ["fin", "category", "add", "games", "--name", "Jogos & Steam", "--type", "expense"],
    )
    assert res_add.exit_code == int(ExitCode.SUCCESS)

    # Duplicate category in same type fails
    res_dup = runner.invoke(
        app,
        ["fin", "category", "add", "games", "--name", "Jogos", "--type", "expense"],
    )
    assert res_dup.exit_code == int(ExitCode.ERROR)

    # Invalid type fails with USAGE_ERROR
    res_inv = runner.invoke(
        app,
        ["fin", "category", "add", "invalido", "--name", "Inv", "--type", "outro"],
    )
    assert res_inv.exit_code == int(ExitCode.USAGE_ERROR)

    # 3. Remove custom category
    res_rm = runner.invoke(app, ["fin", "category", "rm", "games", "--type", "expense"])
    assert res_rm.exit_code == int(ExitCode.SUCCESS)

    # Remove non-existent fails with NOT_FOUND
    res_rm_nf = runner.invoke(app, ["fin", "category", "rm", "games", "--type", "expense"])
    assert res_rm_nf.exit_code == int(ExitCode.NOT_FOUND)
