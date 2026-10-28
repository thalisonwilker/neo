---
name: tasks
description: Decomposição e gates da feature 0014-gramatica-cli-git.
alwaysApply: false
---

# Tasks — Refatoração da Gramática `neo git` e Padronização da CLI

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano de Implementação

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Padronizar códigos de saída (`ExitCode`: `0`, `1`, `2`, `3`, `4`, `5`), exceções de domínio (`AuthenticationError`, `ResourceNotFoundError`, `UnsupportedProviderOperationError`), seção `[git]` em `config.py` (chaves `provider`, `workspace`, `default-branch`, `branch-pattern`, `commit-format`, bloqueio de `token`), arquivo `~/.config/neo/credentials.toml` (`0600`) e precedência de variáveis `NEO_GIT_*` / `NEO_GITHUB_TOKEN` / `NEO_BITBUCKET_*` | AC-2, AC-3, AC-8 | — | `uv run pytest tests/unit/test_config.py tests/unit/test_resolver.py -v` | done |
| 2 | Implementar `neo git config (set|get|list|unset)` e `neo git auth (login|status|logout)` sem atalhos de uma letra e sem `--token`, com suporte a e-mail + API Token no Bitbucket e bloqueio orientativo dos comandos antigos (`config auth`, `set-provider`, `get-provider`) | AC-1, AC-2, AC-3, AC-8 | 1 | `uv run pytest tests/e2e/test_config_flow.py -v` | done |
| 3 | Refatorar `neo git workspace (list|select|show)` e `neo git repo (list|search|show)` para a nova gramática (somente opções longas, `--query` em `search`, `repo show`, paginação e erros orientativos para `workspace current/set` e `repo clone/create`) `[P]` | AC-1, AC-4, AC-5, AC-8 | 1 | `uv run pytest tests/e2e/test_workspace_commands.py tests/e2e/test_repo_commands.py -v` | done |
| 4 | Implementar `get_commit` nos clientes GitHub/Bitbucket e refatorar `neo git commits (list|search|show)` e `neo git status` `[P]` | AC-1, AC-6, AC-7, AC-8 | 1 | `uv run pytest tests/unit/test_bitbucket_client.py tests/unit/test_github_client.py tests/e2e/test_commits_commands.py tests/e2e/test_git_status.py -v` | done |
| 5 | Atualizar documentação MkDocs (`docs/index.md`, `getting-started.md`, `configuration.md`, `cli/index.md`, `cli/config.md`, `cli/auth.md`, `cli/workspace.md`, `cli/repo.md`, `cli/commits.md`, `cli/status.md`, `glossary.md`, `architecture.md`, `migration.md`, `mkdocs.yml`, `README.md` e `CHANGELOG.md`) | AC-9 | 2, 3, 4 | `uv run --group docs mkdocs build --strict && uv run pytest tests/unit/test_docs_build.py -v` | done |
| 6 | Executar todos os gates finais de qualidade (cobertura >= 80%, Ruff, Mypy estrito e auditoria SDD) | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9 | 5 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src && node scripts/audit-esteira.mjs . && node scripts/eval-spec-fidelity.mjs .` | done |

---

## Plano de Testes
- **Unidade (`tests/unit/`):**
  - `test_config.py`: precedência `CLI > NEO_GIT_* > [git] config.toml > remote > default`, CRUD das 5 chaves de `[git]`, rejeição da chave `token` (exit `2`), variáveis `NEO_GITHUB_TOKEN`/`GITHUB_TOKEN`/`GH_TOKEN` e `NEO_BITBUCKET_EMAIL` + `NEO_BITBUCKET_TOKEN`, armazenamento em `~/.config/neo/credentials.toml` com permissão `0600`.
  - `test_bitbucket_client.py` e `test_github_client.py`: método `get_commit(repo_slug, sha, workspace)`, paginação de `list_repositories` e mapeamento de erros HTTP para códigos `3` (401/403), `4` (404) e `5` (não suportado).
  - `test_docs_build.py`: verifica existência das novas páginas (`cli/config.md`, `cli/auth.md`, `cli/status.md`, `migration.md`), ausência de comandos antigos fora de `migration.md` e build estrito do MkDocs.
- **Aceite E2E (`tests/e2e/`):**
  - `test_AC_1_no_short_flags_and_json_support`: garante que `-p`, `-w`, `-r`, `-q`, `-l`, `-y` falham com código `2` e que `--json` funciona em todos os comandos de leitura.
  - `test_AC_2_git_config_commands`: testa `set`, `get`, `list`, `unset` e erro código `2` ao passar `token` ou chave inválida.
  - `test_AC_3_git_auth_commands`: testa `auth login` (GitHub e Bitbucket com prompt oculto), `auth status` (sem vazamento de token) e `auth logout` (confirmação e `--yes`).
  - `test_AC_4_workspace_commands`: testa `workspace list`, `workspace select` e `workspace show`.
  - `test_AC_5_repo_commands`: testa `repo list`, `repo search --query` e `repo show`.
  - `test_AC_6_commits_commands`: testa `commits list`, `commits search --query` e `commits show <sha>`.
  - `test_AC_7_git_status`: testa `neo git status` em diretório Git e fora dele (humano e `--json`).
  - `test_AC_8_legacy_commands_fail_with_migration_hint`: garante que comandos antigos falham com código `2` e mensagem apontando o novo comando.

---

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

---

## Checklist de Definition of Done
- [x] Todos os ACs verificados pelo gate executável (`uv run pytest`)
- [x] Cobertura >= 80% (`uv run pytest --cov=neo --cov-fail-under=80`)
- [x] Análise estática limpa (`uv run ruff check .` e `uv run mypy src`)
- [x] Nenhum atalho de uma letra em `neo git` e nenhum comando aceitando token via argumento
- [x] Documentação, glossário, `migration.md` e `CHANGELOG.md` atualizados (`mkdocs build --strict` verde)
- [x] Auditoria da esteira 100% OK (`node scripts/audit-esteira.mjs .` e `node scripts/eval-spec-fidelity.mjs .`)
- [x] `docs/STATE.md` atualizado
