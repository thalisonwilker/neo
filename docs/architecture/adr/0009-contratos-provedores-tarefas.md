---
name: adr-0009
description: Contratos e localização dos adapters dos provedores de tarefas.
alwaysApply: false
---

# ADR-0009: Contratos e adapters de provedores de tarefas

- **Status:** aceito
- **Data:** 2026-11-04
- **Decisores:** mantenedor do Neo

## Contexto

O ADR-0003 situa clientes de APIs em `integrations/`. A feature 0031 organiza os provedores de tarefas em `services/tasks/`, com contratos comuns e adapters agrupados em `services/tasks/api/`, conforme o design aprovado. A organização física precisa preservar a direção lógica das dependências.

## Decisão

Os contratos e modelos comuns de tarefas ficam em `services/tasks/`; os adapters ficam em `services/tasks/api/`. Contratos e modelos não dependem de implementações concretas, que dependem dos contratos. A composição dos adapters ocorre na borda da aplicação. Esta decisão substitui apenas a localização física de adapters de tarefas indicada no ADR-0003; seu isolamento como camada anticorrupção continua válido.

GitHub e Bitbucket permanecem em `integrations/git/`. Foi considerada a localização dos adapters de tarefas em `integrations/`, que seguiria a localização anterior, mas não atenderia à organização solicitada. `Protocol` permite contratos estruturais e mantém o padrão já usado no Git, sem impor herança de uma classe-base.

## Consequências

- **+** Provedores de tarefas ficam agrupados com seus contratos, mantendo o isolamento das APIs.
- **+** Novos adapters podem implementar os contratos sem alterar os consumidores.
- **−** O caminho físico `services/tasks/api/` contém infraestrutura; a regra de dependência deve ser verificada por testes e revisão.
- **−** Capacidades distintas entre provedores exigem contratos opcionais e tratamento explícito.
