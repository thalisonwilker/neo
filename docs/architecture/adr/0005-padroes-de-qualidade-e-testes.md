---
name: adr-0005
description: Decisão sobre ferramentas de qualidade de código, tipagem e testes.
alwaysApply: false
---

# ADR-0005: Padrões de Qualidade de Código, Tipagem e Testes

- **Status:** aceito
- **Data:** 2026-10-27
- **Decisores:** Time do Projeto Neo

## Contexto
Para garantir que a esteira SDD funcione com gates determinísticos de Definition of Done (DoD), o projeto precisa de verificações estáticas e testes automatizados rápidos e confiáveis.

## Decisão
1. **Linter e Formatação:** `ruff` (linter + formatter unificados em Rust, extremamente rápidos).
2. **Tipagem Estática:** `mypy` em modo estrito (`strict = true` no `pyproject.toml`).
3. **Framework de Testes:** `pytest` com `pytest-cov` e `respx` (para mocks assíncronos/síncronos de chamadas HTTP `httpx`).
4. **Pirâmide de Testes:**
   - **Testes Unitários:** Testam regras de negócio de `services/analysis.py`, parsing de parâmetros em `commands/` e serialização de modelos.
   - **Testes de Integração:** Testam adapters de `integrations/` com chamadas HTTP mockadas via `respx`.
   - **Testes de Aceite (CLI E2E):** Testam comandos da CLI usando `typer.testing.CliRunner` para cada critério de aceite (`AC-N`) das specs.
5. **Automação CI:** GitHub Actions rodando `ruff check`, `ruff format --check`, `mypy` e `pytest --cov=neo` em todo pull request.

## Consequências
- **+** Feedback imediato de qualidade em frações de segundo com o Ruff.
- **+** Código robusto, autoexplicativo e à prova de regressões com tipagem estrita e testes cobrindo critérios de aceite.
- **−** Exigência de disciplina na declaração de tipos completos em todas as assinaturas de funções.
