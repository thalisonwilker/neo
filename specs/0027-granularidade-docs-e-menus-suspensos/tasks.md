---
name: tasks
description: Decomposição e gates da feature de granularidade de documentação e menus suspensos.
alwaysApply: false
---

# Tasks — 0027 Granularidade da Documentação e Menus Suspensos

> Decomposição da implementação com gates executáveis.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Consolidar regra CSS global de menu suspenso/chevron em todos os níveis em `docs/stylesheets/extra.css` | AC-1 | — | `uv run --group docs mkdocs build --strict` | done |
| 2 | Decompor `neo git repo` em `docs/cli/git/repo/` (`index.md`, `list.md`, `remote-list.md`, `search.md`, `show.md`, `create.md`, `edit.md`) | AC-2 | 1 | `test -f docs/cli/git/repo/list.md && uv run --group docs mkdocs build --strict` | done |
| 3 | Decompor `neo git branch` em `docs/cli/git/branch/` (`index.md`, `list.md`, `create.md`, `delete.md`) `[P]` | AC-3 | 1 | `test -f docs/cli/git/branch/list.md && uv run --group docs mkdocs build --strict` | done |
| 4 | Decompor `neo git commits` em `docs/cli/git/commits/` (`index.md`, `list.md`, `search.md`, `show.md`) `[P]` | AC-3 | 1 | `test -f docs/cli/git/commits/list.md && uv run --group docs mkdocs build --strict` | done |
| 5 | Decompor `neo git pr` em `docs/cli/git/pr/` (`index.md`, `open.md`, `list.md`, `show.md`, `approve.md`, `decline.md`) `[P]` | AC-3 | 1 | `test -f docs/cli/git/pr/open.md && uv run --group docs mkdocs build --strict` | done |
| 6 | Atualizar `mkdocs.yml` (árvore `nav` com subitens e `redirect_maps` para caminhos legados) e corrigir links cruzados em `docs/` | AC-4, AC-5 | 2, 3, 4, 5 | `uv run --group docs mkdocs build --strict` | done |
| 7 | Atualizar testes de documentação (`test_docs_build.py` e `test_docs_parity.py`) para validar nova estrutura granular | AC-6 | 6 | `uv run pytest tests/unit/test_docs_build.py tests/unit/test_docs_parity.py -v` | done |

## Plano de Teste
- **Compilação estrita**: `uv run --group docs mkdocs build --strict` (sem links quebrados ou avisos).
- **Testes de documentação**: `uv run pytest tests/unit/test_docs_build.py tests/unit/test_docs_parity.py -v`.
- **Regressão geral**: `uv run pytest tests/unit -v` e `uv run pytest tests/e2e -v`.

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Documentação gerada detalhada (1 arquivo `.md` por ação)
- [x] Links legados redirecionados via `redirect_maps`
- [x] `docs/STATE.md` atualizado

