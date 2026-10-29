---
name: tasks
description: Decomposição e gates da feature 0018 - Agentes Especializados Multi-Role.
alwaysApply: false
---

# Tasks — 0018 Agentes Especializados Multi-Role

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano
| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Implementar serviço de papéis de agentes (`agent_roles.py`) com catálogo, validação de role e montagem de prompt contextualizado | AC-1, AC-3 | — | `uv run pytest tests/unit/test_agent_roles_service.py -v` | done |
| 2 | Implementar subcomando `neo agent roles` e opção `--role` em `neo agent run` com injeção de prompt interativo | AC-1, AC-2, AC-3 | 1 | `uv run pytest tests/e2e/test_agent_roles.py -v` | done |
| 3 | Estender configuração de modelos por papel (`model.<role>`) em `config.py` e atualizar seção `AGENT` em `neo config show` | AC-4, AC-5 | 1, 2 | `uv run pytest tests/e2e/test_agent_role_config.py -v` | done |
| 4 | Atualizar documentação MkDocs (`cli/agent/`) e testes de paridade de comandos CLI | AC-6 | 3 | `uv run mkdocs build --strict && uv run pytest tests/unit/test_docs_parity.py -v` | done |
| 5 | Executar suíte completa de testes, auditoria da esteira e atualização do `docs/STATE.md` | AC-1 a AC-6 | 4 | `uv run pytest -v && node scripts/audit-esteira.mjs . && node scripts/eval-spec-fidelity.mjs` | done |

## Plano de teste
- Testes unitários para catálogo de roles, validação de identificadores e composição de prompt contextualizado por papel.
- Testes E2E para `neo agent roles` (humano e JSON), `neo agent run --role` com rejeição de papéis inválidos (código 2).
- Testes de precedência de modelo: `model.<role>` > `model` geral.
- Validação estrita do MkDocs (`mkdocs build --strict`).

## Divergências (SPEC_DEVIATION)
*(Nenhuma identificada)*

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Spec e tasks atualizadas refletindo a entrega
- [x] `docs/STATE.md` atualizado

