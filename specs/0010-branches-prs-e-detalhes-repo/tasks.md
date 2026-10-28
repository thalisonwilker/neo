---
name: tasks
description: Decomposição e gates da feature 0010-branches-prs-e-detalhes-repo.
alwaysApply: false
---

# Tasks — Branches, Pull Requests e Detalhes de Repositório (`neo git`)

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Modelar `BitbucketBranch` e `BitbucketPullRequest` em `bitbucket_models.py` e parsers equivalentes em `github_models.py`; atualizar protocolo `GitProviderClient` em `resolver.py` | AC-2, AC-3, AC-4 | — | `uv run pytest tests/unit -v` | todo |
| 2 | Implementar paginação em `list_repositories` e métodos `list_branches`, `list_pull_requests` e `get_pull_request` em `BitbucketClient` e `GitHubClient` com testes unitários `respx` | AC-2, AC-3, AC-4, AC-5 | 1 | `uv run pytest tests/unit/test_bitbucket_client.py tests/unit/test_github_client.py -v` | todo |
| 3 | Adicionar subcomando `neo git repo show <slug>` em `commands/repo.py` `[P]` | AC-1 | 1 | `uv run pytest tests/e2e/test_repo_commands.py -v` | todo |
| 4 | Criar `commands/branches.py` (`neo git branches list`) e `commands/pr.py` (`neo git pr list`, `neo git pr show <id>`) e registrá-los em `commands/git.py` `[P]` | AC-2, AC-3, AC-4 | 2 | `uv run pytest tests/e2e/test_branches_pr_commands.py -v` | todo |
| 5 | Atualizar documentação (`README.md`, `docs/cli/`, `mkdocs.yml`, `docs/glossary.md`, `docs/STATE.md`) e validar todos os quality gates | AC-1, AC-2, AC-3, AC-4, AC-5 | 3, 4 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src && node scripts/audit-esteira.mjs .` | todo |

## Plano de teste
- **Unidade (`tests/unit/`):**
  - Parsing de modelos `BitbucketBranch` e `BitbucketPullRequest` (Bitbucket e GitHub).
  - Mocks HTTP (`respx`) para `list_branches`, `list_pull_requests` (estados `open`, `merged`, `declined`, `all`), `get_pull_request` e paginação de `list_repositories`.
- **Aceite CLI (`tests/e2e/`):**
  - `test_AC_1_repo_show`: painel detalhado e modo `--json` de `neo git repo show <slug>`, mais erro 404.
  - `test_AC_2_branches_list`: listagem e filtro `--query` de branches em `neo git branches list` (Bitbucket e GitHub), auto-detecção de repo e erro quando sem repo.
  - `test_AC_3_pr_list`: listagem de PRs por `--state` e validação de estado inválido.
  - `test_AC_4_pr_show`: exibição detalhada de um PR (`neo git pr show <id>`) e tratamento de 404.
  - `test_AC_5_repo_pagination`: listagem e busca retornando repositórios de múltiplas páginas.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

## Checklist de Definition of Done
- [ ] Todos os AC verdes **pelo gate executável** (não por inspeção)
- [ ] Nenhum `SPEC_DEVIATION` pendente
- [ ] ADRs de decisões difíceis de reverter registrados
- [ ] Glossário / context-map atualizados se mudaram
- [ ] Spec reflete o que foi construído
- [ ] `docs/STATE.md` atualizado (próximo passo / decisões)

