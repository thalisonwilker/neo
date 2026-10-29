---
name: tasks
description: Decomposição e gates da feature 0017 - Contexto Ativo e Config Show por Seções.
alwaysApply: false
---

# Tasks — 0017 Contexto Ativo de Trabalho e Config Show por Seções

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano
| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Implementar serviço de contexto ativo (`active_context.py`) com resolução de task por branch, persistência local e contagem de commits | AC-1, AC-2 | — | `uv run pytest tests/unit/test_active_context.py -v` | done |
| 2 | Adicionar subcomandos `neo tasks bind <id>` e `neo tasks unbind` em `tasks.py` | AC-1 | 1 | `uv run pytest tests/e2e/test_tasks_bind.py -v` | done |
| 3 | Reformular comando `neo config show` com painéis Rich modularizados (`GIT`, `TASKS`, `AGENT`) e payload estruturado em JSON | AC-3, AC-4, AC-5 | 1, 2 | `uv run pytest tests/e2e/test_config_show_sections.py -v` | done |
| 4 | Atualizar documentação MkDocs e testes de paridade | AC-6 | 3 | `uv run mkdocs build --strict && uv run pytest tests/unit/test_docs_parity.py -v` | done |
| 5 | Executar suíte completa de testes, auditoria da esteira e atualização do `docs/STATE.md` | AC-1 a AC-6 | 4 | `uv run pytest -v && node scripts/audit-esteira.mjs .` | done |

## Plano de teste
- Testes unitários para heurística de branch regex, persistência local e contagem de commits.
- Testes E2E via `CliRunner` validando saída Rich com seções `GIT`, `TASKS`, `AGENT` e saída `--json`.
- Validação estrita do MkDocs (`mkdocs build --strict`).

## Divergências (SPEC_DEVIATION)
*(Nenhuma identificada)*

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Spec e tasks atualizadas refletindo a entrega
- [x] `docs/STATE.md` atualizado
