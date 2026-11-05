"""Composição do serviço financeiro."""

from neo.services.finance import (
    FinanceService,
)


def _get_service() -> FinanceService:
    return FinanceService()
