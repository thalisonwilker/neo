---
name: roadmap
description: Prioridades do Neo em horizontes Now/Next/Later.
alwaysApply: true
---

# Roadmap — Neo (Personal Command Assistant)

> Plano incremental para implementar com o time. Gerado no kickoff.
> Princípio: **quick wins de baixo risco primeiro** para gerar tração e confiança.

## Objetivo do roadmap
Entregar a fundação da CLI e o MVP completo de integração de trabalho (Bitbucket + Shortcut + Análise Cruzada de Bugs) com qualidade estrita e segurança de credenciais nos primeiros ciclos de desenvolvimento.

## Horizontes

### 🟢 Agora (Onda 1 — MVP: Fundação & Trabalho)

| # | Item | Valor | Esforço | Dono | Depende de | Pronto quando |
|---|---|---|---|---|---|---|
| 1 | **Fundação do Neo:** Typer CLI, Rich formatting, flag `--json`, config e Keyring seguro | Alto | Baixo | Time Neo | — | `neo --help` funcional, `neo config auth` armazena e recupera tokens do Keychain com testes passando |
| 2 | **Módulo Bitbucket:** `neo repo list`, `neo repo search`, `neo repo clone`, `neo commits search` | Alto | Médio | Time Neo | Item 1 | Comandos listam, buscam e clonam repositórios reais com tratamento de erro e testes unitários/mocks |
| 3 | **Módulo Shortcut:** `neo story list [--mine]`, `neo story show <id>`, `neo story analyze <id>` | Alto | Médio | Time Neo | Item 1 | Listagem ergonômica de cards e exibição de detalhes no terminal com flag `--json` e testes |
| 4 | **Serviço de Análise Cruzada:** `neo bug investigate <id>` | Alto | Médio | Time Neo | Itens 2 e 3 | Comando correlaciona card do Shortcut com commits e PRs do Bitbucket e imprime relatório investigativo |
| 5 | **CI e Gates SDD:** GitHub Actions com Ruff, Mypy, Pytest e cobertura | Alto | Baixo | Time Neo | Item 1 | Pipeline verde em todo PR bloqueando regressões |

### 🟡 Próximo (Onda 2 — Extensibilidade & Vida Pessoal)

| # | Item | Valor | Esforço | Dono | Depende de |
|---|---|---|---|---|---|
| 1 | **Módulo `work`:** Planejamento semanal e progresso de demandas de múltiplos boards | Médio | Médio | Time Neo | Onda 1 |
| 2 | **Módulo `study`:** Planos de estudo, revisões espaçadas e notas | Médio | Médio | Time Neo | Onda 1 |
| 3 | **Módulos de Saúde & Esportes:** `fitness` e `cycling` (integração Strava/Garmin) | Médio | Alto | Time Neo | Onda 1 |
| 4 | **Módulos de Lazer & Organização:** `fishing` (marés/condições) e `agenda` | Médio | Médio | Time Neo | Onda 1 |

### ⚪ Depois (Onda 3 — Camada de IA & Linguagem Natural)

| # | Item | Por que esperar |
|---|---|---|
| 1 | **Comando `neo ask`:** Interface em linguagem natural conectando LLMs locais (Ollama) ou provedores remotos | Exige que todos os módulos de comandos e integrações estejam estáveis como ferramentas (tools) para o agente |
| 2 | **Automações pró-ativas com confirmação humana:** Sugestões contextuais baseadas em agenda e cards | Depende do módulo de IA e coleta segura de histórico local |

## Como rodar com o time
- **Cadência de revisão do roadmap:** Semanal a cada entrega de feature SDD.
- **Quem decide prioridade:** Usuário criador / Mantenedor do projeto.
- **Definition of Ready / Done:** Seguir rigorosamente os contratos especificados em cada `spec.md` e `TESTING.md`.
