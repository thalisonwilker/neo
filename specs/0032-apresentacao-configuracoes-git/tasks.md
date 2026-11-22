---
name: tasks
description: Plano e gates da apresentação das configurações Git.
alwaysApply: false
---

# Tasks — Apresentação das configurações Git

> Status: implementado e validado. Contrato: [spec.md](spec.md).

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Criar componente visual separado e integrá-lo à saída humana de `neo git config show`; manter JSON existente | AC-1, AC-2, AC-3 | — | `uv run pytest tests/e2e/test_git_config_show.py -v` | done |
| 2 | Cobrir campos, estados, cores, texto literal, credenciais e compatibilidade JSON com testes de aceite | AC-1, AC-2, AC-3 | 1 | `uv run pytest tests/e2e/test_git_config_show.py -v` | done |
| 3 | Atualizar documentação e testes existentes afetados pela apresentação | AC-1, AC-2, AC-3 | 1 | `uv run pytest tests/unit/test_docs_parity.py tests/e2e/test_config_flow.py -v && uv run mkdocs build --strict` | done |
| 4 | Executar gates completos e atualizar o estado da feature | AC-1, AC-2, AC-3 | 1, 2, 3 | `uv run pytest --cov=neo --cov-report=term-missing --cov-fail-under=80 && uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run mkdocs build --strict && node scripts/audit-esteira.mjs .` | done |

## Plano de teste

- Aceite: um teste rastreável por AC; verificar combinações da matriz, estilos Rich, dados com caracteres de marcação, ausência de contexto e credencial, e opções JSON local e global.
- Regressão: suíte completa, paridade da documentação e gates de qualidade do projeto.
- Integração: nenhuma integração externa nova; respostas e credenciais simuladas nos testes.

## Divergências (SPEC_DEVIATION)

Nenhuma identificada.

## Checklist de Definition of Done

- [x] Todos os AC verdes pelo gate executável.
- [ ] Cobertura mínima atingida (87,44%); anexar relatório ao PR.
- [x] Ruff e Mypy e demais gates configurados aprovados; complexidade e SAST não têm comandos configurados.
- [x] Nenhum `SPEC_DEVIATION` pendente.
- [x] Glossário, context-map e ADRs: nenhuma alteração aplicável.
- [x] Spec reflete o que foi construído.
- [x] `docs/STATE.md` atualizado.

## Rastreabilidade de aceite

- AC-1: `test_AC_1_fields_and_default_branch` e `test_AC_2_git_config_set_get_show_unset`.
- AC-2: `test_AC_2_configured_fields_and_colors`, `test_AC_2_unconfigured_fields_and_colors` e `test_AC_1_fields_and_default_branch`.
- AC-3: `test_AC_3_json_compatibility_and_secret` e `test_AC_3_git_config_api_key_status_and_unset`.
