---
name: tasks
description: Tarefas e gates da criação e clonagem de repositório Git.
alwaysApply: false
---

# Tasks — Criação e clonagem de repositório Git

> Status: implementado e validado.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Implementar validação, criação remota e clone autenticado, com tratamento seguro de falhas | AC-1, AC-2, AC-5 | — | `uv run pytest tests/e2e/test_git_repo_creation.py -v` | done |
| 2 | Preparar branch e arquivos, criar commit, publicar, selecionar repositório e orientar `cd` | AC-3, AC-4, AC-5 | 1 | `uv run pytest tests/e2e/test_git_repo_creation.py -v` | done |
| 3 | Atualizar testes de aceite e regressão para o novo contrato e opções | AC-1, AC-2, AC-3, AC-4, AC-5 | 1, 2 | `uv run pytest tests/unit tests/e2e -v` | done |
| 4 | Atualizar documentação do comando e verificar paridade | AC-1, AC-2, AC-3, AC-4, AC-5 | 1, 2 | `uv run pytest tests/unit/test_docs_parity.py -v && uv run mkdocs build --strict` | done |
| 5 | Executar gates de qualidade, cobertura e auditoria; atualizar estado e rastreabilidade | AC-1, AC-2, AC-3, AC-4, AC-5 | 3, 4 | `uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest --cov=neo --cov-report=term-missing --cov-fail-under=80 && node scripts/audit-esteira.mjs .` | done |

## Plano de teste

- Aceite via CLI: cenários rastreáveis a cada AC, com Git local e provedor simulado, incluindo falhas e ordem das operações.
- Unidade e integração: autenticação e contratos de provedores, conforme as mudanças necessárias, sem chamadas externas reais.
- Documentação: paridade da CLI e build estrito.

## Rastreabilidade de aceite

| Critérios | Testes de aceite |
|---|---|
| AC-1, AC-2, AC-3, AC-4 | `test_AC_1_2_3_4_default_flow`, `test_AC_1_2_3_4_options` |
| AC-5 | `test_AC_5_validation_failure_before_remote`, `test_AC_5_existing_destination_and_invalid_branch`, `test_AC_5_push_failure_preserves_clone` |

## Divergências (SPEC_DEVIATION)

Nenhuma registrada.

## Checklist de Definition of Done

- [x] Todos os AC verdes pelo gate executável.
- [x] Nenhum `SPEC_DEVIATION` pendente.
- [x] ADRs registrados se houver decisões difíceis de reverter.
- [x] Glossário e context-map atualizados se mudarem.
- [x] Spec reflete o que foi construído.
- [x] `docs/STATE.md` atualizado.
