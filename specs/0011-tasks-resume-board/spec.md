---
name: spec
description: Contrato da feature 0011 — comando `neo tasks resume` com quadro Kanban no terminal (A fazer, Fazendo, Feito) e configuração dinâmica de colunas por serviço.
alwaysApply: true
---

# Spec — Quadro Resumo de Tasks (`neo tasks resume`)

> **Fonte da verdade.** Status: implementado
> Tier: **Pequeno** (`spec.md` + `tasks.md` — evolução do módulo `neo tasks` e integração Shortcut).

## Resumo
Adiciona o comando `neo tasks resume` (e `neo tasks config columns`), que exibe no terminal um quadro estilo Kanban com 3 colunas (**A fazer**, **Fazendo** e **Feito**). Quando as colunas do serviço atual (ex.: Shortcut) ainda não estão configuradas em `config.toml`, o comando consulta os estados do workflow na API do serviço e conduz a configuração interativa permitindo mapear **uma ou mais colunas do board** para cada etapa.

---

## Critérios de aceite

### AC-1: Verificação e configuração automática de colunas por serviço no `neo tasks resume`
- **Dado** que o usuário possui credencial válida para o serviço de tasks (`shortcut` por padrão) mas ainda **não** possui o mapeamento das colunas (`todo`, `doing`, `done`) salvo em `~/.config/neo/config.toml`;
- **Quando** executa `neo tasks resume` em modo interativo (sem `--json`);
- **Então** o sistema consulta os workflows e estados disponíveis na API do serviço (`GET /api/v3/workflows` no Shortcut), exibe a lista numerada de colunas/estados encontrados (ex.: `📝 - Backlog de Sprint`, `🚨 - Bug`, `🚧 - Em Progresso`, `✅ - Finalizado`) e solicita que o usuário selecione **1 ou mais colunas** (separadas por vírgula) para:
  1. **A fazer** (`todo`)
  2. **Fazendo** (`doing`)
  3. **Feito** (`done`)
- **E** salva o mapeamento em `~/.config/neo/config.toml` associado ao serviço e prossegue imediatamente para exibir o quadro `resume`.

### AC-2: Reconfiguração explícita de colunas (`neo tasks config columns` ou `--configure`)
- **Dado** um usuário autenticado no serviço de tasks;
- **Quando** executa `neo tasks config columns [--service <svc>]` (ou `neo tasks resume --configure`) ou passa as opções explícitas `--todo`, `--doing`, `--done`;
- **Então** o sistema atualiza o mapeamento das colunas **A fazer**, **Fazendo** e **Feito** daquele serviço em `config.toml` e confirma a gravação.

### AC-3: Exibição do quadro Kanban (`A fazer` | `Fazendo` | `Feito`) filtrando minhas tasks por padrão
- **Dado** que as colunas `todo`, `doing` e `done` estão configuradas para o serviço atual;
- **Quando** o usuário executa `neo tasks resume [--service <svc>] [--limit/-l <n>]`;
- **Então** o sistema busca as stories ativas **atribuídas ao usuário autenticado** (padrão) pertencentes aos estados mapeados em cada coluna e renderiza uma tabela Rich lado a lado com as 3 colunas:
  - **A fazer (`<quantidade>`)**
  - **Fazendo (`<quantidade>`)**
  - **Feito (`<quantidade>`)**
- **E** cada item exibe o ID (`#2157`), badge do tipo (`Bug`/`Feature`/`Chore`) e o título da task (respeitando o limite `--limit` por coluna, padrão `10`).

### AC-4: Flag `--all` para visão completa do board e suporte a `--json`
- **Dado** as colunas configuradas para o serviço;
- **Quando** o usuário executa `neo tasks resume --all` (ou `-a`);
- **Então** o quadro exibe as tasks de **todos os membros** do board nas colunas configuradas (sem restringir ao `owner` autenticado);
- **E** quando executado com a flag global `--json` (`neo --json tasks resume`), emite no `stdout` um objeto JSON estruturado contendo `service`, `filter` (`mine` ou `all`), `column_mapping` e as listas `todo`, `doing` e `done`.

---

## Matriz de decisão — Comportamento de `neo tasks resume`

| Colunas configuradas no `config.toml`? | Flag `--configure` | Modo `--json` | Flag `--all` | Resultado esperado | AC |
|---|---|---|---|---|---|
| Não | — | `False` | — | Busca estados na API, abre assistente interativo para mapear `A fazer`, `Fazendo`, `Feito`, salva no `config.toml` e renderiza o quadro | AC-1 |
| Não | — | `True` | — | Falha com código `1` e erro JSON orientando configurar as colunas via `neo tasks config columns` | AC-1, AC-4 |
| Sim | `True` | `False` | — | Reabre assistente interativo de mapeamento de colunas, atualiza `config.toml` e renderiza o quadro | AC-2 |
| Sim | `False` | `False` | `False` | Busca tasks **do usuário logado** e exibe tabela Kanban 3 colunas (`A fazer`, `Fazendo`, `Feito`) | AC-3 |
| Sim | `False` | `False` | `True` | Busca tasks **de todo o board** e exibe tabela Kanban 3 colunas | AC-4 |
| Sim | `False` | `True` | `False`/`True` | Retorna JSON estruturado com os cards agrupados em `todo`, `doing`, `done` | AC-4 |

---

## Casos de borda e erros
- **Entrada inválida no prompt interativo de seleção de colunas:** se o usuário digitar um índice ou nome inexistente, exibir mensagem de erro clara e encerrar com código `1`.
- **Nenhuma task em uma ou mais colunas:** a coluna correspondente na tabela exibe `[dim]Nenhuma task[/dim]` mantendo as 3 colunas alinhadas.
- **Execução em `--json` sem colunas configuradas:** não bloqueia aguardando `stdin`; encerra com código `1` e mensagem orientando rodar `neo tasks config columns` ou `neo tasks resume` interativamente.

## Fora de escopo
- Movimentação (drag-and-drop / transição de estado) de cards entre colunas via CLI.
- Criação ou edição de colunas/workflows no servidor do Shortcut.

## Rastreabilidade
- Arquitetura: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md)
- Qualidade e Testes: [ADR-0005](../../docs/architecture/adr/0005-padroes-de-qualidade-e-testes.md)
- UX e JSON: [ADR-0006](../../docs/architecture/adr/0006-observabilidade-e-ux-cli.md)
- Specs relacionadas: [0004-modulo-shortcut](../0004-modulo-shortcut/spec.md), [0009-refactor-cli-git-e-tasks](../0009-refactor-cli-git-e-tasks/spec.md)

