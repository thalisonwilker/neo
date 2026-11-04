---
name: tasks
description: Plano de implementação e gates para a atualização dos comandos Git.
alwaysApply: false
---

# Tasks — Atualização dos comandos Git

| # | Task | Cobre AC | Depende de | Gate | Status |
|---|---|---|---|---|---|
| 1 | Registro, seleção e resolução de contexto local e task | AC-1, AC-2, AC-7 | — | `uv run pytest tests/e2e/test_git_context.py -v` | done |
| 2 | Comandos de branches locais e configuração da branch | AC-3, AC-7 | 1 | `uv run pytest tests/e2e/test_git_branches_0023.py tests/e2e/test_git_context.py -v` | done |
| 3 | Validar e gerenciar credenciais pelo novo comando | AC-6, AC-7 | — | `uv run pytest tests/e2e/test_git_api_key.py -v` | done |
| 4 | Criar/publicar repositório e editar descrição nos provedores | AC-4, AC-5 | 1, 3 | `uv run pytest tests/e2e/test_git_repo_creation.py tests/unit/test_repo_description_api.py -v` | done |
| 5 | Atualizar documentação e compatibilidade dos comandos | AC-1 a AC-7 | 1–4 | `uv run mkdocs build --strict` | done |
| 6 | Rodar gates completos e atualizar estado | AC-1 a AC-7 | 1–5 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run mypy src` | done |

## Plano de teste
- Unidade e integração: armazenamento isolado, Git local temporário e respostas HTTP simuladas para ambos os provedores, sem chamadas reais.
- Aceite: pelo menos um teste por `AC-N`, incluindo falhas e isolamento de credenciais.
- Documentação: teste de paridade, build estrito e auditoria da esteira.

## Divergências
- Nenhuma registrada.

## Definition of Done
- [x] ACs verdes pelos gates; cobertura mínima, Ruff e Mypy aprovados.
- [x] ADR de decisões estruturais, glossário e documentação atualizados.
- [x] Nenhum `SPEC_DEVIATION` pendente; `docs/STATE.md` atualizado.
- [ ] Avaliar análise de complexidade e SAST: o projeto não define comandos executáveis para esses gates; anexar cobertura ao PR quando houver PR.
