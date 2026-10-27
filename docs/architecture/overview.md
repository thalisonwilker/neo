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
- Decisão detalhada: [ADR-0002](adr/0002-tech-stack-core.md)

## 2. Arquitetura base
- **Estilo:** Monolito Modular orientado a DDD tático.
- **Camadas:**
  - `commands/`: Controladores de CLI e formatação de saída (Typer + Rich/JSON).
  - `services/`: Regras de negócio, orquestração e correlação cruzada de dados (`analysis.py`).
  - `integrations/`: Camada Anti-Corrupção (ACL) e clientes de APIs externas (Bitbucket, Shortcut).
  - `config.py`: Gestão de perfis, ambientes e credenciais.
- Mapa de contextos: [context-map.md](context-map.md) · Diagramas: [diagrams.md](diagrams.md)
- Decisão detalhada: [ADR-0003](adr/0003-arquitetura-modular-e-integracoes.md)

## 3. Infra & Distribuição
- **Empacotamento:** Pacote Python padrão com entrypoint de console `neo = "neo.cli:app"`.
- **Ambientes:** Local (desenvolvimento do usuário) e CI (GitHub Actions).
- **Instalação:** Via `uv tool install .` ou `pipx install .` para isolamento de ambiente.
- Decisão detalhada: [ADR-0002](adr/0002-tech-stack-core.md)

## 4. Qualidade
- **Linters & Formatters:** `ruff check` e `ruff format` para análise estática ultra rápida.
- **Type Checking:** `mypy` configurado em modo estrito.
- **Testes:** `pytest` com `pytest-cov` e `respx` para mocks de requisições HTTP externas.
- **Definition of Done (DoD):** Comandos e gates descritos em [TESTING.md](../engineering/TESTING.md).
- Decisão detalhada: [ADR-0005](adr/0005-padroes-de-qualidade-e-testes.md)

## 5. Observabilidade & UX
- **UX Visual:** Tabelas estilizadas, painéis e spinners de progresso com Rich.
- **Modo Script/Automação:** Flag global `--json` para emissão de JSON limpo no stdout.
- **Erros Amigáveis:** Captura de exceções conhecidas com instruções claras de correção.
- **Debug:** Flag `--verbose` para inspeção de requisições e payloads sem exposição de segredos.
- Decisão detalhada: [ADR-0006](adr/0006-observabilidade-e-ux-cli.md)

## 6. Segurança
- Armazenamento de tokens no Keyring seguro do sistema operacional (macOS Keychain, Linux SecretService).
- Fallback para arquivo `~/.config/neo/config.toml` com permissões `0600`.
- Operações de alteração de estado exigem confirmação explícita ou flag `--yes`.
- Decisão detalhada: [ADR-0004](adr/0004-gestao-de-credenciais-e-seguranca.md)

## 7. Operacional
- Operação puramente client-side na máquina do usuário.
- Comunicação direta via HTTPS com APIs oficiais do Bitbucket (`api.bitbucket.org`) e Shortcut (`api.app.shortcut.com`).
- Sem servidores intermediários ou telemetria invasiva de dados do usuário.
