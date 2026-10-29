"""Testes unitários para o serviço de domínio financeiro (neo fin)."""

from __future__ import annotations

from pathlib import Path

import pytest

from neo.services.finance import (
    AccountInUseError,
    AccountNotFoundError,
    CategoryInUseError,
    CategoryNotFoundError,
    DuplicateEntityError,
    FinanceService,
)


@pytest.fixture
def service(tmp_path: Path) -> FinanceService:
    db_file = tmp_path / "test_finance.db"
    return FinanceService(db_path=db_file)


def test_account_crud(service: FinanceService) -> None:
    # 1. Create account
    acc = service.create_account(
        slug="nubank", name="Nubank Conta", account_type="checking", initial_balance=1000.0
    )
    assert acc.slug == "nubank"
    assert acc.name == "Nubank Conta"
    assert acc.initial_balance == 1000.0
    assert acc.current_balance == 1000.0

    # Duplicate creation fails
    with pytest.raises(DuplicateEntityError):
        service.create_account(slug="nubank", name="Outro Nubank")

    # 2. Get account
    found = service.get_account("nubank")
    assert found.slug == "nubank"

    with pytest.raises(AccountNotFoundError):
        service.get_account("inexistente")

    # 3. List accounts
    service.create_account(slug="inter", name="Banco Inter", initial_balance=500.0)
    accounts = service.list_accounts()
    assert len(accounts) == 2

    # 4. Update account
    updated = service.update_account(slug="nubank", name="Nubank Principal", account_type="savings")
    assert updated.name == "Nubank Principal"
    assert updated.account_type == "savings"

    # 5. Delete account
    service.delete_account("inter")
    assert len(service.list_accounts()) == 1


def test_category_crud(service: FinanceService) -> None:
    # Categories are seeded
    initial_categories = service.list_categories()
    assert len(initial_categories) >= 10

    # Create new custom category
    cat = service.create_category(slug="jogos", name="Jogos e Games", category_type="expense")
    assert cat.slug == "jogos"
    assert cat.category_type == "expense"

    # Duplicate in same type fails
    with pytest.raises(DuplicateEntityError):
        service.create_category(slug="jogos", name="Jogos Repetidos", category_type="expense")

    # Filter categories by type
    expenses = service.list_categories(category_type="expense")
    incomes = service.list_categories(category_type="income")
    assert all(c.category_type == "expense" for c in expenses)
    assert all(c.category_type == "income" for c in incomes)

    # Delete category
    service.delete_category("jogos", category_type="expense")
    with pytest.raises(CategoryNotFoundError):
        service.get_category("jogos", category_type="expense")


def test_transaction_crud_and_balance_recalculation(service: FinanceService) -> None:
    service.create_account(slug="carteira", name="Carteira Dinheiro", initial_balance=200.0)

    # 1. Add expense
    tx1 = service.create_transaction(
        amount=50.0,
        description="Almoço",
        transaction_type="expense",
        account_slug="carteira",
        category_slug="alimentacao",
        date_str="2026-10-15",
    )
    assert tx1.id > 0
    assert tx1.amount == 50.0
    assert tx1.transaction_type == "expense"

    acc = service.get_account("carteira")
    assert acc.current_balance == 150.0  # 200 - 50

    # 2. Add income
    tx2 = service.create_transaction(
        amount=100.0,
        description="Venda usada",
        transaction_type="income",
        account_slug="carteira",
        category_slug="outros",
        date_str="2026-10-16",
    )
    assert tx2.id > 0

    acc = service.get_account("carteira")
    assert acc.current_balance == 250.0  # 150 + 100

    # 3. List transactions with filters
    all_txs = service.list_transactions()
    assert len(all_txs) == 2

    filtered_month = service.list_transactions(month="2026-10")
    assert len(filtered_month) == 2

    empty_month = service.list_transactions(month="2026-09")
    assert len(empty_month) == 0

    # 4. Account cannot be deleted when it has transactions
    with pytest.raises(AccountInUseError):
        service.delete_account("carteira")

    # Category cannot be deleted when it has transactions
    with pytest.raises(CategoryInUseError):
        service.delete_category("alimentacao", category_type="expense")

    # 5. Update transaction
    updated_tx = service.update_transaction(tx1.id, amount=70.0, description="Almoço executivo")
    assert updated_tx.amount == 70.0
    assert updated_tx.description == "Almoço executivo"

    acc = service.get_account("carteira")
    assert acc.current_balance == 230.0  # 200 - 70 + 100

    # 6. Delete transaction and verify balance restored
    service.delete_transaction(tx1.id)
    acc = service.get_account("carteira")
    assert acc.current_balance == 300.0  # 200 + 100


def test_transaction_validations(service: FinanceService) -> None:
    service.create_account(slug="padrao", name="Conta Padrão", initial_balance=0.0)

    # Negative or zero amount
    with pytest.raises(ValueError, match="maior que zero"):
        service.create_transaction(amount=0.0, description="Inválido", transaction_type="expense")

    with pytest.raises(ValueError, match="maior que zero"):
        service.create_transaction(amount=-10.0, description="Inválido", transaction_type="expense")

    # Invalid date
    with pytest.raises(ValueError, match="Formato de data inválido"):
        service.create_transaction(
            amount=10.0,
            description="Data errada",
            transaction_type="expense",
            date_str="29-10-2026",
        )


def test_summaries_and_balance(service: FinanceService) -> None:
    service.create_account(slug="banco1", name="Banco 1", initial_balance=1000.0)
    service.create_account(slug="banco2", name="Banco 2", initial_balance=500.0)

    service.create_transaction(
        amount=200.0,
        description="Supermercado",
        transaction_type="expense",
        account_slug="banco1",
        category_slug="alimentacao",
        date_str="2026-10-05",
    )
    service.create_transaction(
        amount=100.0,
        description="Combustível",
        transaction_type="expense",
        account_slug="banco1",
        category_slug="transporte",
        date_str="2026-10-10",
    )
    service.create_transaction(
        amount=3000.0,
        description="Salário",
        transaction_type="income",
        account_slug="banco2",
        category_slug="salario",
        date_str="2026-10-01",
    )

    # Balance Summary
    balance = service.get_balance_summary()
    assert balance.total_initial == 1500.0
    assert balance.total_income == 3000.0
    assert balance.total_expense == 300.0
    assert balance.total_current == 4200.0  # 1500 + 3000 - 300

    # Monthly Summary
    monthly = service.get_monthly_summary("2026-10")
    assert monthly.month == "2026-10"
    assert monthly.total_income == 3000.0
    assert monthly.total_expense == 300.0
    assert monthly.net_balance == 2700.0
    assert len(monthly.expenses_by_category) == 2

    # Alimentação is 200 / 300 = ~66.67%
    alim = next(c for c in monthly.expenses_by_category if c.category_slug == "alimentacao")
    assert alim.total == 200.0
    assert round(alim.percentage, 1) == 66.7
