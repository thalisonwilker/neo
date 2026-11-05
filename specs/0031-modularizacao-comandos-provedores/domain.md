---
name: domain
description: Modelo dos contratos comuns de provedores Git e de tarefas.
alwaysApply: false
---

# Domain Model — Modularização de comandos e provedores

> **Status:** aprovado. Este modelo define os termos e relações; não altera os comportamentos existentes.

## Bounded contexts

- **Git Integration** (supporting): acesso uniforme às operações Git remotas, com GitHub e Bitbucket como integrações existentes.
- **Shortcut Integration** (supporting): acesso às stories e capacidades existentes do Shortcut. O contrato comum permite acrescentar outros provedores de tarefas futuramente, sem declarar um novo bounded context nesta entrega.
- **CLI & Commands** (generic): recebe argumentos, usa os contratos e apresenta resultados. **Configuration & Secrets** fornece configuração e credenciais.

## Linguagem ubíqua

| Termo | Significado nesta feature | NÃO confundir com |
|---|---|---|
| Provider / Provedor Git | Plataforma Git acessada pelo contrato `GitProvider`; atualmente GitHub ou Bitbucket | Provedor de tarefas |
| Provedor de tarefas | Serviço acessado pelo contrato `TaskProvider`; atualmente Shortcut | Provedor Git |
| Workspace | Escopo proprietário dos repositórios Git, conforme o glossário | Diretório local ou workspace de um serviço de tarefas |
| Repository, Commit e Pull Request | Conceitos Git definidos no glossário e traduzidos a modelos comuns | Objetos brutos de uma API específica |
| Story / Card | Unidade de trabalho atualmente gerenciada no Shortcut | Item de checklist ou ID associado a repositório local |
| Task | No contexto Git, ID associado a um repositório local; no contrato `TaskProvider`, o nome do serviço não altera a definição existente de Story / Card | Item de checklist do Shortcut |
| Capacidade opcional | Operação disponível somente em determinados provedores, como iterações ou workflows | Garantia de suporte por todos os provedores |

O glossário atual limita **Provider** a Git e define **Story / Card** no Shortcut. A inclusão de **Provedor de tarefas** e **Capacidade opcional** é proposta para revisão antes de promover os termos ao glossário global. Evitar renomear Story / Card ou Task sem uma decisão explícita, pois já possuem significados distintos.

## Modelos e invariantes

- Workspace, Repository, Commit e Pull Request são representações tipadas de dados remotos. Os adapters preservam os campos necessários aos comandos atuais e traduzem os formatos de cada API.
- Story / Card, membro, comentário, item de checklist, iteração e estado de workflow são representações dos dados necessários aos fluxos atuais de tarefas. Sua forma comum será definida na spec a partir dos campos efetivamente utilizados.
- Uma credencial pertence ao serviço configurado e continua sendo obtida pelos mecanismos existentes; ela não integra os modelos de saída nem os logs.
- A seleção de provedor não altera a precedência atual de configuração e contexto. A ausência de uma capacidade é explícita e não pode simular sucesso.
- Os recursos remotos pertencem aos respectivos serviços externos. Esta refatoração não propõe novas fronteiras transacionais, agregados persistidos no Neo nem eventos de domínio.

## Relações entre contextos

`CLI & Commands` consome os contratos de Git e tarefas; `Configuration & Secrets` fornece as credenciais à composição; os adapters funcionam como camada anticorrupção entre os contratos e as APIs externas. A análise existente mantém a correlação entre Story / Card e Git.

O mapa de contextos será atualizado após aprovação deste modelo e da decisão arquitetural, para refletir os novos caminhos e contratos sem antecipar código ainda não implementado.
