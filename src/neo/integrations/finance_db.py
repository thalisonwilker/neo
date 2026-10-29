"""Adaptador de persistência SQLite e migrações para o módulo financeiro do Neo."""

from __future__ import annotations

import logging
import os
import sqlite3
import stat
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from neo.config import DEFAULT_CONFIG_DIR

logger = logging.getLogger(__name__)

DEFAULT_FINANCE_DB_FILE = DEFAULT_CONFIG_DIR / "finance.db"

DEFAULT_CATEGORIES: list[tuple[str, str, str]] = [
    # (slug, name, type)
    ("alimentacao", "Alimentação", "expense"),
    ("moradia", "Moradia", "expense"),
    ("transporte", "Transporte", "expense"),
    ("lazer", "Lazer", "expense"),
    ("saude", "Saúde", "expense"),
    ("educacao", "Educação", "expense"),
    ("outros", "Outros", "expense"),
    ("salario", "Salário", "income"),
    ("freelance", "Freelance", "income"),
    ("investimentos", "Investimentos", "income"),
    ("outros", "Outros", "income"),
]

SCHEMA_DDL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    account_type TEXT NOT NULL DEFAULT 'checking',
    initial_balance REAL NOT NULL DEFAULT 0.0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    category_type TEXT NOT NULL CHECK(category_type IN ('expense', 'income')),
    is_default INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE(slug, category_type)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('expense', 'income')),
    amount REAL NOT NULL CHECK(amount > 0),
    description TEXT NOT NULL,
    date TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_tx_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_tx_category ON transactions(category_id);
"""


def get_finance_db_path(custom_path: Path | None = None) -> Path:
    """Retorna o caminho do banco SQLite financeiro com base na precedência."""
    if custom_path is not None:
        return custom_path

    env_var = os.getenv("NEO_FINANCE_DB")
    if env_var:
        return Path(env_var)

    return DEFAULT_FINANCE_DB_FILE


def _set_restricted_permissions(path: Path) -> None:
    """Aplica permissão 0600 no arquivo de banco de dados no padrão POSIX."""
    try:
        if path.exists():
            path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError as err:
        logger.debug("Não foi possível ajustar permissões 0600 para %s: %s", path, err)


def init_finance_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Inicializa o banco SQLite financeiro aplicando DDL e seed inicial se vazio."""
    resolved_path = get_finance_db_path(db_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(resolved_path))
    conn.row_factory = sqlite3.Row

    _set_restricted_permissions(resolved_path)

    with conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.executescript(SCHEMA_DDL)

        # Checar se tabela de categorias está vazia
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories;")
        count = cursor.fetchone()[0]
        if count == 0:
            now = datetime.now(UTC).isoformat()
            cursor.executemany(
                """
                INSERT INTO categories (slug, name, category_type, is_default, created_at)
                VALUES (?, ?, ?, 1, ?)
                """,
                [(slug, name, cat_type, now) for slug, name, cat_type in DEFAULT_CATEGORIES],
            )

    return conn


@contextmanager
def get_db_connection(db_path: Path | None = None) -> Generator[sqlite3.Connection]:
    """Context manager que fornece uma conexão SQLite configurada."""
    conn = init_finance_db(db_path)
    try:
        yield conn
    finally:
        conn.close()
