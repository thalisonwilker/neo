---
name: tasks
description: Decomposição e gates da feature 0012-filtro-iteracao-tasks.
alwaysApply: false
---

# Tasks — Filtro por Iteração em Tasks (`neo tasks`)

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Modelar `ShortcutIteration` e adicionar `iteration_id` a `ShortcutStory` em `shortcut_models.py`; implementar `list_iterations()`, `get_latest_iteration()` e `resolve_iteration()` em `ShortcutClient` (`GET /api/v3/iterations`) | AC-1, AC-2, AC-3, AC-4 | — | `uv run pytest tests/unit/test_shortcut_client.py -v` | done |
| 2 | Adicionar subcomando `neo tasks iterations` e opção `--iteration / -i` (padrão = última iteração) em `neo tasks list` e `neo tasks resume` em `commands/tasks.py` | AC-1, AC-2, AC-3, AC-4 | 1 | `uv run pytest tests/e2e/test_tasks_iterations.py tests/e2e/test_tasks_resume.py tests/e2e/test_tasks_commands.py -v` | done |
| 3 | Atualizar documentação (`README.md`, `docs/cli/tasks.md`, `docs/cli/index.md`, `docs/STATE.md`) e validar todos os quality gates | AC-1, AC-2, AC-3, AC-4 | 2 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src && node scripts/audit-esteira.mjs .` | done |

## Plano de teste
- **Unidade (`tests/unit/test_shortcut_client.py`):**
  - Parsing de `ShortcutIteration`, ordenação da última iteração (`get_latest_iteration`) e resolução por ID, nome exato e substring (`resolve_iteration`).
- **Aceite CLI (`tests/e2e/test_tasks_iterations.py`):**
  - `test_AC_1_tasks_iterations_list`: valida `neo tasks iterations` em modo Rich e `--json`, destacando a última iteração com `[● Atual]`.
  - `test_AC_2_default_latest_iteration_in_list_and_resume`: verifica que `neo tasks list` e `neo tasks resume` sem `-i` filtram automaticamente pelas tasks da última iteração (`Sprint 72`).
  - `test_AC_3_explicit_iteration_filter_and_not_found`: valida `-i "Sprint 71"`, `-i 71`, `-i all` e erro código `1` quando a iteração não existe.
  - `test_AC_4_iteration_badge_in_resume_cards`: verifica a presença do `iteration_id` e do badge `🔄 Sprint ...` nos cards do `neo tasks resume`.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

## Checklist de Definition of Done
- [x] Todos os AC verdes **pelo gate executável** (não por inspeção)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] ADRs de decisões difíceis de reverter registrados
- [x] Glossário / context-map atualizados se mudaram
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado (próximo passo / decisões)

