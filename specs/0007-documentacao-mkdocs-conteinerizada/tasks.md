---
name: tasks
description: Decomposição e gates da feature 0007-documentacao-mkdocs-conteinerizada.
alwaysApply: false
---

# Tasks — Documentação MkDocs Conteinerizada

> Decomposição da implementação do MkDocs Material conteinerizado com Docker Compose e suporte local via uv.

## Plano de Implementação

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Adicionar grupo de dependências `docs` em `pyproject.toml` | AC-5 | — | `uv sync --group docs` | done |
| 2 | Criar configuração `mkdocs.yml` com tema Material, paleta claro/escuro, abas e PyMdown plugins estilo HTTPX | AC-1 | 1 | `uv run --group docs mkdocs --version` | done |
| 3 | Estruturar páginas Markdown no portal de documentação (`index.md`, `getting-started.md`, `configuration.md`, `cli/*.md`, `architecture.md`) | AC-2 | 2 | `uv run --group docs mkdocs build --strict` | done |
| 4 | Criar `Dockerfile.docs` e `docker-compose.docs.yml` com mapeamento de volumes e live-reload | AC-3, AC-4 | 2, 3 | `docker compose -f docker-compose.docs.yml config` | done |
| 5 | Adicionar testes automatizados em `tests/unit/test_docs_build.py` validando os arquivos de infraestrutura e compilação | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 | 4 | `uv run pytest tests/unit/test_docs_build.py -v` | done |
| 6 | Atualizar `README.md` com instruções de execução da documentação (Docker e uv) e validar esteira SDD | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 | 5 | `node scripts/audit-esteira.mjs && node scripts/eval-spec-fidelity.mjs` | done |

---

## Plano de Testes
- **Unidade / Automação:**
  - `tests/unit/test_docs_build.py`:
    - Verifica a presença e sintaxe de `mkdocs.yml` (tema material, paleta, abas, extensões PyMdown).
    - Verifica a existência e sintaxe de `Dockerfile.docs` e `docker-compose.docs.yml`.
    - Executa validação de integridade dos arquivos markdown e links de navegação.

---

## Divergências (SPEC_DEVIATION)
*(Nenhuma divergência identificada)*

---

## Checklist de Definition of Done
- [x] Todos os ACs verificados pelo gate executável de testes (`uv run pytest tests/unit/test_docs_build.py`)
- [x] Compilação estrita do MkDocs limpa sem avisos (`uv run --group docs mkdocs build --strict`)
- [x] Configuração do Docker Compose validada
- [x] Cobertura de testes mantida $\ge 80\%$
- [x] Auditoria da esteira 100% OK (`node scripts/audit-esteira.mjs` e `node scripts/eval-spec-fidelity.mjs`)
- [x] Manual atualizado no `README.md` e `docs/STATE.md` atualizado
