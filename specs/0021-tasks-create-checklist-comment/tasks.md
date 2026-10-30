---
name: tasks
description: Decomposição e gates da feature 0021-tasks-create-checklist-comment.
alwaysApply: false
---

# Tasks — Criação de Tarefas, Checklist e Comentários (`neo tasks`)

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Adicionar modelos DTOs `ShortcutTask` e `ShortcutComment` e atualizar `ShortcutStory` em `shortcut_models.py` | AC-1, AC-2, AC-3, AC-4, AC-5 | — | `uv run pytest tests/unit/test_shortcut_client.py -v` | done |
| 2 | Implementar métodos `create_story`, `create_task`, `update_task` e `create_comment` em `ShortcutClient` (`src/neo/integrations/shortcut.py`) | AC-1, AC-2, AC-3, AC-4 | 1 | `uv run pytest tests/unit/test_shortcut_client.py -v` | done |
| 3 | Implementar subcomando `neo tasks create` com resolução de última iteração e owner padrão em `src/neo/commands/tasks.py` | AC-1 | 2 | `uv run pytest tests/e2e/test_tasks_create.py -v` | done |
| 4 | Implementar subcomandos `neo tasks check` (`add`, `complete`/`done`, `uncomplete`/`undone`) e `neo tasks comment` (`add`) em `src/neo/commands/tasks.py`, e enriquecer `neo tasks show` | AC-2, AC-3, AC-4, AC-5 | 2, 3 | `uv run pytest tests/e2e/test_tasks_check_comment.py -v` | done |
| 5 | Documentação (`docs/cli/tasks.md` / `docs/cli/tasks/`), testes de paridade e validação da esteira | AC-1, AC-2, AC-3, AC-4, AC-5 | 3, 4 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src && node scripts/audit-esteira.mjs .` | done |

## Plano de Teste
- **Unidade (`tests/unit/test_shortcut_client.py`):**
  - Criação de story com `create_story` (com e sem iteration_id / owner_ids).
  - Adição de task (checklist item) com `create_task`.
  - Atualização de task com `update_task(complete=True/False)`.
  - Adição de comentário com `create_comment`.
- **Aceite CLI (`tests/e2e/test_tasks_create.py`):**
  - Criação com defaults (associação à última iteração e usuário `me`).
  - Criação com `--iteration none` e `--owner none`.
  - Criação com `--json`.
- **Aceite CLI (`tests/e2e/test_tasks_check_comment.py`):**
  - Adição de checkitem (`neo tasks check add`).
  - Conclusão (`neo tasks check complete` e alias `done`).
  - Reabertura (`neo tasks check uncomplete` e alias `undone`).
  - Adição de comentário (`neo tasks comment add`).
  - Visualização de checklist e comentários em `neo tasks show`.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

## Checklist de Definition of Done
- [x] Todos os AC verdes **pelo gate executável** (não por inspeção)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] ADRs de decisões difíceis de reverter registrados (se aplicável)
- [x] Glossário / context-map atualizados se mudaram
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado (próximo passo / decisões)
