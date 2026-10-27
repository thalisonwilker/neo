---
name: features
description: Inventário de funcionalidades do Neo classificadas e sequenciadas em ondas.
alwaysApply: false
---

# Funcionalidades do Produto — Neo

> Brainstorm + classificação + **sequenciamento** (Lean Inception). Cada funcionalidade nasce de uma jornada (`journeys.md`). A **Onda 1 = MVP** (`mvp-canvas.md`) e alimenta o `roadmap.md`.

## Inventário e classificação

| # | Funcionalidade | Jornada | Esforço | Valor | Confiança | UX | Onda |
|---|----------------|---------|---------|-------|-----------|-----|------|
| 1 | Configuração e autenticação segura (Keyring + config.toml) | Fundação | baixo | alto | alta | alta | 1 |
| 2 | Bitbucket: Listar e buscar repositórios (`neo repo list/search`) | Jornada 3 | baixo | alto | alta | alta | 1 |
| 3 | Bitbucket: Clonar repositório (`neo repo clone <nome>`) | Jornada 3 | baixo | alto | alta | média | 1 |
| 4 | Bitbucket: Criar repositório (`neo repo create <nome>`) com confirmação | Jornada 3 | médio | médio | alta | média | 1 |
| 5 | Bitbucket: Consultar commits e branches (`neo commits search`) | Jornadas 2 e 3 | médio | alto | alta | alta | 1 |
| 6 | Shortcut: Listar stories (`neo story list [--mine]`) | Jornada 1 | baixo | alto | alta | alta | 1 |
| 7 | Shortcut: Exibir e analisar story (`neo story show/analyze <id>`) | Jornada 1 e 2 | médio | alto | alta | alta | 1 |
| 8 | Análise Cruzada: Investigação de Bug (`neo bug investigate <id>`) | Jornada 2 | médio | alto | média | alta | 1 |
| 9 | Flag global `--json` para automação Unix em todos os comandos | Transversal | baixo | alto | alta | alta | 1 |
| 10 | Módulo `work`: Planejamento semanal e métricas de demandas | Futuro | médio | médio | média | média | 2 |
| 11 | Módulos pessoais: `study`, `fitness`, `cycling`, `fishing`, `agenda` | Futuro | alto | médio | baixa | média | 2 |
| 12 | Camada de IA: `neo ask "comando em linguagem natural"` | Futuro | alto | alto | média | alta | 3 |

## Sequenciador (ondas)

- **Onda 1 (MVP — Trabalho & Desenvolvimento):**
  - Fundação: CLI Typer + Configuração de tokens segura (Keyring).
  - Módulo Bitbucket: `repo list`, `repo search`, `repo clone`, `repo create`, `commits search`.
  - Módulo Shortcut: `story list`, `story show`, `story analyze`.
  - Serviço de Análise Cruzada: `bug investigate <id>` (Shortcut ↔ Bitbucket).
  - *Hipótese validada:* Redução substancial do context-switching do desenvolvedor e ganho expressivo de velocidade em investigações de incidentes.

- **Onda 2 (Extensibilidade e Vida Pessoal):**
  - Módulos `work` (planejamento) e extensões de estilo de vida (`study`, `fitness`, `cycling`, `fishing`, `agenda`).

- **Onda 3 (Agente de IA e Linguagem Natural):**
  - Módulo `neo ask` conectando modelos locais (via Ollama/Llama) ou APIs externas para automações complexas com confirmação humana explícita.
