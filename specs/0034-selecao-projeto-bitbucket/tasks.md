---
name: tasks
description: Tarefas e gates da seleção de projeto Bitbucket.
alwaysApply: false
---

# Tasks — Seleção de projeto Bitbucket

> Status: implementado e validado.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Consultar projetos Bitbucket com paginação e tratamento de erros; representar identificador e nome | AC-1, AC-2 | — | `uv run pytest tests/unit/test_bitbucket_client.py -v` | done |
| 2 | Selecionar projeto e persistir workspace e projeto de forma conjunta, preservando configuração anterior nas falhas | AC-1, AC-2, AC-5 | 1 | `uv run pytest tests/e2e/test_workspace_commands.py tests/e2e/test_bitbucket_projects.py -v` | done |
| 3 | Exibir projeto no config show somente para Bitbucket, em modos humano e JSON | AC-3, AC-5 | 2 | `uv run pytest tests/e2e/test_git_config_show.py tests/e2e/test_bitbucket_projects.py -v` | done |
| 4 | Usar projeto associado ao workspace na criação Bitbucket e rejeitar ausência ou incompatibilidade antes do remoto; remover projeto fixo | AC-4, AC-5 | 2 | `uv run pytest tests/e2e/test_git_repo_creation.py tests/e2e/test_bitbucket_projects.py tests/unit/test_bitbucket_client.py -v` | done |
| 5 | Atualizar documentação, executar gates de aceite, qualidade e auditoria e registrar resultado | AC-1, AC-2, AC-3, AC-4, AC-5 | 1, 2, 3, 4 | `uv run pytest --cov=neo --cov-report=term-missing --cov-fail-under=80 && uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run mkdocs build --strict && node scripts/audit-esteira.mjs .` | done |

## Plano de teste

- Unidade: paginação, modelos e parâmetros enviados à API Bitbucket, com HTTP simulado.
- Aceite: um ou mais testes por AC, incluindo seleção, cancelamento, falhas, JSON, GitHub e workspace divergente.
- Documentação: paridade e build estrito, sem chamadas reais às APIs.

## Rastreabilidade de aceite

| AC | Testes |
|---|---|
| AC-1 | `test_AC_1_project_selected_and_persisted`, `test_AC_1_projects_are_paginated_and_uuid_is_sent` |
| AC-2 | `test_AC_2_failures_preserve_previous_configuration`, `test_AC_2_write_failure_preserves_previous_configuration` |
| AC-3 | `test_AC_3_project_shown_only_for_bitbucket` |
| AC-4 | `test_AC_4_missing_or_mismatched_project_blocks_creation`, `test_AC_4_creation_sends_selected_project` |
| AC-5 | `test_AC_5_json_is_noninteractive_and_preserves_state`, testes existentes de GitHub |

## Divergências (SPEC_DEVIATION)

Nenhuma registrada.

## Checklist de Definition of Done

- [x] Todos os AC verdes pelo gate executável.
- [x] Nenhum `SPEC_DEVIATION` pendente.
- [x] ADRs registrados se houver decisões difíceis de reverter.
- [x] Glossário e context-map atualizados se mudarem.
- [x] Spec reflete o que foi construído.
- [x] `docs/STATE.md` atualizado.
