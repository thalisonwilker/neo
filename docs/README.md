---
name: project-home
description: Mapa do projeto Neo — índice navegável com link para cada artefato (onde estamos, produto, arquitetura, engenharia, specs, glossário). Porta de entrada de docs/. Gerado/atualizado no /kickoff. Puxe quando precisar achar onde algo mora.
alwaysApply: false
---

# Neo — Mapa do Projeto

> **Porta de entrada da documentação.** Um índice navegável de "onde está cada coisa" — não duplica conteúdo, apenas **aponta** para o doc certo. Gerado no `/kickoff`.

**One-liner do produto:** Assistente pessoal extensível executado pela linha de comando para reduzir tarefas manuais, organizar informações e apoiar decisões com autonomia.  
**Status:** MVP Greenfield (Fundação & Trabalho)

## 🧭 Onde estamos agora
- **Memória de trabalho** (onde paramos, próximo passo, bloqueios) → [STATE.md](STATE.md)
- **Aprendizados & gotchas** (staging volátil que se auto-poda) → [lessons.md](lessons.md)
- **Roadmap** (Now / Next / Later) → [product/roadmap.md](product/roadmap.md)

## 🎯 Produto — por quê e para quem
- **Visão & escopo** (North Star, personas, o que É/NÃO É) → [product/vision.md](product/vision.md)
- **Stakeholders** (matriz de influência × interesse) → [product/stakeholders.md](product/stakeholders.md)
- **Jornadas** (fluxos de uso e oportunidades) → [product/journeys.md](product/journeys.md)
- **Funcionalidades** (inventário classificado e sequenciamento de ondas) → [product/features.md](product/features.md)
- **MVP canvas** (hipóteses e critérios de sucesso da Onda 1) → [product/mvp-canvas.md](product/mvp-canvas.md)

## 🏛️ Arquitetura — como, no nível de sistema
- **Overview** (os 5 eixos + segurança + operacional) → [architecture/overview.md](architecture/overview.md)
- **Context map** (bounded contexts e relações DDD) → [architecture/context-map.md](architecture/context-map.md)
- **Diagramas** (C4 context e fluxo de análise em Mermaid) → [architecture/diagrams.md](architecture/diagrams.md)
- **ADRs** (decisões duráveis e imutáveis) → [architecture/adr/](architecture/adr/)
  - [ADR-0001: Record Architecture Decisions](architecture/adr/0001-record-architecture-decisions.md)
  - [ADR-0002: Tech Stack Principal](architecture/adr/0002-tech-stack-core.md)
  - [ADR-0003: Arquitetura Modular e Isolamento de Integrações](architecture/adr/0003-arquitetura-modular-e-integracoes.md)
  - [ADR-0004: Gestão de Credenciais e Segurança Operacional](architecture/adr/0004-gestao-de-credenciais-e-seguranca.md)
  - [ADR-0005: Padrões de Qualidade de Código, Tipagem e Testes](architecture/adr/0005-padroes-de-qualidade-e-testes.md)
  - [ADR-0006: Observabilidade e UX Visual no Terminal](architecture/adr/0006-observabilidade-e-ux-cli.md)

## 🛠️ Engenharia — como construímos
- **Testes e quality gates** (comandos e Definition of Done) → [engineering/TESTING.md](engineering/TESTING.md)
- **Camada agêntica** (rules, subagents, skills, workflows) → [engineering/agentic-layer.md](engineering/agentic-layer.md)
- **Métricas de entrega** → [engineering/metrics.md](engineering/metrics.md)

## 📐 Specs — o contrato de cada feature
> A pasta [`specs/`](../specs/) é a fonte viva; atualize ao criar features com `/nova-feature`.
- [`specs/0001-exemplo-cota-de-uso/`](../specs/0001-exemplo-cota-de-uso/spec.md) — exemplo de referência da esteira
- [`specs/0002-fundacao-cli-e-configuracao/`](../specs/0002-fundacao-cli-e-configuracao/spec.md) — fundação da CLI, Rich, flag --json e Keyring (ativa)

## 📖 Linguagem & convenções
- **Glossário** (linguagem ubíqua) → [glossary.md](glossary.md)
- **Instruções p/ Agentes (Antigravity / Codex)** → [../AGENTS.md](../AGENTS.md)
- **Manual da esteira SDD** (fluxo, tiers, DoR/DoD) → [../README.md](../README.md)
