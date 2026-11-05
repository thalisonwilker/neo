---
name: tasks
description: Decomposição, rastreabilidade e gates da modularização de comandos e provedores.
alwaysApply: false
---

# Tasks — Modularização de comandos e provedores

> **Status do plano:** implementado; gates executados em 2026-11-04.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Registrar ADR da localização dos adapters de tarefas e preparar testes de caracterização da CLI, erros e credenciais | AC-2, AC-6 | — | `uv run pytest tests/unit tests/e2e -v` | done |
| 2 | Definir contrato e modelos Git neutros; adaptar GitHub, Bitbucket e resolvedor | AC-3, AC-6 | 1 | `uv run pytest tests/unit tests/integration -v` | done |
| 3 | Definir contratos e modelos de tarefas, capacidades opcionais e adaptar Shortcut e resolvedor | AC-4, AC-5, AC-6 | 1 | `uv run pytest tests/unit tests/integration -v` | done |
| 4 | Extrair os grupos e ações de `git`, incluindo config, repo, branch, commits e PR | AC-1, AC-2, AC-3 | 2 | `uv run pytest tests/unit tests/e2e -v` | done |
| 5 | Extrair os grupos e ações de `tasks`, usando os contratos e capacidades de tarefas | AC-1, AC-2, AC-4, AC-5 | 3 | `uv run pytest tests/unit tests/e2e -v` | done |
| 6 | Extrair os grupos e ações de `config`, `agent` e `fin`; atualizar composição da CLI | AC-1, AC-2 | 4, 5 | `uv run pytest tests/unit tests/e2e -v` | done |
| 7 | Atualizar glossário, mapa de contextos, documentação aplicável e estado; completar testes de aceite por AC | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 | 6 | `uv run pytest tests/e2e -v && uv run mkdocs build --strict && node scripts/audit-esteira.mjs .` | done |
| 8 | Executar gates completos e registrar evidências de cobertura e análise estática | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 | 7 | `uv run pytest --cov=neo --cov-report=term-missing --cov-fail-under=80 && uv run ruff check . && uv run ruff format --check . && uv run mypy src` | done |

## Plano de teste

- Caracterização: help, aliases, argumentos, prompts, JSON, erros e efeitos observáveis da CLI; manter testes das features anteriores.
- Contratos: exemplos parametrizados para GitHub e Bitbucket, conversão para modelos comuns e erros; Shortcut com operações e campos utilizados pelos comandos; provider de teste sem capacidade opcional.
- Integração HTTP: criar `tests/integration/` para os testes com respostas mockadas por `respx`; nenhuma chamada externa real.
- Aceite: testes identificados por `AC-N`, incluindo os caminhos da estrutura, imports, credenciais e execução via `CliRunner` conforme aplicável.
- Qualidade: gates da tabela, cobertura mínima de 80%, documentação estrita e auditoria SDD. Comandos de complexidade/SAST dependem de configuração existente; registrar qualquer limitação real.

## Evidências de validação

- `tests/e2e/test_0031_modularizacao.py`: testes identificados de AC-1 a AC-6; a suíte existente complementa a cobertura de comportamento e erros por comando e adapter.
- Suíte completa: **250 testes**, cobertura **87,41%**; integração e unidade: 141 testes. Ruff, format, Mypy, `neo --help`, build estrito MkDocs e auditoria da esteira passaram.
- Os comandos específicos de complexidade e SAST ainda não estão configurados no projeto. O relatório de cobertura deve ser anexado ao PR quando este for aberto.

## Divergências (SPEC_DEVIATION)

- Nenhuma registrada.

## Definition of Done

- [x] Todos os critérios de aceite passam pelos respectivos gates executáveis.
- [ ] Cobertura mínima atingida e relatório disponível para o PR.
- [ ] Análise estática limpa, incluindo comandos de complexidade e SAST quando configurados.
- [x] Nenhum `SPEC_DEVIATION` pendente.
- [x] ADR, glossário e mapa de contextos atualizados conforme as decisões aprovadas.
- [x] Spec fiel ao resultado e `docs/STATE.md` atualizado.
