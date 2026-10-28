---
name: tasks
description: Decomposição e gates da feature 0011-tasks-resume-board (`neo tasks resume`).
alwaysApply: false
---

# Tasks — Quadro Resumo de Tasks (`neo tasks resume`)

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Modelar `ShortcutWorkflow` e `ShortcutWorkflowState` em `shortcut_models.py` e implementar `list_workflows()` em `ShortcutClient` (`GET /api/v3/workflows`) | AC-1, AC-3 | — | `uv run pytest tests/unit/test_shortcut_client.py -v` | done |
| 2 | Implementar persistência do mapeamento de colunas por serviço (`get_task_columns_config` e `set_task_columns_config`) em `config.py` suportando 1 ou mais estados por coluna (`todo`, `doing`, `done`) | AC-1, AC-2 | — | `uv run pytest tests/unit/test_config.py -v` | done |
| 3 | Implementar assistente interativo de configuração de colunas, comando `neo tasks config columns` e comando `neo tasks resume` (com `--all`, `--limit`, `--configure` e `--json`) em `commands/tasks.py` | AC-1, AC-2, AC-3, AC-4 | 1, 2 | `uv run pytest tests/e2e/test_tasks_resume.py -v` | done |
| 4 | Atualizar documentação (`README.md`, `docs/cli/tasks.md`, `docs/cli/index.md`, `docs/STATE.md`) e validar todos os quality gates | AC-1, AC-2, AC-3, AC-4 | 3 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src && node scripts/audit-esteira.mjs .` | done |

## Plano de teste
- **Unidade (`tests/unit/`):**
  - Parsing de `ShortcutWorkflow` e `ShortcutWorkflowState` e chamada `GET /api/v3/workflows` com `respx`.
  - Leitura e gravação de `todo`, `doing`, `done` por serviço em `config.toml`.
- **Aceite CLI (`tests/e2e/test_tasks_resume.py`):**
  - `test_AC_1_resume_auto_configures_when_missing`: executa `neo tasks resume` sem colunas configuradas, seleciona múltiplas colunas no prompt interativo, verifica gravação no `config.toml` e renderização do quadro.
  - `test_AC_2_config_columns_command`: executa `neo tasks config columns` e `neo tasks resume --configure` atualizando as colunas.
  - `test_AC_3_resume_renders_kanban_mine_by_default`: verifica que apenas as stories do usuário logado aparecem distribuídas nas colunas `A fazer`, `Fazendo` e `Feito`.
  - `test_AC_4_resume_all_and_json_mode`: valida flag `--all` (todas as tasks do board) e saída estruturada com `--json`.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

## Checklist de Definition of Done
- [x] Todos os AC verdes **pelo gate executável** (não por inspeção)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] ADRs de decisões difíceis de reverter registrados
- [x] Glossário / context-map atualizados se mudaram
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado (próximo passo / decisões)

