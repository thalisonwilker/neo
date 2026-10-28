---
name: tasks
description: Decomposição e gates da feature 0013-publicacao-pacote-pypi.
alwaysApply: false
---

# Tasks — Pacote PyPI (`neo-cmd`), Limpeza de Estrutura e Publicação via GitHub Actions

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Remover pastas e arquivos desnecessários (`.cursor`, `.windsurf`, `.spec-driven`, `.github/prompts`, `.github/copilot-instructions.md`, `specs/0001-exemplo-cota-de-uso`, `src/README.md`, `site/`, `.coverage`) e atualizar `docs/README.md` | AC-1 | — | `node scripts/audit-esteira.mjs .` | done |
| 2 | Configurar `pyproject.toml` para o pacote `neo-cmd` (`module-name = "neo"`, `classifiers`, `keywords`, `[project.urls]`) e enxugar o `README.md` mantendo apenas o resumo essencial | AC-2, AC-3 | 1 | `uv build && node scripts/audit-esteira.mjs .` | done |
| 3 | Criar `.github/workflows/publish.yml` para build e publicação no PyPI via GitHub Actions (Trusted Publishing OIDC em tags `v*`, releases e `workflow_dispatch`) e adicionar testes em `tests/unit/test_pypi_package.py` | AC-2, AC-3, AC-4 | 2 | `uv run pytest tests/unit/test_pypi_package.py -v` | done |
| 4 | Atualizar `docs/STATE.md` e validar todos os quality gates (`pytest`, `ruff`, `mypy`, `audit-esteira`) | AC-1, AC-2, AC-3, AC-4 | 3 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src && node scripts/audit-esteira.mjs .` | done |

## Plano de teste
- **Unidade (`tests/unit/test_pypi_package.py`):**
  - `test_AC_1_unnecessary_dirs_removed`: verifica que `.cursor`, `.windsurf`, `.spec-driven`, `.github/prompts` e `specs/0001-exemplo-cota-de-uso` não existem.
  - `test_AC_2_pyproject_pypi_metadata`: valida metadados de `pyproject.toml` (`name == "neo-cmd"`, `license == "MIT"`, `scripts.neo == "neo.cli:app"`, `tool.uv.build-backend.module-name == "neo"`, `urls`, `classifiers`).
  - `test_AC_3_readme_is_concise`: valida que o `README.md` é enxuto, contém instruções de instalação e link para a documentação completa.
  - `test_AC_4_publish_workflow_valid`: valida a sintaxe e configuração OIDC (`id-token: write`, `uv build`, `pypa/gh-action-pypi-publish`) em `.github/workflows/publish.yml`.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

## Checklist de Definition of Done
- [x] Todos os AC verdes **pelo gate executável** (não por inspeção)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] ADRs de decisões difíceis de reverter registrados
- [x] Glossário / context-map atualizados se mudaram
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado (próximo passo / decisões)
