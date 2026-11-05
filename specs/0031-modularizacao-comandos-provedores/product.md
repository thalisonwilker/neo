---
name: product
description: Objetivos da modularização de comandos e provedores Git e de tarefas.
alwaysApply: false
---

# Product — Modularização de comandos e provedores

> **Tier:** arquitetural · **Status:** aprovado · **Dono:** mantenedor do Neo

## Problema
Os comandos agrupam várias ações em arquivos extensos e as integrações expõem detalhes de provedores aos consumidores. Isso dificulta localizar responsabilidades e acrescentar provedores de Git e tarefas.

## Para quem
Mantenedores e desenvolvedores que implementam comandos e integrações do Neo.

## Resultado esperado / métrica de sucesso
- Baseline: comandos de Git, tarefas e finanças concentram múltiplas ações em arquivos únicos; tarefas dependem diretamente do Shortcut.
- Alvo proposto: comandos organizados pela hierarquia da CLI, provedores existentes acessados por contratos comuns e testes de regressão existentes aprovados.

## Goals
- Modularizar os comandos em arquivos de responsabilidade menor, acompanhando a hierarquia da CLI.
- Definir contratos de provedores Git e de tarefas e organizar os respectivos adapters.
- Preservar o comportamento existente da CLI, configurações e credenciais durante a migração.
- Facilitar a implementação futura de provedores de tarefas, incluindo Trello.

## Non-goals propostos
- Alterar a gramática ou o comportamento público existente da CLI.
- Disponibilizar integração funcional com Trello sem definir e aprovar seu escopo e contrato.
- Adicionar novas funcionalidades de negócio aos provedores existentes.

## Riscos / premissas
- A proposta coloca adapters de tarefas em `services/tasks/api`, conforme solicitado; o design precisa resolver a dependência entre contrato e implementação em relação à regra de camadas do projeto.
- Recursos variam entre provedores; as capacidades opcionais e os erros correspondentes precisam ser definidos no design.
- A aprovação da proposta de produto e design precede a implementação e a criação de uma spec com critérios de aceite verificáveis.
