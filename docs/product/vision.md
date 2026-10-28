---
name: vision
description: Visão do produto — problema, personas, North Star do Neo.
alwaysApply: true
---

# Visão do Produto — Neo (Um assistente pessoal via linha de comando para organizar a vida de um dev)

> "Compreenda seus sistemas. Seja dono das suas escolhas."
> Gerado no kickoff (Lean Inception). Documento vivo: revisar a cada pivô relevante.

## Elevator pitch
> Para **desenvolvedores e profissionais de tecnologia** que **perdem tempo alternando entre interfaces web desconexas (Bitbucket, Shortcut, etc.) e executando tarefas manuais repetitivas**, o **Neo** é um **assistente pessoal extensível executado pela linha de comando (CLI)** que **centraliza operações, correlaciona dados de trabalho e automatiza fluxos com contexto e autonomia**.
> Diferente de **scripts isolados ou CLIs proprietárias de ferramentas únicas**, o Neo **unifica múltiplos serviços em uma experiência única, modular, com análise cruzada e preservação estrita do controle do usuário**.

## O produto É / NÃO É / FAZ / NÃO FAZ

| É | NÃO É |
|---|---|
| Um assistente de comando extensível e modular em Python (Typer) | Um bot autônomo sem supervisão que altera sistemas sem consentimento |
| Uma central de apoio a decisões e investigação com dados correlacionados | Um substituto completo das UIs do Bitbucket ou Shortcut |
| Um orquestrador que devolve tempo, clareza e autonomia ao usuário | Uma coleção desordenada de scripts bash descartáveis |

| FAZ | NÃO FAZ |
|---|---|
| Consulta, cria, lista e clona repositórios e analisa commits no Bitbucket | Não executa ações destrutivas sem confirmação explícita do usuário |
| Pesquisa, lista e analisa stories, cards e bugs no Shortcut | Não armazena tokens ou credenciais em texto puro desprotegido |
| Correlaciona demandas (Shortcut) com branches, commits e PRs (Bitbucket) | Não engessa o fluxo de trabalho obrigando uso de um único serviço |
| Expande-se por novos domínios (estudo, treinos, rotas, agenda, IA) | Não sequestra a tomada de decisão do usuário |

## Personas

| Persona | Quem é / contexto | Dor principal | O que espera do produto |
|---|---|---|---|
| **Engenheiro de Software Focado** | Desenvolvedor que lida com múltiplos repositórios, cards de tarefas e bugs diariamente | Perda de foco e tempo ao saltar entre abas do browser para ver stories e PRs | Consultar e relacionar cards e commits direto do terminal com comandos rápidos |
| **Tech Lead / Investigador de Incidentes** | Liderança técnica investigando causa-raiz de bugs ou progresso de entregas | Dificuldade em cruzar quem alterou o que e qual card motivou aquela alteração | Análise rápida cruzada entre bug reportado no Shortcut e histórico de alterações no Bitbucket |
| **Power User Produtivo** | Profissional que valoriza automação via terminal para trabalho e vida pessoal | Fragmentação de ferramentas e falta de autonomia sobre dados e rotinas | Uma CLI confiável que evolua para apoiar estudos, rotinas e automações pessoais |

## North Star / objetivo
- **North Star metric:** Tempo economizado por semana em operações manuais de consulta e investigação cruzada (estimativa de redução de 70% no chaveamento de contexto web/terminal).
- **Baseline → Alvo:** 0 comandos unificados (100% manual na web) → Gestão e investigação completa de repositórios e stories via Neo em < 5 segundos por operação.
- **Objetivos do MVP:**
  1. Integrar APIs do Bitbucket e Shortcut com autenticação segura.
  2. Oferecer comandos ergonômicos para listagem, busca, clonagem e análise de repos e stories.
  3. Prover comando de investigação cruzada (`neo story analyze <id>`, `neo bug investigate <id>`).

## Premissas e hipóteses a validar
- [ ] A centralização de Bitbucket + Shortcut no terminal reduz sensivelmente a fadiga de alternância de contexto (context-switching).
- [ ] A correlação automática entre branch/commit e story ID elimina o trabalho investigativo manual em incidentes.
- [ ] A arquitetura modular permitirá plugar futuros módulos (`study`, `cycling`, `ask`) sem refatorar o núcleo.
