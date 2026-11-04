---
name: tasks
description: Plano preliminar para os comandos de pull request.
alwaysApply: false
---

# Tasks — Comandos de Pull Request

| # | Task | Cobre AC | Depende de | Gate | Status |
|---|---|---|---|---|---|
| 1 | Fechar contrato, estados e tratamento de falhas | AC-1, AC-2, AC-3, AC-4 | — | Revisão da spec | done |
| 2 | Implementar operações nos clientes GitHub e Bitbucket | AC-1, AC-2, AC-3, AC-4 | 1 | `uv run pytest tests/unit -v` | done |
| 3 | Implementar comandos CLI e testes de aceite | AC-1, AC-2, AC-3, AC-4 | 2 | `uv run pytest tests/e2e -v` | done |
| 4 | Atualizar documentação e rodar gates de qualidade | AC-1, AC-2, AC-3, AC-4 | 3 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src` | done |
| 5 | Listar PRs abertos ao executar `neo git pr`, com testes e documentação | AC-5 | 2 | `uv run pytest tests/e2e/test_pr_commands.py tests/unit/test_github_pr.py tests/unit/test_bitbucket_pull_requests.py -v` | done |

## Definition of Done
- [x] Critérios exercitados por testes e sem `SPEC_DEVIATION` pendente.
- [x] Suíte completa, cobertura 85,15%, Ruff, Mypy, MkDocs e auditoria da esteira aprovados.
- [ ] Anexar cobertura ao PR; gates separados de complexidade e SAST ainda não estão configurados no projeto.
