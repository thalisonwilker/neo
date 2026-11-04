---
name: tasks
description: Validação da navegação MkDocs organizada pela árvore da CLI.
alwaysApply: false
---

# Tasks — Navegação pela árvore da CLI

| # | Task | Cobre AC | Depende de | Gate | Status |
|---|---|---|---|---|---|
| 1 | Reorganizar a navegação e registrar a visão geral de configuração | AC-1, AC-2 | — | `uv run pytest tests/unit/test_docs_build.py tests/unit/test_docs_parity.py -v` | done |
| 2 | Verificar build e auditoria da documentação | AC-1, AC-2 | 1 | `uv run mkdocs build --strict && node scripts/audit-esteira.mjs .` | done |
| 3 | Apresentar árvore aninhada de comandos com links por recurso | AC-3 | 1 | `uv run pytest tests/unit/test_docs_parity.py tests/unit/test_docs_build.py -v` | done |
