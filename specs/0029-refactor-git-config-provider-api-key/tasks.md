---
name: tasks
description: Decomposição e gates da feature. Puxe ao implementar.
alwaysApply: false
---

# Tasks — 0029 Refactor git config provider e api-key

> Decomposição da implementação. Cada task **mapeia para um ou mais `AC-N`** (rastreabilidade
> spec → task → commit) e tem um **gate executável**: o comando que prova que ela está pronta.
> Marque `[P]` nas tasks que podem rodar em paralelo (sem dependência entre si).

## Plano
| #  | Task | Cobre AC | Depende de | Gate (comando) | Status |
|----|------|----------|------------|----------------|--------|
| 1  | Implementar reset da seção `[git]` em `set_git_config_value` ao definir chave `provider` em `src/neo/config.py` | AC-1 | — | `uv run pytest tests/unit/test_config.py -v -k provider` | done |
| 2  | Refatorar `_set_api_key` em `src/neo/commands/git.py`: remover solicitação de e-mail no Bitbucket (autenticação Bearer), testar conexão com o provedor e emitir "Conexão efetuada" no sucesso e "Conexão recusada" no erro | AC-2, AC-3, AC-4 | — | `uv run pytest tests/unit/test_git_config_api_key.py -v` | done |
| 3  | Atualizar testes E2E e unitários existentes (`test_git_api_key.py`, `test_config_flow.py`, etc.) para refletir as novas mensagens e a ausência de prompt de e-mail | AC-1 a AC-4 | 1, 2 | `uv run pytest tests/unit tests/e2e -v` | done |
| 4  | Atualizar documentação MkDocs (`docs/cli/git/config.md`, `docs/cli/git/auth.md`, `docs/guias/trocar-provedor.md`, etc.) e validar paridade estrita | AC-1, AC-2, AC-3 | 3 | `uv run pytest tests/unit/test_docs_parity.py -v && uv run --group docs mkdocs build --strict` | done |

## Plano de teste
- Unidade:
  - Teste de `set_git_config_value("provider", ...)` resetando chaves residuais da seção `[git]`.
  - Testes do prompt `config set api-key` para GitHub e Bitbucket com retornos "Conexão efetuada" e "Conexão recusada".
- Integração / E2E:
  - Testes de fluxo de configuração e troca de provedor com verificação de reset do `config.toml`.
  - Suíte completa de testes de credenciais com mocks de API.
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

