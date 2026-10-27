---
name: adr-0003
description: Decisão sobre arquitetura modular e desacoplamento de integrações.
alwaysApply: false
---

# ADR-0003: Arquitetura Modular e Isolamento de Integrações

- **Status:** aceito
- **Data:** 2026-10-27
- **Decisores:** Time do Projeto Neo

## Contexto
O Neo nasce integrando Bitbucket e Shortcut, mas sua visão exige evolução para múltiplos outros domínios de trabalho (`work`), estilo de vida (`study`, `fitness`, `cycling`, `fishing`, `agenda`) e inteligência artificial (`ask`). Acoplar a lógica dos comandos diretamente aos clientes de API tornaria o código frágil e inviabilizaria testes e extensões.

## Decisão
Vamos adotar um **Monolito Modular baseado em DDD tático**, estruturado em:
```text
src/neo/
├── cli.py                     # Entrypoint e orquestração de subapps Typer
├── config.py                  # Gerenciador de configurações e perfis
├── commands/                  # Controladores de CLI por domínio (repo, story, bug, etc.)
│   ├── repo.py
│   ├── commits.py
│   └── story.py
├── integrations/              # Clientes de borda isolados (Anti-Corruption Layer)
│   ├── bitbucket.py
│   └── shortcut.py
└── services/                  # Lógica de negócio e correlação pura
    └── analysis.py
```

Regras arquiteturais:
1. Comandos em `commands/` dependem de `services/` ou de interfaces em `integrations/`, nunca manipulando requisições HTTP brutas.
2. Clientes em `integrations/` convertem respostas de APIs de terceiros para modelos puros tipados (Pydantic/Dataclasses) para proteger o núcleo do sistema (ACL).
3. `services/analysis.py` implementa a correlação cruzada sem conhecer detalhes de transporte de rede.

## Consequências
- **+** Módulos independentes: adicionar um novo comando ou serviço não afeta os existentes.
- **+** Testabilidade total: clientes de integração podem ser mockados em testes unitários.
- **−** Pequeno boilerplate inicial com DTOs/modelos entre a resposta da API e o comando.
