---
name: spec
description: Contrato da feature 0012 — listagem de iterações e filtro por iteração (padrão = última iteração, ou via --iteration/-i) em `neo tasks list` e `neo tasks resume`.
alwaysApply: true
---

# Spec — Filtro por Iteração em Tasks (`neo tasks list`, `neo tasks resume`, `neo tasks iterations`)

> **Fonte da verdade.** Status: implementado
> Tier: **Pequeno** (`spec.md` + `tasks.md` — evolução do módulo `neo tasks` e integração Shortcut).

## Resumo
Adiciona suporte a **Iterações (Sprints)** no módulo `neo tasks`: cria o comando `neo tasks iterations` para listar as iterações do workspace e faz com que `neo tasks list` e `neo tasks resume` filtrem automaticamente pela **última iteração** (iteração atual no Shortcut), oferecendo a opção `--iteration / -i <nome_ou_id>` para consultar qualquer outra iteração (ou `all` para todas).

---

## Critérios de aceite

### AC-1: Listagem de iterações (`neo tasks iterations`)
- **Dado** um usuário autenticado no serviço de tasks (`shortcut`);
- **Quando** executa `neo tasks iterations [--service <svc>] [--limit/-l <n>]`;
- **Então** o sistema consulta `GET /api/v3/iterations`, ordena da mais recente para a mais antiga (por `start_date` e `id`) e exibe uma tabela Rich (ou lista JSON com `--json`) contendo: **ID**, **Nome** (marcando a última com `[● Atual]`), **Status** (`unstarted`, `started`, `done`) e **Período (`start_date → end_date`)**.

### AC-2: Filtro padrão pela última iteração em `neo tasks list` e `neo tasks resume`
- **Dado** que o workspace no Shortcut possui iterações cadastradas e o usuário **não** informou `--iteration / -i`;
- **Quando** executa `neo tasks list` (com ou sem `--mine`) ou `neo tasks resume` (com ou sem `--all`);
- **Então** o sistema seleciona automaticamente a **última iteração** (maior `start_date` / maior `id`), filtra apenas as tasks cujo `iteration_id` corresponda a essa iteração e destaca o nome da iteração no título da tabela/quadro (e no campo `iteration` em modo `--json`);
- **E** caso o workspace não possua nenhuma iteração cadastrada na API (`[]`), exibe as tasks sem filtro de iteração (fallback gracioso).

### AC-3: Seleção explícita de iteração via `--iteration / -i <termo>`
- **Dado** as iterações disponíveis no serviço;
- **Quando** o usuário executa `neo tasks list -i <termo>` ou `neo tasks resume -i <termo>`;
- **Então** o sistema resolve `<termo>` buscando por:
  1. Valor especial `all` → desativa o filtro por iteração e retorna tasks de todas as iterações;
  2. ID numérico exato da iteração;
  3. Nome exato da iteração (case-insensitive, ex.: `"Sprint 71"`);
  4. Substring no nome da iteração (case-insensitive, ex.: `"71"` encontra `"Sprint 71"`);
- **E** filtra as tasks pela iteração encontrada;
- **E** caso nenhuma iteração corresponda a `<termo>`, encerra com código `1` e mensagem de erro clara orientando consultar `neo tasks iterations`.

### AC-4: Exibição da Iteração nos cards e tabelas
- **Dado** as stories retornadas no `neo tasks list` e `neo tasks resume`;
- **Quando** renderizadas no terminal (Rich) ou em `--json`;
- **Então** o modelo `ShortcutStory` inclui `iteration_id` e cada card no `neo tasks resume` exibe o badge da iteração correspondente (`🔄 <nome da iteração>`) quando presente.

---

## Matriz de decisão — Resolução do Filtro de Iteração (`--iteration / -i`)

| Valor de `--iteration / -i` | Iterações existem na API? | Correspondência encontrada? | Comportamento em `list` e `resume` | AC |
|---|---|---|---|---|
| `None` (omitido) | Sim | Última iteração (`max(start_date, id)`) | Filtra tasks por `iteration_id == latest.id` e exibe nome da sprint no título | AC-2 |
| `None` (omitido) | Não (`[]`) | — | Não filtra por iteração (exibe todas as tasks ativas) | AC-2 |
| `"all"` | Sim / Não | — | Não filtra por iteração (exibe tasks de todas as sprints) | AC-3 |
| `<id>` ou `<nome/substring>` | Sim | Sim | Filtra tasks por `iteration_id == matched.id` e exibe nome da sprint no título | AC-3 |
| `<id>` ou `<nome/substring>` | Sim / Não | Não | Encerra com código `1` e erro sugerindo `neo tasks iterations` | AC-3 |

---

## Casos de borda e erros
- **Múltiplas iterações com mesma substring (ex.: `-i "Sprint"`):** seleciona a mais recente entre as que deram match parcial (e prioriza match exato antes de parcial).
- **Nenhuma story encontrada na iteração selecionada:** exibe painel/célula informando que não há tasks naquela iteração (ou `[]` em JSON) com código `0`.

## Fora de escopo
- Criação, edição ou encerramento de iterações/sprints via CLI.
- Alterar a iteração de uma story via CLI.

## Rastreabilidade
- Arquitetura: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md)
- Qualidade e Testes: [ADR-0005](../../docs/architecture/adr/0005-padroes-de-qualidade-e-testes.md)
- UX e JSON: [ADR-0006](../../docs/architecture/adr/0006-observabilidade-e-ux-cli.md)
- Specs relacionadas: [0004-modulo-shortcut](../0004-modulo-shortcut/spec.md), [0011-tasks-resume-board](../0011-tasks-resume-board/spec.md)

