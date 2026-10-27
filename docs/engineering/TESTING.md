---
name: TESTING
description: Comandos de gate e convenções de teste para o Neo.
alwaysApply: false
---

# TESTING — Como verificar o Neo

> **Fonte única dos comandos de gate** e das convenções de teste. É o que o **DoD**, a **CI** e os **agentes** consomem para provar que uma task/feature está pronta.

## Como rodar

| Nível | Comando | Quando |
|---|---|---|
| **Unidade** | `uv run pytest tests/unit -v` | Sempre durante desenvolvimento |
| **Integração** | `uv run pytest tests/integration -v` | Ao alterar adapters e clientes HTTP (com mocks `respx`) |
| **Aceite (CLI E2E)** | `uv run pytest tests/e2e -v` | Um teste por `AC-N` da spec via `CliRunner` |
| **Lint & Formatação** | `uv run ruff check . && uv run ruff format --check .` | Pré-commit / CI |
| **Análise Estática** | `uv run mypy src` | CI / Validação de types |
| **Cobertura** | `uv run pytest --cov=neo --cov-report=term-missing --cov-fail-under=80` | Validação de PR / CI |

## Convenções
- Pirâmide: testes de unidade rápidos para lógica de análise e parsing; testes de integração para clientes de API com `respx` mockando respostas JSON; testes E2E executando o app Typer com `CliRunner`.
- **Cada `AC-N` da spec tem um teste de aceite que é o seu gate.** Nomeie o teste com o ID (`test_AC_1_*` / `AC-1: ...`) para rastreabilidade spec → teste.
- Zero chamadas externas reais para APIs durante a execução da suíte de testes.
- **Análise estática estrita:** Mypy configurado com checagem de tipos sem retorno `Any` não tipado.

## Gates (Definition of Done executável)
- Uma **task** só vira `done` quando o **Gate (comando)** dela em `tasks.md` passa.
- Uma **feature** só faz merge quando:
  1. `uv run ruff check .` passa sem warnings.
  2. `uv run ruff format --check .` passa.
  3. `uv run mypy src` passa sem erros de tipagem.
  4. Todos os testes de aceite (`AC-N`) passam.
  5. Cobertura mínima de 80% atingida.
