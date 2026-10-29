---
name: context-map
description: Bounded contexts e relações do Neo.
alwaysApply: false
---

# Context Map — Neo

> Visão DDD estratégica: os bounded contexts do Neo e seus relacionamentos.

## Bounded Contexts

| Contexto | Subdomínio | Responsabilidade | Camada |
|---|---|---|---|
| **CLI & Commands** | Generic | Parsing de argumentos, despacho de comandos Typer e renderização de saída (Rich / JSON) | `commands/` |
| **Analysis & Correlation** | Core | Regras de análise contextual entre histórias do Shortcut e sugestões de Git (branches e commits) | `services/` |
| **GitHub Integration** | Supporting | Comunicação HTTP com API do GitHub via `GitProviderProtocol`, paginação e conversão de DTOs | `integrations/github.py` |
| **Bitbucket Integration** | Supporting | Comunicação HTTP com API do Bitbucket via `GitProviderProtocol`, paginação e conversão de DTOs | `integrations/bitbucket.py` |
| **Shortcut Integration** | Supporting | Comunicação HTTP com API do Shortcut, busca de stories, iterações e workflows | `integrations/shortcut.py` |
| **Agent & SDD Orchestration** | Supporting | Diagnóstico, preparação e invocação do Antigravity CLI (`agy`) e esteiras SDD (`spec-driven` / `spec-kit`) | `services/agent_validator.py`, `integrations/agents/` |
| **Configuration & Secrets** | Generic | Leitura de preferências (`config.toml`), perfis de ambiente e persistência segura em Keyring | `config.py` |

## Relações entre contextos

```text
[CLI & Commands]
      │
      ├──(Dependency)──► [Analysis & Correlation]
      │                         │
      │                         ├──(ACL)──► [Git Providers (GitHub & Bitbucket)]
      │                         └──(ACL)──► [Shortcut Integration]
      │
      ├──(Dependency)──► [Agent & SDD Orchestration]
      │                         │
      │                         ├──(Port/Adapter)──► [Antigravity CLI (agy)]
      │                         └──(Port/Adapter)──► [SDD Providers (spec-driven / spec-kit)]
      │
      └──(Dependency)──► [Configuration & Secrets]
```

| Upstream | Downstream | Padrão | Por quê |
|---|---|---|---|
| GitHub API | GitHub Integration | Anti-Corruption Layer (ACL) | Converte respostas da API do GitHub no contrato comum `GitProviderProtocol` |
| Bitbucket API | Bitbucket Integration | Anti-Corruption Layer (ACL) | Converte respostas da API do Bitbucket no contrato comum `GitProviderProtocol` |
| Shortcut API | Shortcut Integration | Anti-Corruption Layer (ACL) | Isola mudanças de schema do Shortcut do restante do sistema |
| Analysis & Correlation | CLI Commands | Open Host Service | Fornece métodos claros de investigação e análise consumidos pelos comandos |
| Configuration & Secrets | Integrations | Dependency | Injeta credenciais seguras e URLs de base nos clientes HTTP e agentes |

## Diagramas
Diagramas visuais detalhados em Mermaid disponíveis em [`diagrams.md`](./diagrams.md).
