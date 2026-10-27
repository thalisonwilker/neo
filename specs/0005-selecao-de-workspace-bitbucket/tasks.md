---
name: tasks
description: Decomposição e gates da feature de seleção de workspace do Bitbucket.
alwaysApply: false
---

# Tasks — Seleção e Gestão de Workspace do Bitbucket

> Decomposição da implementação em tarefas rastreáveis. Cada task mapeia para critérios de aceite (`AC-N`) e possui um gate executável.

## Plano de Implementação

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Adicionar persistência de `default_workspace` e helpers de leitura/escrita no `src/neo/config.py` | AC-2, AC-3, AC-5 | — | `uv run pytest tests/unit/test_config.py -v` | done |
| 2 | Estender `BitbucketClient` para retornar lista completa de workspaces do usuário em DTOs Pydantic | AC-1, AC-3 | 1 | `uv run pytest tests/unit/test_bitbucket_client.py -v` | done |
| 3 | Integrar resolução de workspace com precedência (flag $\rightarrow$ config $\rightarrow$ API) no `BitbucketClient` e comandos `repo`/`commits` | AC-5 | 1, 2 | `uv run pytest tests/unit/test_bitbucket_client.py tests/e2e/test_repo_commands.py -v` | done |
| 4 | Criar módulo de comando `src/neo/commands/workspace.py` com `list`, `current` e `select` (interativo e `--slug`) | AC-1, AC-2, AC-3, AC-4, AC-6 | 2, 3 | `uv run pytest tests/e2e/test_workspace_commands.py -v` | done |
| 5 | Registrar `workspace_app` no CLI raiz `src/neo/cli.py` e atualizar documentação no `README.md` | AC-1, AC-2, AC-3, AC-4 | 4 | `uv run pytest tests/unit/test_cli.py && node scripts/audit-esteira.mjs` | done |

---

## Plano de Testes
- **Unidade:**
  - `tests/unit/test_config.py`: salvar, ler e atualizar `default_workspace` em `config.toml`.
  - `tests/unit/test_bitbucket_client.py`: testar método `list_workspaces()` mockando resposta da API do Bitbucket e validar resolução de workspace com precedência.
- **Aceite (E2E):**
  - `tests/e2e/test_workspace_commands.py`:
    - `test_AC_1_workspace_list`: listagem em modo Rich e `--json`.
    - `test_AC_2_workspace_current`: exibição do workspace ativo e origem.
    - `test_AC_3_workspace_select_by_slug`: seleção direta por slug e validação de slug inexistente.
    - `test_AC_4_workspace_select_interactive`: seleção com simulação de prompt no terminal.
    - `test_AC_5_workspace_precedence`: verificação de precedência ao executar `neo repo list`.
    - `test_AC_6_workspace_without_credentials`: saída amigável sem credenciais.

---

## Divergências (SPEC_DEVIATION)
*(Nenhuma divergência identificada)*

---

## Checklist de Definition of Done
- [x] Todos os ACs verificados pelo gate executável de testes (`uv run pytest`)
- [x] Cobertura de testes mantida $\ge 80\%$ (`uv run pytest --cov=neo` -> 86%)
- [x] Análise estática limpa (`uv run ruff check .` e `uv run mypy src`)
- [x] Auditoria da esteira 100% OK (`node scripts/audit-esteira.mjs`)
- [x] Manual atualizado no `README.md` e `docs/STATE.md` atualizado
