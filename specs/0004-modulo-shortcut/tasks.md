---
name: tasks
description: Decomposição e gates da feature 0004-modulo-shortcut.
alwaysApply: false
---

# Tasks — 0004-modulo-shortcut

> Decomposição da implementação das 5 funções do Shortcut via REST API v3.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Modelar DTOs tipados da API v3 (`ShortcutMember`, `ShortcutStory`, `StoryAnalysis`) em `src/neo/integrations/shortcut_models.py` | AC-1 a AC-5 | — | `uv run mypy src` | done |
| 2 | Implementar cliente HTTP v3 em `src/neo/integrations/shortcut.py` com as 5 funções de API | AC-1 a AC-6 | 1 | `uv run pytest tests/unit/test_shortcut_client.py -v` | done |
| 3 | Implementar subcomando `neo story` (`whoami`, `list`, `search`, `show`, `analyze`) em `src/neo/commands/story.py` | AC-1 a AC-6 | 2 | `uv run pytest tests/e2e/test_story_commands.py -v` | done |
| 4 | Registrar `story_app` em `src/neo/cli.py` e validação de qualidade estática e cobertura | AC-1 a AC-6 | 3 | `uv run ruff check . && uv run mypy src && uv run pytest --cov=neo` | done |

## Plano de teste
- **Unidade:**
  - `tests/unit/test_shortcut_client.py`: Testa as 5 funções contra `https://api.app.shortcut.com/api/v3` usando `respx`, validando headers `Shortcut-Token`, parsing de stories, tratamentos de erro 401 e 404.
- **Aceite (E2E):**
  - `tests/e2e/test_story_commands.py`: Executa `neo story whoami`, `list`, `search`, `show`, `analyze` em formato Rich e JSON com `CliRunner`.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência identificada.

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável (`uv run pytest tests/e2e/test_story_commands.py`)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Análise estática limpa (`ruff check`, `mypy src`)
- [x] Cobertura de testes ≥ 80% (83.92% atingido)
- [x] `docs/STATE.md` atualizado

