---
name: architecture-overview
description: Arquitetura consolidada do Neo nos 5 eixos + segurança e operacional.
alwaysApply: false
---

# Arquitetura do Sistema — Neo

> Visão consolidada do sistema pelos 5 eixos (+ segurança e operacional). O detalhe vive nos ADRs linkados e diagramas.

## 1. Tech stack
- **Linguagem & Runtime:** Python >= 3.13.
- **CLI & Parsing:** Typer com validação baseada em type hints nativos.
- **Gerenciador de Dependências:** `uv` com suporte a `pyproject.toml` e lockfiles determinísticos.
- **UX & Saída:** Rich para saída visual interativa no terminal.
- **HTTP Client:** `httpx` para consumo de APIs REST com suporte a sincronia e assincronia.
- **Segurança de Credenciais:** `keyring` para integração com chaveiros nativos de SO.
- **Agente de Codificação:** Google Antigravity CLI (`agy`) com suporte a modelos Gemini e orquestração SDD.
- Decisões detalhadas: [ADR-0002](adr/0002-tech-stack-core.md) e [ADR-0007](adr/0007-integracao-agente-antigravity-e-sdd.md).

## 2. Arquitetura base
- **Estilo:** Monolito Modular orientado a DDD tático.
- **Camadas:**
  - `commands/`: Controladores de CLI e formatação de saída (Typer + Rich/JSON) para `git`, `tasks`, `agent` e `config`.
  - `services/`: Regras de negócio, validação de agentes (`agent_validator.py`) e orquestração de análise contextual.
  - `integrations/`: Camada Anti-Corrupção (ACL), contrato comum `GitProviderProtocol` e clientes de APIs externas (GitHub, Bitbucket, Shortcut, Antigravity).
  - `config.py`: Gestão de preferências em `~/.config/neo/config.toml` e credenciais seguras em Keyring.
- Mapa de contextos: [context-map.md](context-map.md) · Diagramas: [diagrams.md](diagrams.md)
- Decisões detalhadas: [ADR-0003](adr/0003-arquitetura-modular-e-integracoes.md) e [ADR-0007](adr/0007-integracao-agente-antigravity-e-sdd.md).

## 3. Infra & Distribuição
- **Empacotamento:** Pacote Python padrão com entrypoint de console `neo = "neo.cli:app"` publicado no PyPI (`neo-cmd`).
- **Ambientes:** Local (desenvolvimento do usuário) e CI (GitHub Actions).
- **Instalação:** Via `uv tool install neo-cmd` ou `pipx install neo-cmd` para isolamento de ambiente.
- Decisão detalhada: [ADR-0002](adr/0002-tech-stack-core.md).

## 4. Qualidade
- **Linters & Formatters:** `ruff check` e `ruff format` para análise estática ultra rápida.
- **Type Checking:** `mypy` configurado em modo estrito (`strict = true`).
- **Testes:** `pytest` com `pytest-cov` e `respx` para mocks de requisições HTTP externas.
- **Documentação Estrita:** Validação de links e compilação do MkDocs com `uv run mkdocs build --strict` e teste de paridade de comandos (`test_docs_parity.py`).
- **Definition of Done (DoD):** Comandos e gates descritos em [TESTING.md](../engineering/TESTING.md).
- Decisão detalhada: [ADR-0005](adr/0005-padroes-de-qualidade-e-testes.md).

## 5. Observabilidade & UX
- **UX Visual:** Tabelas estilizadas, painéis e spinners de progresso com Rich.
- **Modo Script/Automação:** Flag global `--json` para emissão de JSON limpo no stdout com códigos de saída semânticos (`0` a `5`).
- **Erros Amigáveis:** Captura de exceções conhecidas com instruções claras de correção.
- **Debug:** Flag `--verbose` para inspeção de requisições e payloads sem exposição de segredos.
- Decisão detalhada: [ADR-0006](adr/0006-observabilidade-e-ux-cli.md).

## 6. Segurança
- Armazenamento primário de tokens no Keyring seguro do sistema operacional (macOS Keychain, Linux Secret Service, Windows Credential Manager).
- Fallback restrito para arquivo `~/.config/neo/credentials.toml` com permissões `0600`.
- Suporte a variáveis de ambiente para ambientes não-interativos e CI/CD (`NEO_GITHUB_TOKEN`, `NEO_BITBUCKET_TOKEN`, `SHORTCUT_API_TOKEN`).
- Operações de alteração de estado exigem confirmação explícita ou flag `--yes`.
- O Neo **nunca** armazena ou solicita tokens de IA para o Antigravity CLI (isolamento nativo em `~/.gemini/`).
- Decisão detalhada: [ADR-0004](adr/0004-gestao-de-credenciais-e-seguranca.md).

## 7. Operacional
- Operação puramente client-side na máquina do usuário.
- Comunicação direta via HTTPS com APIs oficiais do GitHub (`api.github.com`), Bitbucket (`api.bitbucket.org`) e Shortcut (`api.app.shortcut.com`).
- Sem servidores intermediários, coletores de telemetria ou armazenamento de código do usuário em nuvem do Neo.
