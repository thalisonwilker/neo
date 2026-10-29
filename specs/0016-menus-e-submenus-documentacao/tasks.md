---
name: tasks
description: Decomposição e gates da feature de menus e submenus da documentação.
alwaysApply: false
---

# Tasks — 0016 Menus e Submenus na Documentação do Neo

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano
| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Configurar `mkdocs.yml` com `navigation.indexes`, plugin `redirects` e nova árvore de navegação com submenus | AC-1, AC-2, AC-6 | — | `uv run mkdocs build` | done |
| 2 | Reformular `docs/cli/index.md` (Conceitos Gerais, matriz recurso x ação, verbos, opções, códigos de saída e seção "Qual comando usar?") | AC-4 | 1 | `test -f docs/cli/index.md` | done |
| 3 | Criar e padronizar páginas do módulo Git em `docs/cli/git/` (`index`, `auth`, `config`, `status`, `workspace`, `repo`, `commits`, `planejado`) | AC-1, AC-3 | 1, 2 | `ls docs/cli/git/*.md` | done |
| 4 | Criar e padronizar páginas do módulo Tasks em `docs/cli/tasks/` (`index`, `resume`, `whoami`, `iterations`, `list`, `search`, `show`, `analyze`, `config`) | AC-1, AC-3 | 1, 2 | `ls docs/cli/tasks/*.md` | done |
| 5 | Criar e padronizar páginas do módulo Agent em `docs/cli/agent/` (`index`, `config`, `status`, `setup`, `run`) | AC-1, AC-3 | 1, 2 | `ls docs/cli/agent/*.md` | done |
| 6 | Criar páginas de Guias práticos em `docs/guias/` (`index`, `ci-json`, `trocar-provedor`, `fluxo-diario`) | AC-1 | 1 | `ls docs/guias/*.md` | done |
| 7 | Reformular `docs/index.md` (Home: fluxo completo de 4-5 comandos, cheat sheet top 10 e remoção de `-p`) | AC-5 | 1 | `grep -v "\-p" docs/index.md` | done |
| 8 | Remover arquivos legados substituídos e validar links cruzados | AC-6, AC-7 | 3, 4, 5, 6, 7 | `uv run mkdocs build --strict` | done |
| 9 | Implementar script/teste de verificação de paridade de comandos vs documentação | AC-7 | 8 | `uv run pytest tests/unit/test_docs_parity.py -v` | done |

## Plano de teste
- Validação estrutural do MkDocs: `uv run mkdocs build --strict`
- Teste automatizado de paridade CLI vs Documentação: script/teste que percorre `neo --help` recursivamente e confere a existência das páginas em `docs/cli/`.

## Divergências (SPEC_DEVIATION)
*(Nenhuma identificada)*

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável (`uv run mkdocs build --strict` e `pytest`)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Spec e tasks atualizadas refletindo a entrega
- [x] `docs/STATE.md` atualizado
