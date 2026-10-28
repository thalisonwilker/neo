---
name: product
description: PRD-lite da integração com Antigravity CLI e provedores SDD via neo config agent e neo agent.
alwaysApply: false
---

# Product — Integração com Antigravity CLI e Provedores SDD

> **Tier:** arquitetural · **Status:** aprovado · **Dono:** Thalyson

## Problema

Desenvolvedores que utilizam o Neo no terminal precisam abrir manualmente ferramentas ou interfaces gráficas externas para acionar agentes de IA de codificação. Ao mesmo tempo, diferentes times adotam diferentes metodologias de Spec-Driven Development (como a esteira `spec-driven` com regras no repositório ou o `spec-kit` com a CLI `specify`).

Falta ao Neo uma interface unificada para:
1. Configurar de forma coesa o executável do agente (`command`), o modelo (`model`) e a ferramenta SDD (`sdd-provider`) sob um mesmo contexto de agente (`neo config agent`).
2. Diagnosticar a disponibilidade dos binários antes da execução (`neo agent status`).
3. Iniciar sessões do agente com o modelo correto e as skills/instruções do projeto carregadas (`neo agent run`).

## Para quem

Desenvolvedores de software que utilizam o terminal como ambiente primário de trabalho e desejam acelerar a escrita de código orientada por especificações com agentes autônomos de IA.

## Resultado esperado / métrica de sucesso

- **Coesão de Interface:** Configurar todo o ecossistema de agentes em uma gramática consistente (`neo config agent set <chave> <valor>`).
- **Tempo de inicialização e contexto:** Iniciar uma sessão do Antigravity no contexto do projeto com um único comando (`neo agent run`).
- **Idempotência e Segurança:** Zero falhas de injeção de shell, zero perda acidental de personalizações em `AGENTS.md` ou `.agents/skills/`, e validação prévia de executáveis antes da persistência.

## Goals

- Configurar unificadamente via `neo config agent`: `command`, `model`, `sdd-provider` e `adapter`.
- Validar se o executável do agente existe no PATH e responde antes de salvar a configuração.
- Suportar o Google Antigravity CLI (`agy`) com seleção de modelo via `--model`.
- Suportar os provedores SDD `spec-driven` e `spec-kit` com preparação idempotente (`neo agent setup`).
- Oferecer diagnóstico de dependências via `neo agent status` (com `--json`).
- Suportar overrides pontuais via flags na execução sem alterar configurações salvas.

## Non-goals

- Implementar outros agentes de codificação (como Claude Code ou Cursor CLI) neste incremento.
- Realizar chamadas diretas a APIs REST de LLMs (o Neo delega a execução ao binário do agente).
- Orquestrar a execução autônoma do ciclo completo de SDD.
- Alterar ou migrar automaticamente as especificações ou a esteira SDD do próprio Neo.

## Riscos / premissas

- **Premissa:** O usuário possui o binário do Antigravity CLI (`agy`) instalado ou acessível no PATH para execução interativa.
- **Mitigação:** `neo agent status` e a validação em `neo config agent set command` detectam ausência e instruem a instalação oficial.
