---
name: tasks
description: Implementação e validação da remoção dos grupos Git auth e workspace.
alwaysApply: false
---

# Tasks — Remover grupos Git auth e workspace

| # | Task | Cobre AC | Depende de | Gate | Status |
|---|---|---|---|---|---|
| 1 | Remover grupos da CLI e preservar configuração Git | AC-1, AC-2 | — | `uv run pytest tests/e2e -v` | done |
| 2 | Atualizar testes de comandos removidos e configuração | AC-1, AC-2 | 1 | `uv run pytest tests/e2e tests/unit -v` | done |
| 3 | Atualizar README e documentação | AC-3 | 1 | `uv run mkdocs build --strict` | done |
| 4 | Executar gates e atualizar estado | AC-1, AC-2, AC-3 | 1–3 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src` | done |

## Testes e Definition of Done
- [x] ACs cobertos por testes e sem `SPEC_DEVIATION`.
- [x] Cobertura, Ruff, Mypy, documentação e auditoria aprovados.
- [x] `docs/STATE.md` atualizado.
- [ ] Anexar cobertura ao PR e definir gates de complexidade e SAST, ainda sem comandos configurados.
