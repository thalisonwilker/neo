---
name: tasks
description: Decomposição e gates da feature 0008-ci-cd-e-deploy-github-actions.
alwaysApply: false
---

# Tasks — CI/CD e Deploy com GitHub Actions

> Decomposição da implementação dos Quality Gates automatizados e Deploy no GitHub Pages via GitHub Actions.

## Plano de Implementação

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Ajustar `site_url` no `mkdocs.yml` para a URL canônica do GitHub Pages | AC-3 | — | `uv run --group docs mkdocs build --strict` | done |
| 2 | Criar workflow completo de CI e Deploy em `.github/workflows/ci.yml` | AC-1, AC-2, AC-4 | 1 | `node -e 'require("js-yaml").load(fs.readFileSync(".github/workflows/ci.yml"))'` | done |
| 3 | Criar testes automatizados em `tests/unit/test_ci_workflow.py` validando integridade, estágios e permissões | AC-1, AC-2, AC-3, AC-4 | 2 | `uv run pytest tests/unit/test_ci_workflow.py -v` | done |
| 4 | Atualizar `README.md` com instruções de ativação do GitHub Pages e badges de CI | AC-5 | 3 | `node scripts/audit-esteira.mjs && node scripts/eval-spec-fidelity.mjs` | done |

---

## Plano de Testes
- **Unidade / Automação:**
  - `tests/unit/test_ci_workflow.py`:
    - Verifica a existência e sintaxe YAML de `.github/workflows/ci.yml`.
    - Valida que os triggers incluem `push: branches: [main]` e `pull_request`.
    - Valida a presença de todos os jobs: `audit`, `quality` (lint + mypy + pytest com `--cov-fail-under=80`) e `deploy-docs`.
    - Valida que `deploy-docs` tem `needs: [quality, audit]` e usa `actions/deploy-pages@v4`.
    - Valida que `site_url` no `mkdocs.yml` aponta para o GitHub Pages.

---

## Divergências (SPEC_DEVIATION)
*(Nenhuma divergência identificada)*

---

## Checklist de Definition of Done
- [x] Todos os ACs verificados pelo gate executável de testes (`uv run pytest tests/unit/test_ci_workflow.py`)
- [x] Pipeline sintaticamente válida e validada com PyYAML
- [x] Cobertura de testes mantida $\ge 80\%$
- [x] Auditoria da esteira 100% OK (`node scripts/audit-esteira.mjs` e `node scripts/eval-spec-fidelity.mjs`)
- [x] Manual atualizado no `README.md` e `docs/STATE.md` atualizado
