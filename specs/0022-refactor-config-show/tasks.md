---
name: tasks
description: Decomposição e gates da feature 0022-refactor-config-show.
alwaysApply: false
---

# Tasks — Refatoração do Comando `neo config show`

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Implementar resolução de contexto de Git (status, provider, workspace, branch, task_id) e Tasks (status, provider, workspace, todo_list, current_task com checklist) em `src/neo/commands/config.py` | AC-1, AC-2, AC-3, AC-4, AC-5 | — | `uv run pytest tests/e2e/test_config_flow.py -v` | done |
| 2 | Refatorar a saída visual (Rich) de `neo config show` com as 4 tabelas (`Git`, `Tasks`, `Agents`, `Serviços configurados`) e o payload `--json` unificado | AC-1, AC-2, AC-3, AC-4, AC-5 | 1 | `uv run pytest tests/e2e/test_config_flow.py -v` | done |
| 3 | Atualizar documentação (`docs/cli/index.md`, `README.md`, `docs/STATE.md`), testes de paridade e validação da esteira SDD | AC-1, AC-2, AC-3, AC-4, AC-5 | 2 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src && node scripts/audit-esteira.mjs .` | done |

## Plano de Teste
- **Aceite CLI (`tests/e2e/test_config_flow.py`):**
  - Validação das 4 tabelas na saída visual (`Git`, `Tasks`, `Agents`, `Serviços configurados`).
  - Filtragem para exibir somente serviços com token configurado.
  - Formatação multilinhas da coluna `To-Do-List` (A fazer, Fazendo, Feito).
  - Identificação de `Tasks` na branch e no bloco de tarefas com progresso de checklist.
  - Validação do schema da resposta com flag global `--json`.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

## Checklist de Definition of Done
- [x] Todos os AC verdes **pelo gate executável** (não por inspeção)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] ADRs de decisões difíceis de reverter registrados (se aplicável)
- [x] Glossário / context-map atualizados se mudaram
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado (próximo passo / decisões)
