---
name: tasks
description: Decomposição e gates da feature 0006-modulo-github-e-multi-provedor-git.
alwaysApply: false
---

# Tasks — Módulo GitHub e Multi-provedor Git

> Decomposição da implementação do suporte a GitHub e abstração de múltiplos provedores Git.

## Plano de Implementação

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Adicionar serviço `github` e gestão de `default_provider` no `src/neo/config.py` | AC-1, AC-2 | — | `uv run pytest tests/unit/test_config.py -v` | done |
| 2 | Modelar DTOs tipados do GitHub e implementar `GitHubClient` em `src/neo/integrations/github.py` | AC-5, AC-6, AC-7 | 1 | `uv run pytest tests/unit/test_github_client.py -v` | done |
| 3 | Criar resolvedor de provedor (`src/neo/integrations/resolver.py`) com auto-detecção por remote local, flag e config | AC-3, AC-4 | 1, 2 | `uv run pytest tests/unit/test_resolver.py -v` | done |
| 4 | Atualizar comandos `repo`, `commits` e `workspace` para utilizar o resolvedor com flag `--provider / -p` | AC-3, AC-4, AC-5, AC-6, AC-7 | 3 | `uv run pytest tests/e2e/test_github_commands.py -v` | done |
| 5 | Adicionar subcomandos `neo config set-provider` e `neo config get-provider` em `src/neo/commands/config.py` | AC-2 | 1 | `uv run pytest tests/e2e/test_config_flow.py -v` | done |
| 6 | Atualizar documentação no `README.md` e validar esteira SDD | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7 | 4, 5 | `node scripts/audit-esteira.mjs && node scripts/eval-spec-fidelity.mjs` | done |

---

## Plano de Testes
- **Unidade:**
  - `tests/unit/test_config.py`: testar credencial `github`, `GITHUB_TOKEN`, `default_provider`.
  - `tests/unit/test_github_client.py`: testar endpoints do GitHub (`/user`, `/user/repos`, `/orgs/{org}/repos`, `/repos/{owner}/{repo}/commits`) com `respx`.
  - `tests/unit/test_resolver.py`: testar regras de precedência e regex de remotes git.
- **Aceite (E2E):**
  - `tests/e2e/test_github_commands.py`: testar `neo repo list --provider github`, `neo commits search`, `neo workspace list --provider github`.
  - `tests/e2e/test_config_flow.py`: testar `neo config set-provider` e `neo config get-provider`.

---

## Divergências (SPEC_DEVIATION)
*(Nenhuma divergência identificada)*

---

## Checklist de Definition of Done
- [x] Todos os ACs verificados pelo gate executável de testes (`uv run pytest`)
- [x] Cobertura de testes mantida $\ge 80\%$ (`uv run pytest --cov=neo`)
- [x] Análise estática limpa (`uv run ruff check .` e `uv run mypy src`)
- [x] Auditoria da esteira 100% OK (`node scripts/audit-esteira.mjs`)
- [x] Manual atualizado no `README.md` e `docs/STATE.md` atualizado
