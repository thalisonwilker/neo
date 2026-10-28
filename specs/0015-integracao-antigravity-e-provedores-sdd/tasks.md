---
name: tasks
description: Decomposição e gates da feature 0015-integracao-antigravity-e-provedores-sdd.
alwaysApply: false
---

# Tasks — Integração Antigravity CLI, Configuração Unificada de Agente e Provedores SDD

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e possui um gate executável.

## Plano de Implementação

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Modelar entidades e persistência em `config.py` (seção `[agent]` com chaves `command`, `model`, `sdd-provider`, `adapter`, variáveis `NEO_AGENT_*`, `NEO_SDD_*`), com isolamento estrito de credenciais | AC-4, AC-13, AC-14 | — | `uv run pytest tests/unit/test_agent_config.py -v` | done |
| 2 | Implementar mecanismo de validação de executável em `src/neo/services/agent_validator.py` (`shutil.which`, checagem de `--version`, timeout de 3s, sem shell arbitrário e preservação do valor anterior) | AC-1, AC-2, AC-3 | 1 | `uv run pytest tests/unit/test_agent_validator.py -v` | done |
| 3 | Implementar comandos CLI unificados `neo config agent (set\|get\|list\|unset)` e atualizar `neo config show` com bloco de status do agente | AC-1, AC-4, AC-12, AC-13 | 2 | `uv run pytest tests/e2e/test_agent_config_commands.py -v` | done |
| 4 | Implementar adaptador do Antigravity CLI (`src/neo/integrations/agents/antigravity.py`) com encaminhamento de `--model` e tratamento de combinações incompatíveis | AC-5, AC-6, AC-9, AC-14 | 1 | `uv run pytest tests/unit/test_antigravity_adapter.py -v` | done |
| 5 | Implementar adaptadores de provedores SDD (`spec-driven` e `spec-kit`) e comando `neo agent setup` com verificação prévia, confirmação e idempotência | AC-7, AC-9, AC-11, AC-12 | 1 | `uv run pytest tests/e2e/test_sdd_setup.py -v` | done |
| 6 | Implementar comando `neo agent status` (diagnóstico de binários, versão, modelo, provedor SDD e integridade do projeto, com saída humana e `--json`) | AC-10 | 2, 4, 5 | `uv run pytest tests/e2e/test_agent_status.py -v` | done |
| 7 | Implementar comando `neo agent run` com execução segura via `subprocess.Popen`, argumentos estruturados, diretório explícito, repasse de `SIGINT`/`SIGTERM` e prevenção de processos órfãos | AC-5, AC-6, AC-8, AC-9, AC-14, AC-15 | 4, 5 | `uv run pytest tests/e2e/test_agent_run.py -v` | done |
| 8 | Atualizar documentação MkDocs (`docs/cli/agent.md`, `docs/configuration.md`, `docs/getting-started.md`, `docs/glossary.md`, `docs/architecture/context-map.md`, `mkdocs.yml`), cobrindo guia do Antigravity e provedores SDD | AC-16 | 3, 5, 6, 7 | `uv run --group docs mkdocs build --strict` | done |
| 9 | Executar todos os gates finais de qualidade (Pytest >= 80%, Ruff check & format, Mypy estrito, auditoria da esteira e eval de fidelidade) | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, AC-14, AC-15, AC-16 | 8 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run ruff format --check . && uv run mypy src && node scripts/audit-esteira.mjs . && node scripts/eval-spec-fidelity.mjs .` | done |

---

## Plano de Testes

- **Unidade (`tests/unit/`):**
  - `test_agent_config.py`: CRUD da seção `[agent]` (`command`, `model`, `sdd-provider`, `adapter`), aliases `agent-code`/`sdd`, resolução de precedência (CLI > ENV > config > default), isolamento de credenciais.
  - `test_agent_validator.py`: validação com `which`, execução de `--version`, teste de timeout (3s), comando ausente (código 2), preservação do valor anterior.
  - `test_antigravity_adapter.py`: montagem da linha de comando com `--model`, validação de argumentos, tratamento de erro de compatibilidade.
- **Aceite E2E (`tests/e2e/`):**
  - `test_agent_config_commands.py`: teste de `neo config agent set <chave> <valor>`, `neo config agent get`, `neo config agent list`, `neo config agent unset` e `neo config show` (humano e `--json`).
  - `test_agent_status.py`: teste de `neo agent status` com binário instalado, ausente e modo `--json`.
  - `test_sdd_setup.py`: teste de `neo agent setup` para `spec-driven` e `spec-kit`, verificando idempotência e não-duplicação de arquivos.
  - `test_agent_run.py`: simulação de `neo agent run` com mock de subprocesso, verificação de repasse de argumentos, flags de override, tratamento de `SIGINT` e códigos de saída.

---

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência registrada.

---

## Checklist de Definition of Done
- [x] Todos os 16 ACs verificados pelos gates executáveis de teste
- [x] Cobertura >= 80% (`uv run pytest --cov=neo --cov-fail-under=80`)
- [x] Análise estática limpa (`uv run ruff check .`, `uv run ruff format --check .` e `uv run mypy src`)
- [x] Nenhum segredo ou token do Antigravity gravado ou exibido pelo Neo
- [x] Subprocessos executados sem `shell=True` e com repasse de sinais
- [x] Documentação MkDocs, glossário e context-map atualizados (`mkdocs build --strict` verde)
- [x] Auditoria da esteira 100% OK (`node scripts/audit-esteira.mjs .` e `node scripts/eval-spec-fidelity.mjs .`)
- [x] `docs/STATE.md` atualizado
