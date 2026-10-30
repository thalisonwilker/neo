---
name: tasks
description: Decomposição e gates da feature 0020-documentacao-modulo-financeiro.
alwaysApply: false
---

# Tasks — 0020 Atualização da Documentação com o Módulo Financeiro (`neo fin`)

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano de Implementação

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Atualizar `README.md` raiz e `docs/index.md` promovendo `neo fin` para recursos disponíveis e demonstrando exemplos práticos | AC-1 | — | `git diff README.md docs/index.md` | done |
| 2 | Atualizar `docs/getting-started.md` adicionando seção introdutória de início rápido com `neo fin` | AC-2 | 1 | `git diff docs/getting-started.md` | done |
| 3 | Atualizar matriz de comandos da CLI em `docs/cli/index.md` mapeando recursos e verbos de `neo fin` | AC-3 | — | `git diff docs/cli/index.md` | done |
| 4 | Criar guia prático `docs/guias/gestao-financeira.md`, indexar em `docs/guias/index.md` e registrar no `mkdocs.yml` | AC-4 | — | `uv run --group docs mkdocs build --strict` | done |
| 5 | Atualizar `tests/unit/test_docs_parity.py` e executar validação completa de compilação, testes e auditoria da esteira | AC-5 | 1, 2, 3, 4 | `uv run pytest tests/unit/test_docs_parity.py -v && uv run --group docs mkdocs build --strict && node scripts/audit-esteira.mjs . && node scripts/eval-spec-fidelity.mjs .` | done |

---

## Plano de Testes

- **Unidade e Paridade (`tests/unit/`):**
  - `test_docs_parity.py`: validação de que todas as páginas de documentação de `docs/cli/` correspondem a comandos existentes e estão devidamente referenciadas.
  - `test_docs_build.py`: execução da compilação estrita do MkDocs (`mkdocs build --strict`).
- **Auditoria SDD (`scripts/`):**
  - `audit-esteira.mjs`: validação de frontmatter, links internos e integridade das specs.
  - `eval-spec-fidelity.mjs`: checagem de cobertura 100% de ACs por tasks e testes.

---

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

---

## Checklist de Definition of Done
- [x] Todos os 5 ACs verificados pelos gates executáveis de teste
- [x] Compilação MkDocs estrita 100% verde (`uv run --group docs mkdocs build --strict`)
- [x] Testes de paridade passando (`uv run pytest tests/unit/test_docs_parity.py -v`)
- [x] Auditoria da esteira 100% OK (`node scripts/audit-esteira.mjs .` e `node scripts/eval-spec-fidelity.mjs .`)
- [x] `docs/STATE.md` atualizado
