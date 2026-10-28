---
name: tasks
description: Decomposição e gates planejados (backlog) da feature 0010-branches-prs-e-detalhes-repo.
alwaysApply: false
---

# Tasks — Operações de Backlog Git (`branch`, `pr`, `tag`, `release`, `repo open/clone/create`, `commits diff`)

> Decomposição planejada para implementação futura (backlog). `neo git repo show` e paginação de `repo list/search` foram movidos para [0014-gramatica-cli-git](../0014-gramatica-cli-git/tasks.md).

## Plano (Backlog Planejado)

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Implementar modelos e clientes para `branch` (`list`, `show`, `create`, `remove`) e `pr` (`list`, `show`, `search`, `create`) no GitHub e Bitbucket | AC-1, AC-2 | — | `uv run pytest tests/unit -v` | todo |
| 2 | Implementar comandos `neo git branch` e `neo git pr` seguindo a gramática estrita sem atalhos de uma letra | AC-1, AC-2 | 1 | `uv run pytest tests/e2e -v` | todo |
| 3 | Implementar comandos `neo git tag` e `neo git release` (com retorno código `5` no Bitbucket para `release` sugerindo `tag`) | AC-3 | 1 | `uv run pytest tests/e2e -v` | todo |
| 4 | Implementar `neo git repo open|clone|create` e `neo git commits diff <sha>` na nova gramática | AC-4 | 1 | `uv run pytest tests/e2e -v` | todo |

## Checklist de Definition of Done
- [ ] Todos os AC verdes **pelo gate executável**
- [ ] Nenhum `SPEC_DEVIATION` pendente
- [ ] Documentação atualizada removendo o aviso `!!! note "Planejado"` dos itens implementados
- [ ] `docs/STATE.md` atualizado
