"""Testes unitários de persistência e schema SQLite para o módulo financeiro."""

from __future__ import annotations

import sqlite3
import stat
from pathlib import Path

import pytest

from neo.integrations.finance_db import (
    DEFAULT_FINANCE_DB_FILE,
    get_db_connection,
    get_finance_db_path,
    init_finance_db,
)


def test_get_finance_db_path_precedence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # 1. Custom path
    custom = tmp_path / "custom.db"
    assert get_finance_db_path(custom) == custom

    # 2. Env var
    env_path = tmp_path / "from_env.db"
    monkeypatch.setenv("NEO_FINANCE_DB", str(env_path))
    assert get_finance_db_path() == env_path

    # 3. Default path
    monkeypatch.delenv("NEO_FINANCE_DB", raising=False)
    assert get_finance_db_path() == DEFAULT_FINANCE_DB_FILE


def test_init_finance_db_creates_file_and_tables(tmp_path: Path) -> None:
    db_file = tmp_path / "finance.db"
    assert not db_file.exists()

    conn = init_finance_db(db_file)
    conn.close()

    assert db_file.exists()

    # Permissions on POSIX (0600)
    file_stat = db_file.stat()
    file_mode = stat.S_IMODE(file_stat.st_mode)
    assert file_mode == 0o600

    # Verify tables
    with get_db_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row[0] for row in cursor.fetchall()}
        assert "accounts" in tables
        assert "categories" in tables
        assert "transactions" in tables


def test_init_finance_db_seeds_default_categories(tmp_path: Path) -> None:
    db_file = tmp_path / "finance.db"
    init_finance_db(db_file).close()

    with get_db_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT slug, name, category_type, is_default FROM categories ORDER BY id;")
        categories = cursor.fetchall()
        assert len(categories) >= 10

        expense_slugs = {row["slug"] for row in categories if row["category_type"] == "expense"}
        income_slugs = {row["slug"] for row in categories if row["category_type"] == "income"}

        assert "alimentacao" in expense_slugs
        assert "moradia" in expense_slugs
        assert "transporte" in expense_slugs
        assert "salario" in income_slugs
        assert "freelance" in income_slugs


def test_init_finance_db_idempotent(tmp_path: Path) -> None:
    db_file = tmp_path / "finance.db"
    conn1 = init_finance_db(db_file)
    conn1.close()

    conn2 = init_finance_db(db_file)
    conn2.close()

    with get_db_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories;")
        count = cursor.fetchone()[0]
        # Shouldn't duplicate
        assert count == 11


def test_foreign_keys_enforced(tmp_path: Path) -> None:
    db_file = tmp_path / "finance.db"
    init_finance_db(db_file).close()

    with get_db_connection(db_file) as conn:
        cursor = conn.cursor()
        # Inserting a transaction without account should fail
        with pytest.raises(sqlite3.IntegrityError):
            cursor.execute(
                """
                INSERT INTO transactions (account_id, category_id, transaction_type, amount, description, date, created_at)
                VALUES (999, 1, 'expense', 50.0, 'Teste', '2026-10-29', '2026-10-29T12:00:00Z')
                """
            )
