---
name: tasks
description: Decomposição e gates da feature 0002-fundacao-cli-e-configuracao.
alwaysApply: false
---

# Tasks — 0002-fundacao-cli-e-configuracao

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e tem um gate executável.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Adicionar dependências core (`typer`, `rich`, `keyring`, `httpx`, `pydantic`) e dev (`pytest`, `pytest-cov`, `respx`, `ruff`, `mypy`) no `pyproject.toml` | — | — | `uv sync` | done |
| 2 | Implementar módulo de configuração e gestão de credenciais em `src/neo/config.py` com Keyring e fallback | AC-2, AC-4, AC-6 | 1 | `uv run pytest tests/unit/test_config.py -v` | done |
| 3 | Implementar entrypoint CLI em `src/neo/cli.py` com callback de versão e flag global `--json` | AC-1, AC-5 | 1 | `uv run pytest tests/unit/test_cli.py -v` | done |
| 4 | Implementar subcomando de autenticação em `src/neo/commands/config.py` (`set`, `get`, `delete`, `show`) | AC-2, AC-3, AC-5, AC-6 | 2, 3 | `uv run pytest tests/e2e/test_config_flow.py -v` | done |
| 5 | Validação de qualidade estática e cobertura de testes da fundação | AC-1 a AC-6 | 2, 3, 4 | `uv run ruff check . && uv run mypy src && uv run pytest --cov=neo` | done |

## Plano de teste
- **Unidade:**
  - `tests/unit/test_config.py`: Testa precedência de variáveis de ambiente vs keyring vs arquivo `config.toml`, mascaramento de tokens e tratamento de serviços inválidos.
  - `tests/unit/test_cli.py`: Testa `--version`, `--help` e interceptação da flag `--json`.
- **Aceite (E2E):**
  - `tests/e2e/test_config_flow.py`: Executa o fluxo de CLI ponta a ponta com `CliRunner` validando os comandos `neo config auth set`, `get`, `delete` e `show` tanto em formato Rich quanto com `--json`.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência identificada.

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável (`uv run pytest tests/e2e`)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Análise estática limpa (`ruff check`, `mypy src`)
- [x] Cobertura de testes ≥ 80% (91.42% atingido)
- [x] `docs/STATE.md` atualizado

