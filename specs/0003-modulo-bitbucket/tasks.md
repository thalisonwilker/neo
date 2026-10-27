---
name: tasks
description: Decomposição e gates da feature 0003-modulo-bitbucket.
alwaysApply: false
---

# Tasks — 0003-modulo-bitbucket

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e tem um gate executável.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Implementar modelos de domínio e DTOs tipados (Pydantic) em `src/neo/integrations/bitbucket_models.py` | AC-1, AC-3, AC-5 | — | `uv run mypy src` | done |
| 2 | Implementar cliente de API HTTP em `src/neo/integrations/bitbucket.py` com paginação, busca e tratamento de erros | AC-1 a AC-6 | 1 | `uv run pytest tests/unit/test_bitbucket_client.py -v` | done |
| 3 | Implementar subcomando `neo repo` (`list`, `search`, `clone`, `create`) em `src/neo/commands/repo.py` | AC-1, AC-2, AC-3, AC-4, AC-6 | 2 | `uv run pytest tests/e2e/test_repo_commands.py -v` | done |
| 4 | Implementar subcomando `neo commits` (`search`) em `src/neo/commands/commits.py` | AC-5, AC-6 | 2 | `uv run pytest tests/e2e/test_commits_commands.py -v` | done |
| 5 | Registrar subcomandos no `src/neo/cli.py` e validação de qualidade estática e cobertura | AC-1 a AC-6 | 3, 4 | `uv run ruff check . && uv run mypy src && uv run pytest --cov=neo` | done |

## Plano de teste
- **Unidade:**
  - `tests/unit/test_bitbucket_client.py`: Testa chamadas à API REST mockadas com `respx` (listagem, busca, clone URLs, criação e commits), validação de modelos Pydantic e captura de erros HTTP (401, 404, 429).
- **Aceite (E2E):**
  - `tests/e2e/test_repo_commands.py`: Executa `neo repo list`, `search`, `clone`, `create` com `CliRunner`, verificando formatação Rich, flag `--json`, e exigência de credenciais.
  - `tests/e2e/test_commits_commands.py`: Executa `neo commits search` com filtros de autor e query em modos Rich e JSON.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência identificada.

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável (`uv run pytest tests/e2e`)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Análise estática limpa (`ruff check`, `mypy src`)
- [x] Cobertura de testes ≥ 80% (83.22% atingido)
- [x] `docs/STATE.md` atualizado

