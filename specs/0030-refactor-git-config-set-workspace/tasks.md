---
name: tasks
description: Decomposição e gates da feature. Puxe ao implementar.
alwaysApply: false
---

# Tasks — 0030 Refactor git config set workspace

> Decomposição da implementação. Cada task **mapeia para um ou mais `AC-N`** (rastreabilidade
> spec → task → commit) e tem um **gate executável**: o comando que prova que ela está pronta.
> Marque `[P]` nas tasks que podem rodar em paralelo (sem dependência entre si).

## Plano
| #  | Task | Cobre AC | Depende de | Gate (comando) | Status |
|----|------|----------|------------|----------------|--------|
| 1  | Implementar recuperação de workspaces e seleção interativa/validada em `git_config_set` (`src/neo/commands/git.py`) quando `key == "workspace"` | AC-1, AC-2, AC-3, AC-4 | — | `uv run pytest tests/unit/test_git_config_workspace.py -v` | done |
| 2  | Atualizar testes E2E e unitários existentes que utilizam `neo git config set workspace` para garantir compatibilidade com validação remota (ou mock de workspaces) | AC-1 a AC-4 | 1 | `uv run pytest tests/unit tests/e2e -v` | done |
| 3  | Atualizar documentação MkDocs (`docs/cli/git/config.md`, `docs/cli/git/workspace.md`, etc.) e validar paridade estrita | AC-1, AC-2 | 2 | `uv run pytest tests/unit/test_docs_parity.py -v && uv run --group docs mkdocs build --strict` | done |

## Plano de teste
- Unidade:
  - Seleção interativa quando `value` é None (apresentação de opções 1..N e escolha).
  - Validação de slug existente quando `value` é fornecido diretamente.
  - Erro NOT_FOUND quando `value` não existe na lista retornada pela API.
  - Erro USAGE_ERROR quando o índice numérico for inválido (< 1 ou > len).
- Integração / E2E:
  - Testes do fluxo completo com GitHub e Bitbucket com mocks de API.
- Qualidade:
  - `uv run ruff check .`
  - `uv run ruff format .`
  - `uv run mypy src`
  - `uv run --group docs mkdocs build --strict`

## Divergências (SPEC_DEVIATION)
> Se a implementação precisar fugir da spec, registre aqui antes de seguir (ver `CLAUDE.md`).
- (Nenhuma divergência)

## Checklist de Definition of Done
- [x] Todos os AC verdes **pelo gate executável** (não por inspeção)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] ADRs de decisões difíceis de reverter registrados (se aplicável — sem decisão irreversível)
- [x] Glossário / context-map atualizados se mudaram (inalterados)
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado (próximo passo / decisões)
