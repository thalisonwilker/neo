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
| **Analysis & Correlation** | Core | Regras de correlação cruzada entre bugs/demandas e commits/branches | `services/` |
| **Bitbucket Integration** | Supporting | Comunicação HTTP com API do Bitbucket, paginação e mapeamento para modelos do domínio | `integrations/bitbucket.py` |
| **Shortcut Integration** | Supporting | Comunicação HTTP com API do Shortcut, busca de stories e conversão para modelos do domínio | `integrations/shortcut.py` |
| **Configuration & Secrets** | Generic | Leitura de configurações, perfis de ambiente e persistência segura em Keyring | `config.py` |

## Relações entre contextos

```text
[CLI & Commands]
      │
      ├──(Dependency)──► [Analysis & Correlation]
      │                         │
      │                         ├──(ACL)──► [Bitbucket Integration]
      │                         └──(ACL)──► [Shortcut Integration]
      │
      └──(Dependency)──► [Configuration & Secrets]
```

| Upstream | Downstream | Padrão | Por quê |
|---|---|---|---|
| Bitbucket API | Bitbucket Integration | Anti-Corruption Layer (ACL) | Converte respostas da API externa em entidades e DTOs puros do Neo |
| Shortcut API | Shortcut Integration | Anti-Corruption Layer (ACL) | Isola mudanças de schema do Shortcut do restante do sistema |
| Analysis & Correlation | CLI Commands | Open Host Service | Fornece métodos claros de investigação e análise consumidos pelos comandos |
| Configuration & Secrets | Integrations | Dependency | Injeta credenciais seguras e URLs de base nos clientes HTTP |

## Diagramas
Diagramas visuais detalhados em Mermaid disponíveis em [`diagrams.md`](./diagrams.md).
