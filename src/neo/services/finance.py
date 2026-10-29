"""Serviço de domínio para micro gerenciamento financeiro pessoal."""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Literal

from neo.integrations.finance_db import get_db_connection

logger = logging.getLogger(__name__)

AccountType = Literal["checking", "savings", "investment", "credit", "cash", "other"]
TransactionType = Literal["expense", "income"]


class FinanceError(Exception):
    """Exceção base para operações financeiras."""


class AccountNotFoundError(FinanceError):
    """Conta bancária não encontrada."""


class CategoryNotFoundError(FinanceError):
    """Categoria não encontrada."""


class TransactionNotFoundError(FinanceError):
    """Transação não encontrada."""


class AccountInUseError(FinanceError):
    """Conta possui transações vinculadas e não pode ser removida."""


class CategoryInUseError(FinanceError):
    """Categoria possui transações vinculadas e não pode ser removida."""


class DuplicateEntityError(FinanceError):
    """Entidade já existente com mesmo identificador."""


@dataclass
class Account:
    id: int
    slug: str
    name: str
    account_type: str
    initial_balance: float
    current_balance: float
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "account_type": self.account_type,
            "initial_balance": self.initial_balance,
            "current_balance": self.current_balance,
            "created_at": self.created_at,
        }


@dataclass
class Category:
    id: int
    slug: str
    name: str
    category_type: str
    is_default: bool
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "category_type": self.category_type,
            "is_default": self.is_default,
            "created_at": self.created_at,
        }


@dataclass
class Transaction:
    id: int
    account_id: int
    category_id: int
    transaction_type: str
    amount: float
    description: str
    date: str
    created_at: str
    account_slug: str | None = None
    account_name: str | None = None
    category_slug: str | None = None
    category_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "account_id": self.account_id,
            "category_id": self.category_id,
            "account_slug": self.account_slug,
            "account_name": self.account_name,
            "category_slug": self.category_slug,
            "category_name": self.category_name,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "description": self.description,
            "date": self.date,
            "created_at": self.created_at,
        }


@dataclass
class CategoryTotal:
    category_slug: str
    category_name: str
    total: float
    percentage: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "category_slug": self.category_slug,
            "category_name": self.category_name,
            "total": self.total,
            "percentage": self.percentage,
        }


@dataclass
class MonthlySummary:
    month: str
    total_income: float
    total_expense: float
    net_balance: float
    expenses_by_category: list[CategoryTotal]

    def to_dict(self) -> dict[str, Any]:
        return {
            "month": self.month,
            "total_income": self.total_income,
            "total_expense": self.total_expense,
            "net_balance": self.net_balance,
            "expenses_by_category": [c.to_dict() for c in self.expenses_by_category],
        }


@dataclass
class BalanceSummary:
    accounts: list[Account]
    total_initial: float
    total_income: float
    total_expense: float
    total_current: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "accounts": [a.to_dict() for a in self.accounts],
            "total_initial": self.total_initial,
            "total_income": self.total_income,
            "total_expense": self.total_expense,
            "total_current": self.total_current,
        }


class FinanceService:
    """Serviço para gerenciar contas, categorias, transações e resumos financeiros."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path

    # -------------------------------------------------------------------------
    # Contas / Bancos
    # -------------------------------------------------------------------------

    def create_account(
        self,
        slug: str,
        name: str,
        account_type: str = "checking",
        initial_balance: float = 0.0,
    ) -> Account:
        """Cadastra uma nova conta bancária ou carteira."""
        clean_slug = slug.strip().lower()
        now = datetime.now(UTC).isoformat()

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO accounts (slug, name, account_type, initial_balance, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (clean_slug, name.strip(), account_type, float(initial_balance), now),
                )
                account_id = cursor.lastrowid
                conn.commit()
            except sqlite3.IntegrityError as err:
                raise DuplicateEntityError(
                    f"Conta com identificador '{clean_slug}' já existe."
                ) from err

        assert account_id is not None
        return Account(
            id=account_id,
            slug=clean_slug,
            name=name.strip(),
            account_type=account_type,
            initial_balance=float(initial_balance),
            current_balance=float(initial_balance),
            created_at=now,
        )

    def get_account(self, slug: str) -> Account:
        """Obtém uma conta pelo slug com saldo atual calculado."""
        clean_slug = slug.strip().lower()
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.id, a.slug, a.name, a.account_type, a.initial_balance, a.created_at,
                       COALESCE(SUM(CASE WHEN t.transaction_type = 'income' THEN t.amount
                                         WHEN t.transaction_type = 'expense' THEN -t.amount
                                         ELSE 0 END), 0) AS tx_delta
                FROM accounts a
                LEFT JOIN transactions t ON a.id = t.account_id
                WHERE a.slug = ?
                GROUP BY a.id;
                """,
                (clean_slug,),
            )
            row = cursor.fetchone()
            if not row:
                raise AccountNotFoundError(f"Conta '{clean_slug}' não encontrada.")

            current_balance = round(row["initial_balance"] + row["tx_delta"], 2)
            return Account(
                id=row["id"],
                slug=row["slug"],
                name=row["name"],
                account_type=row["account_type"],
                initial_balance=round(row["initial_balance"], 2),
                current_balance=current_balance,
                created_at=row["created_at"],
            )

    def list_accounts(self) -> list[Account]:
        """Lista todas as contas com saldo atual calculado."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT a.id, a.slug, a.name, a.account_type, a.initial_balance, a.created_at,
                       COALESCE(SUM(CASE WHEN t.transaction_type = 'income' THEN t.amount
                                         WHEN t.transaction_type = 'expense' THEN -t.amount
                                         ELSE 0 END), 0) AS tx_delta
                FROM accounts a
                LEFT JOIN transactions t ON a.id = t.account_id
                GROUP BY a.id
                ORDER BY a.name ASC;
                """
            )
            rows = cursor.fetchall()
            return [
                Account(
                    id=row["id"],
                    slug=row["slug"],
                    name=row["name"],
                    account_type=row["account_type"],
                    initial_balance=round(row["initial_balance"], 2),
                    current_balance=round(row["initial_balance"] + row["tx_delta"], 2),
                    created_at=row["created_at"],
                )
                for row in rows
            ]

    def update_account(
        self,
        slug: str,
        name: str | None = None,
        account_type: str | None = None,
    ) -> Account:
        """Atualiza metadados de uma conta existente."""
        acc = self.get_account(slug)
        new_name = name.strip() if name else acc.name
        new_type = account_type.strip() if account_type else acc.account_type

        with get_db_connection(self.db_path) as conn:
            conn.execute(
                "UPDATE accounts SET name = ?, account_type = ? WHERE id = ?;",
                (new_name, new_type, acc.id),
            )
            conn.commit()

        return self.get_account(slug)

    def delete_account(self, slug: str) -> None:
        """Exclui uma conta caso não possua movimentações."""
        acc = self.get_account(slug)
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE account_id = ?;", (acc.id,))
            tx_count = cursor.fetchone()[0]
            if tx_count > 0:
                raise AccountInUseError(
                    f"A conta '{slug}' possui {tx_count} transações associadas e não pode ser removida."
                )

            cursor.execute("DELETE FROM accounts WHERE id = ?;", (acc.id,))
            conn.commit()

    # -------------------------------------------------------------------------
    # Categorias
    # -------------------------------------------------------------------------

    def create_category(self, slug: str, name: str, category_type: str) -> Category:
        """Cadastra uma nova categoria de despesa ou receita."""
        clean_slug = slug.strip().lower()
        if category_type not in ("expense", "income"):
            raise ValueError("O tipo de categoria deve ser 'expense' ou 'income'.")

        now = datetime.now(UTC).isoformat()
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO categories (slug, name, category_type, is_default, created_at)
                    VALUES (?, ?, ?, 0, ?)
                    """,
                    (clean_slug, name.strip(), category_type, now),
                )
                cat_id = cursor.lastrowid
                conn.commit()
            except sqlite3.IntegrityError as err:
                raise DuplicateEntityError(
                    f"Categoria '{clean_slug}' para o tipo '{category_type}' já existe."
                ) from err

        assert cat_id is not None
        return Category(
            id=cat_id,
            slug=clean_slug,
            name=name.strip(),
            category_type=category_type,
            is_default=False,
            created_at=now,
        )

    def get_category(self, slug: str, category_type: str | None = None) -> Category:
        """Busca uma categoria pelo slug e opcionalmente pelo tipo."""
        clean_slug = slug.strip().lower()
        query = "SELECT id, slug, name, category_type, is_default, created_at FROM categories WHERE slug = ?"
        params: list[Any] = [clean_slug]
        if category_type:
            query += " AND category_type = ?"
            params.append(category_type)

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if not row:
                tipo_msg = f" para o tipo '{category_type}'" if category_type else ""
                raise CategoryNotFoundError(f"Categoria '{clean_slug}'{tipo_msg} não encontrada.")

            return Category(
                id=row["id"],
                slug=row["slug"],
                name=row["name"],
                category_type=row["category_type"],
                is_default=bool(row["is_default"]),
                created_at=row["created_at"],
            )

    def list_categories(self, category_type: str | None = None) -> list[Category]:
        """Lista categorias cadastradas, opcionalmente filtradas por tipo."""
        query = "SELECT id, slug, name, category_type, is_default, created_at FROM categories"
        params: list[Any] = []
        if category_type:
            query += " WHERE category_type = ?"
            params.append(category_type)
        query += " ORDER BY category_type ASC, name ASC;"

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                Category(
                    id=row["id"],
                    slug=row["slug"],
                    name=row["name"],
                    category_type=row["category_type"],
                    is_default=bool(row["is_default"]),
                    created_at=row["created_at"],
                )
                for row in rows
            ]

    def delete_category(self, slug: str, category_type: str | None = None) -> None:
        """Exclui uma categoria caso não possua transações vinculadas."""
        cat = self.get_category(slug, category_type)
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ?;", (cat.id,))
            tx_count = cursor.fetchone()[0]
            if tx_count > 0:
                raise CategoryInUseError(
                    f"A categoria '{cat.slug}' possui {tx_count} transações associadas e não pode ser removida."
                )

            cursor.execute("DELETE FROM categories WHERE id = ?;", (cat.id,))
            conn.commit()

    # -------------------------------------------------------------------------
    # Transações
    # -------------------------------------------------------------------------

    def _resolve_account(self, account_slug: str | None) -> Account:
        """Resolve a conta para a transação ou seleciona conta padrão."""
        if account_slug:
            return self.get_account(account_slug)

        accounts = self.list_accounts()
        if not accounts:
            raise AccountNotFoundError(
                "Nenhuma conta cadastrada. Cadastre uma conta com 'neo fin bank add <slug> --name <nome>' primeiro."
            )
        return accounts[0]

    def _resolve_category(self, category_slug: str | None, transaction_type: str) -> Category:
        """Resolve a categoria para a transação ou seleciona categoria 'outros' padrão."""
        if category_slug:
            return self.get_category(category_slug, category_type=transaction_type)

        try:
            return self.get_category("outros", category_type=transaction_type)
        except CategoryNotFoundError:
            cats = self.list_categories(category_type=transaction_type)
            if not cats:
                raise CategoryNotFoundError(
                    f"Nenhuma categoria disponível para transações do tipo '{transaction_type}'."
                )
            return cats[0]

    def _validate_date(self, date_str: str | None) -> str:
        """Valida e formata data no formato YYYY-MM-DD."""
        if not date_str:
            return date.today().isoformat()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError as err:
            raise ValueError(
                "Formato de data inválido. Use o padrão ISO YYYY-MM-DD (ex: 2026-10-29)."
            ) from err

    def create_transaction(
        self,
        amount: float,
        description: str,
        transaction_type: str,
        account_slug: str | None = None,
        category_slug: str | None = None,
        date_str: str | None = None,
    ) -> Transaction:
        """Registra uma nova movimentação financeira (despesa ou receita)."""
        if amount <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        if transaction_type not in ("expense", "income"):
            raise ValueError("Tipo de transação deve ser 'expense' ou 'income'.")

        valid_date = self._validate_date(date_str)
        account = self._resolve_account(account_slug)
        category = self._resolve_category(category_slug, transaction_type)
        now = datetime.now(UTC).isoformat()

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transactions (account_id, category_id, transaction_type, amount, description, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account.id,
                    category.id,
                    transaction_type,
                    float(amount),
                    description.strip(),
                    valid_date,
                    now,
                ),
            )
            tx_id = cursor.lastrowid
            conn.commit()

        assert tx_id is not None
        return Transaction(
            id=tx_id,
            account_id=account.id,
            category_id=category.id,
            transaction_type=transaction_type,
            amount=round(float(amount), 2),
            description=description.strip(),
            date=valid_date,
            created_at=now,
            account_slug=account.slug,
            account_name=account.name,
            category_slug=category.slug,
            category_name=category.name,
        )

    def get_transaction(self, tx_id: int) -> Transaction:
        """Busca uma transação específica pelo ID."""
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT t.id, t.account_id, t.category_id, t.transaction_type, t.amount, t.description, t.date, t.created_at,
                       a.slug AS account_slug, a.name AS account_name,
                       c.slug AS category_slug, c.name AS category_name
                FROM transactions t
                JOIN accounts a ON t.account_id = a.id
                JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?;
                """,
                (tx_id,),
            )
            row = cursor.fetchone()
            if not row:
                raise TransactionNotFoundError(f"Transação com ID {tx_id} não encontrada.")

            return Transaction(
                id=row["id"],
                account_id=row["account_id"],
                category_id=row["category_id"],
                transaction_type=row["transaction_type"],
                amount=round(row["amount"], 2),
                description=row["description"],
                date=row["date"],
                created_at=row["created_at"],
                account_slug=row["account_slug"],
                account_name=row["account_name"],
                category_slug=row["category_slug"],
                category_name=row["category_name"],
            )

    def list_transactions(
        self,
        month: str | None = None,
        account_slug: str | None = None,
        category_slug: str | None = None,
        transaction_type: str | None = None,
        limit: int = 100,
    ) -> list[Transaction]:
        """Lista transações com filtros opcionais por mês, conta, categoria e tipo."""
        query = """
            SELECT t.id, t.account_id, t.category_id, t.transaction_type, t.amount, t.description, t.date, t.created_at,
                   a.slug AS account_slug, a.name AS account_name,
                   c.slug AS category_slug, c.name AS category_name
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params: list[Any] = []

        if month:
            query += " AND t.date LIKE ?"
            params.append(f"{month.strip()}%")

        if account_slug:
            query += " AND a.slug = ?"
            params.append(account_slug.strip().lower())

        if category_slug:
            query += " AND c.slug = ?"
            params.append(category_slug.strip().lower())

        if transaction_type:
            query += " AND t.transaction_type = ?"
            params.append(transaction_type.strip().lower())

        query += " ORDER BY t.date DESC, t.id DESC LIMIT ?;"
        params.append(limit)

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [
                Transaction(
                    id=row["id"],
                    account_id=row["account_id"],
                    category_id=row["category_id"],
                    transaction_type=row["transaction_type"],
                    amount=round(row["amount"], 2),
                    description=row["description"],
                    date=row["date"],
                    created_at=row["created_at"],
                    account_slug=row["account_slug"],
                    account_name=row["account_name"],
                    category_slug=row["category_slug"],
                    category_name=row["category_name"],
                )
                for row in rows
            ]

    def update_transaction(
        self,
        tx_id: int,
        amount: float | None = None,
        description: str | None = None,
        date_str: str | None = None,
        account_slug: str | None = None,
        category_slug: str | None = None,
    ) -> Transaction:
        """Atualiza campos de uma transação existente."""
        current_tx = self.get_transaction(tx_id)

        new_amount = float(amount) if amount is not None else current_tx.amount
        if new_amount <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        new_desc = description.strip() if description is not None else current_tx.description
        new_date = self._validate_date(date_str) if date_str is not None else current_tx.date

        acc_id = current_tx.account_id
        if account_slug:
            acc = self.get_account(account_slug)
            acc_id = acc.id

        cat_id = current_tx.category_id
        if category_slug:
            cat = self.get_category(category_slug, category_type=current_tx.transaction_type)
            cat_id = cat.id

        with get_db_connection(self.db_path) as conn:
            conn.execute(
                """
                UPDATE transactions
                SET amount = ?, description = ?, date = ?, account_id = ?, category_id = ?
                WHERE id = ?;
                """,
                (new_amount, new_desc, new_date, acc_id, cat_id, tx_id),
            )
            conn.commit()

        return self.get_transaction(tx_id)

    def delete_transaction(self, tx_id: int) -> None:
        """Exclui uma transação existente."""
        # Check existence
        self.get_transaction(tx_id)

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?;", (tx_id,))
            conn.commit()

    # -------------------------------------------------------------------------
    # Balanço e Resumo
    # -------------------------------------------------------------------------

    def get_balance_summary(self) -> BalanceSummary:
        """Gera o balanço consolidado de todas as contas cadastradas."""
        accounts = self.list_accounts()
        total_initial = round(sum(a.initial_balance for a in accounts), 2)
        total_current = round(sum(a.current_balance for a in accounts), 2)

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
                    COALESCE(SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
                FROM transactions;
                """
            )
            row = cursor.fetchone()
            total_income = round(row["total_income"], 2)
            total_expense = round(row["total_expense"], 2)

        return BalanceSummary(
            accounts=accounts,
            total_initial=total_initial,
            total_income=total_income,
            total_expense=total_expense,
            total_current=total_current,
        )

    def get_monthly_summary(self, month: str | None = None) -> MonthlySummary:
        """Gera o resumo financeiro consolidado de um mês específico (YYYY-MM)."""
        target_month = month.strip() if month else date.today().strftime("%Y-%m")

        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END), 0) AS total_income,
                    COALESCE(SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END), 0) AS total_expense
                FROM transactions
                WHERE date LIKE ?;
                """,
                (f"{target_month}%",),
            )
            totals_row = cursor.fetchone()
            total_income = round(totals_row["total_income"], 2)
            total_expense = round(totals_row["total_expense"], 2)
            net_balance = round(total_income - total_expense, 2)

            # Detalhamento de despesas por categoria
            cursor.execute(
                """
                SELECT c.slug, c.name, SUM(t.amount) AS category_total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.transaction_type = 'expense' AND t.date LIKE ?
                GROUP BY c.id
                ORDER BY category_total DESC;
                """,
                (f"{target_month}%",),
            )
            cat_rows = cursor.fetchall()
            expenses_by_category: list[CategoryTotal] = []
            for row in cat_rows:
                cat_total = round(row["category_total"], 2)
                pct = round((cat_total / total_expense * 100), 2) if total_expense > 0 else 0.0
                expenses_by_category.append(
                    CategoryTotal(
                        category_slug=row["slug"],
                        category_name=row["name"],
                        total=cat_total,
                        percentage=pct,
                    )
                )

        return MonthlySummary(
            month=target_month,
            total_income=total_income,
            total_expense=total_expense,
            net_balance=net_balance,
            expenses_by_category=expenses_by_category,
        )
