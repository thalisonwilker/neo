---
name: tasks
description: Decomposição e gates da feature 0009-refactor-cli-git-e-tasks.
alwaysApply: false
---

# Tasks — Refactor CLI: `neo git` e `neo tasks`

> Reorganização da borda `interfaces/` (`src/neo/commands/`) — sem alterar domínio nem integrações.

## Plano de Implementação

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Criar `commands/git.py` (`git_app`) agrupando `workspace_app`, `repo_app`, `commits_app` e `git config` (mover `auth` e `set/get-provider` de `config.py`; rejeitar `shortcut` com dica `neo tasks config`) | AC-1, AC-2 | — | `uv run pytest tests/e2e/test_config_flow.py tests/e2e/test_repo_commands.py tests/e2e/test_workspace_commands.py tests/e2e/test_commits_commands.py tests/e2e/test_github_commands.py -v` | done |
| 2 | Criar `commands/tasks.py` (`tasks_app`) a partir de `story.py`, com opção `--service/-s` (default `shortcut`, validação) e `tasks config set/get/delete` | AC-3, AC-4 | — | `uv run pytest tests/e2e/test_story_commands.py -v` | done |
| 3 | Reduzir `commands/config.py` a `config show`; registrar apenas `config`, `git`, `tasks` em `cli.py`; remover registro de `repo/workspace/commits/story` | AC-5, AC-6 | 1, 2 | `uv run pytest tests/unit/test_cli.py -v` | done |
| 4 | Atualizar mensagens de erro de credencial ausente para os novos comandos (integrations/CLI) | AC-7 | 1, 2 | `uv run pytest tests/unit tests/e2e -v` | done |
| 5 | Migrar/atualizar testes unit + e2e para os novos caminhos e adicionar casos de AC-2 (shortcut em git), AC-3 (serviço inválido) e AC-6 (comandos removidos) | AC-1…AC-6 | 3, 4 | `uv run pytest tests/unit tests/e2e -v --cov=neo --cov-fail-under=80` | done |
| 6 | Atualizar `README.md`, `docs/` (cli/*, getting-started, configuration), `docs/glossary.md` (se houver termo novo) e `docs/STATE.md` | AC-7 | 5 | `uv run --group docs mkdocs build --strict` | done |
| 7 | Gates finais: lint, tipos e auditoria SDD | AC-1…AC-7 | 6 | `uv run ruff check . && uv run mypy src && node scripts/audit-esteira.mjs && node scripts/eval-spec-fidelity.mjs` | done |

---

## Plano de Testes
- **Unidade:** `tests/unit/test_cli.py` — `neo --help` lista só `config|git|tasks`; `neo repo` etc. → exit 2 (AC-6).
- **Aceite (E2E):** reaproveitar os arquivos e2e existentes trocando o prefixo (`git repo list`, `tasks list`, `git config auth set github`); novos casos:
  - `git config auth set shortcut` → exit 1 com dica `neo tasks config` (AC-2).
  - `tasks --service jira list` → exit 1 listando `shortcut` (AC-3).
  - `config show` agrega git + tasks (AC-5).

---

## Divergências (SPEC_DEVIATION)
*(Nenhuma)*

---

## Checklist de Definition of Done
- [x] Todos os ACs verificados pelo gate executável (`uv run pytest`)
- [x] Cobertura ≥ 80% (`uv run pytest --cov=neo`)
- [x] Análise estática limpa (`uv run ruff check .` e `uv run mypy src`)
- [x] Auditoria da esteira 100% OK (`node scripts/audit-esteira.mjs`)
- [x] README, `docs/` e `docs/STATE.md` atualizados
