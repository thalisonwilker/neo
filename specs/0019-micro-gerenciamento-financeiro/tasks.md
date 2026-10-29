---
name: tasks
description: Decomposição e gates da feature 0019-micro-gerenciamento-financeiro.
alwaysApply: false
---

# Tasks — 0019 Micro Gerenciamento Financeiro (`neo fin`)

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano de Implementação

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Implementar persistência e inicialização SQLite com esquema relacional, migrations DDL e seed de categorias em `src/neo/integrations/finance_db.py` | AC-1 | — | `uv run pytest tests/unit/test_finance_db.py -v` | done |
| 2 | Implementar serviço de domínio financeiro (`src/neo/services/finance.py`) cobrindo CRUD de contas, categorias, transações, validação de regras de negócio e cálculo de saldo e resumos | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7 | 1 | `uv run pytest tests/unit/test_finance_service.py -v` | done |
| 3 | Implementar comandos CLI `neo fin bank` e `neo fin category` (`src/neo/commands/finance.py`) com subcomandos add, list, edit, rm, suporte a `--json` e códigos de erro | AC-2, AC-3, AC-8 | 2 | `uv run pytest tests/e2e/test_finance_bank_and_category.py -v` | done |
| 4 | Implementar comandos CLI `neo fin tx` (add, list, edit, rm) e atalhos rápidos `neo fin expense` e `neo fin income` com filtros e colorização | AC-4, AC-5, AC-6, AC-8 | 3 | `uv run pytest tests/e2e/test_finance_transactions.py -v` | done |
| 5 | Implementar comandos de balanço e resumo `neo fin balance` e `neo fin summary` com detalhamento mensal e distribuição por categoria | AC-7, AC-8 | 4 | `uv run pytest tests/e2e/test_finance_summary.py -v` | done |
| 6 | Registrar `fin_app` no CLI principal (`src/neo/cli.py`) e atualizar documentação MkDocs (`docs/cli/fin/` e `mkdocs.yml`) com paridade estrita | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8 | 5 | `uv run pytest tests/unit/test_docs_parity.py -v && uv run --group docs mkdocs build --strict` | done |
| 7 | Executar suite completa de validação de qualidade, cobertura >= 80%, linting Ruff, Mypy estrito e scripts de auditoria SDD | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8 | 6 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run ruff format --check . && uv run mypy src && node scripts/audit-esteira.mjs . && node scripts/eval-spec-fidelity.mjs .` | done |

---

## Plano de Testes

- **Unidade (`tests/unit/`):**
  - `test_finance_db.py`: inicialização do banco SQLite, criação de tabelas, `PRAGMA foreign_keys = ON`, seed inicial de categorias (despesas e receitas), idempotência da migração e permissões de arquivo.
  - `test_finance_service.py`: CRUD de contas, verificação de duplicidade de slug, cálculo de saldo inicial + movimentações, bloqueio de remoção de conta com transações, CRUD de categorias, registro de despesas e receitas, filtros de transações por data/mês/conta/categoria, cálculo de balanço consolidado e resumo mensal por categoria.
- **Aceite E2E (`tests/e2e/`):**
  - `test_finance_bank_and_category.py`: comandos `neo fin bank (add|list|edit|rm)` e `neo fin category (add|list|rm)`, modo `--json`, validações de erro (código 2 para uso inválido, 4 para não encontrado, 1 para violação referencial).
  - `test_finance_transactions.py`: comandos `neo fin tx (add|list|edit|rm)` e atalhos rápidos `neo fin expense` e `neo fin income`, filtros por conta/categoria/mês, deleção com recálculo de saldo.
  - `test_finance_summary.py`: comandos `neo fin balance` e `neo fin summary [--month YYYY-MM]`, exibição tabular formatada e modo `--json`.

---

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

---

## Checklist de Definition of Done
- [x] Todos os 8 ACs verificados pelos gates executáveis de teste
- [x] Cobertura >= 80% (`uv run pytest --cov=neo --cov-fail-under=80`)
- [x] Análise estática limpa (`uv run ruff check .`, `uv run ruff format --check .` e `uv run mypy src`)
- [x] Nenhum SPEC_DEVIATION pendente sem resolução
- [x] Documentação MkDocs completa em `docs/cli/fin/` (`test_docs_parity.py` e `mkdocs build --strict` verdes)
- [x] Auditoria da esteira 100% OK (`node scripts/audit-esteira.mjs .` e `node scripts/eval-spec-fidelity.mjs .`)
- [x] `docs/STATE.md` atualizado
