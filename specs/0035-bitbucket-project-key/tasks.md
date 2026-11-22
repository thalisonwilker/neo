---
name: tasks
description: Decomposição e gates da feature 0035 (Key do projeto Bitbucket).
alwaysApply: false
---

# Tasks — Uso da Key do Projeto Bitbucket

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e tem um gate executável.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Atualizar modelo `GitProject` e parsing em `BitbucketClient.list_projects` para usar `key` | AC-4 | — | `uv run pytest tests/unit/test_bitbucket_client.py -v` | done |
| 2 | Ajustar prompt interativo e persistência em `neo git config set workspace` para exibir e salvar `project.key` | AC-1, AC-5 | 1 | `uv run pytest tests/e2e/test_bitbucket_projects.py -k "AC_1 or AC_2" -v` | done |
| 3 | Ajustar e validar criação de repositório com `key` e visualização em `neo git config show` | AC-2, AC-3 | 1, 2 | `uv run pytest tests/e2e/test_bitbucket_projects.py -v` | done |
| 4 | Atualizar documentação e suíte completa de testes e linters | AC-1, AC-2, AC-3, AC-4, AC-5 | 3 | `uv run pytest tests/unit tests/e2e -v && uv run ruff check . && uv run mypy src` | done |

## Plano de teste

- **Unidade:**
  - `tests/unit/test_bitbucket_client.py`: testar parsing de projetos com `key` e erro quando `key` for inválida ou ausente; testar criação de repositório enviando `{"project": {"key": "<KEY>"}}`.
- **Aceite (E2E):**
  - `tests/e2e/test_bitbucket_projects.py`: testar exibição de `Nome (KEY)`, persistência de `key` em `config.toml`, exibição em `neo git config show` e criação de repositório enviando a `key`.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência identificada.

## Checklist de Definition of Done

- [x] Todos os AC verdes pelo gate executável
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado
