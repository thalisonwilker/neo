---
name: domain
description: Modelo DDD da integração com Antigravity CLI e provedores SDD.
alwaysApply: false
---

# Domain Model (DDD) — Integração com Antigravity CLI e Provedores SDD

> **Subdomínio:** Supporting · **Bounded Context:** `Agent & SDD Orchestration`

## Linguagem ubíqua

| Termo | Definição | NÃO confundir com |
|---|---|---|
| **`AgentAdapter`** | Adaptador responsável por traduzir chamadas e validar o executável do agente de codificação | Biblioteca de chamadas HTTP a modelos de linguagem |
| **`AgentCodeCommand`** | Nome do executável do agente no sistema operacional (ex.: `agy`) | Script arbitrário de shell |
| **`ModelIdentifier`** | Identificador de modelo reconhecido pelo agente (ex.: `Gemini 3.8 Flash`) | Provedor de Git ou serviço de tarefas |
| **`SDDProvider`** | Ferramenta ou especificação de esteira SDD (`spec-driven` ou `spec-kit`) | Provedor de repositório Git (`github`, `bitbucket`) |
| **`AgentSession`** | Sessão de execução gerenciada pelo Neo com repasse de sinais e captura de código de saída | Processo daemon em background sem terminal |

## Agregados e Value Objects

### Agregado: `AgentConfiguration` (Raiz: `AgentConfigRoot`)
- **Entidades:**
  - `AgentProfile`: armazena `adapter` (`antigravity`), `command` (`AgentCodeCommand`), `model` (`ModelIdentifier`).
  - `SDDProfile`: armazena `provider` (`SDDProvider`).
- **Value Objects:**
  - `AgentCodeCommand`: string não-vazia, sem operadores de shell, sanitizada.
  - `ModelIdentifier`: string não-vazia identificando o modelo.
  - `SDDProvider`: Enum (`SPEC_DRIVEN`, `SPEC_KIT`).
- **Invariantes:**
  - `command` só pode ser persistido após validação positiva de presença no PATH e resposta a verificação básica (timeout controlado).
  - Trocar `sdd_provider` não aciona remoção de diretórios existentes.
  - Credenciais do agente nunca são armazenadas nos perfis do Neo.

## Eventos de domínio

| Evento | Disparado quando | Quem reage |
|---|---|---|
| `AgentConfigUpdated` | Uma chave de `agent-code`, `model` ou `sdd-provider` é alterada com sucesso | Módulo de configuração e logs de auditoria |
| `AgentSessionStarted` | A sessão do agente é iniciada em um diretório | Handlers de processo para monitoramento de sinais |
| `AgentSessionTerminated` | A sessão do agente é encerrada ou interrompida | Limpeza de subprocesso para evitar processos órfãos |

## Relações com outros contextos

```text
[CLI & Commands]
      │
      ├──(Dependency)──► [Agent & SDD Orchestration]
      │                         │
      │                         ├──(Port/Adapter)──► [Antigravity CLI (agy)]
      │                         └──(Port/Adapter)──► [SDD Providers (spec-driven / spec-kit)]
      │
      └──(Dependency)──► [Configuration & Secrets]
```

