---
name: tasks
description: Decomposição e gates da feature. Puxe ao implementar.
alwaysApply: false
---

# Tasks — 0028 Refactor comando neo git repo list

> Decomposição da implementação. Cada task **mapeia para um ou mais `AC-N`** (rastreabilidade
> spec → task → commit) e tem um **gate executável**: o comando que prova que ela está pronta.
> Marque `[P]` nas tasks que podem rodar em paralelo (sem dependência entre si).

## Plano
| #  | Task | Cobre AC | Depende de | Gate (comando) | Status |
|----|------|----------|------------|----------------|--------|
| 1  | Adicionar campo `created_on` aos DTOs de repositório (`BitbucketRepo`, parsing GitHub e Bitbucket) e criar helper de formatação de data americana (`MM/DD/YYYY`) | AC-1, AC-3 | — | `uv run pytest tests/unit/test_repo_models.py -v` | done |
| 2  | Criar resolução de vínculo de `task` local (`git-context.json`) para repositórios remotos por correspondência de slug/nome com normalização `#<TASK-ID>` | AC-1 | 1 | `uv run pytest tests/unit/test_repo_task_binding.py -v` | done |
| 3  | Refatorar `neo git repo list` em `src/neo/commands/repo.py` para listar remotos com validação de conexão, novas colunas e formato de data americano; manter `remote-list` como alias e adicionar `local-list` | AC-1, AC-2, AC-3, AC-4, AC-5 | 1, 2 | `uv run pytest tests/unit/test_repo_list_command.py tests/e2e/test_repo_commands.py -v` | done |
| 4  | Atualizar testes E2E e unitários existentes para compatibilidade com o novo comportamento de `neo git repo list`, `remote-list` e `local-list` | AC-1 a AC-5 | 3 | `uv run pytest tests/unit tests/e2e -v` | done |
| 5  | Atualizar documentação MkDocs (`docs/cli/git/repo/list.md`, `remote-list.md`, `local-list.md`, `index.md`, navegação) e validar paridade estrita | AC-1, AC-5 | 3 | `uv run pytest tests/unit/test_docs_parity.py -v && uv run --group docs mkdocs build --strict` | done |

## Plano de teste
- Unidade:
  - Testes dos DTOs `BitbucketRepo` com parsing de `created_on` / `created_at` em Bitbucket e GitHub.
  - Testes do helper de formatação de datas em formato americano `MM/DD/YYYY`.
  - Testes de mapeamento de task por repo com retorno formatado `#<TASK-ID>`.
- Integração / E2E:
  - Testes de `neo git repo list` contra mocks do GitHub e Bitbucket validando colunas, cabeçalhos, formato de datas e exibição da task.
  - Testes de erro de autenticação (`AUTH_ERROR`, code 3) quando credenciais forem inválidas ou ausentes.
  - Testes de `neo git repo list --json`.
  - Testes de compatibilidade com `remote-list` e funcionamento de `local-list`.
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
- [x] ADRs de decisões difíceis de reverter registrados (se aplicável — não houve decisão arquitetural irreversível)
- [x] Glossário / context-map atualizados se mudaram (inalterados)
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado (próximo passo / decisões)

