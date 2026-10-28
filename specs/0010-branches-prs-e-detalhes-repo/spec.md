---
name: spec
description: Contrato planejado (backlog) da feature 0010 — consulta e operações de branches, pull requests, tags, releases, diff de commits e ações de repositório sob a gramática `neo git`.
alwaysApply: false
---

# Spec — Operações de Backlog Git (`branch`, `pr`, `tag`, `release`, `repo open/clone/create`, `commits diff`)

> **Fonte da verdade.** Status: planejado (backlog)
> Tier: **Pequeno** (`spec.md` + `tasks.md` — itens de backlog especificados para ondas seguintes; `neo git repo show` e paginação de `repo list/search` foram incorporados na [0014-gramatica-cli-git](../0014-gramatica-cli-git/spec.md)).

## Resumo
Especifica os comandos planejados (backlog) do módulo `neo git` seguindo a gramática estrita `neo git <recurso> <ação> [argumentos] [--opções]` sem atalhos de uma letra: gerenciamento de branches (`neo git branch`), pull requests (`neo git pr`), tags (`neo git tag`), releases (`neo git release`), ações de repositório (`neo git repo open|clone|create`) e diff de commits (`neo git commits diff <sha>`).

---

## Critérios de aceite (Planejados / Backlog)

### AC-1: Consulta e gerenciamento de branches (`neo git branch`)
- **Dado** um repositório alvo informado via `--repo <slug>` ou auto-detectado do remote `origin` do diretório Git local;
- **Quando** o usuário executa `neo git branch list [--repo <slug>] [--workspace <ws>] [--provider <github|bitbucket>] [--limit <n>] [--json]`, `neo git branch show <nome>`, `neo git branch create <nome>` ou `neo git branch remove <nome> [--yes]`;
- **Então** o sistema opera sobre as branches remotas do repositório no provedor resolvido respeitando os códigos de saída padronizados (`0` a `5`) e confirmação interativa em `remove` (salvo com `--yes`).

### AC-2: Consulta e gerenciamento de Pull Requests (`neo git pr`)
- **Dado** um repositório alvo informado via `--repo <slug>` ou auto-detectado do diretório Git local;
- **Quando** o usuário executa `neo git pr list [--repo <slug>] [--workspace <ws>] [--provider <github|bitbucket>] [--state <open|merged|declined|all>] [--limit <n>] [--json]`, `neo git pr show <id>`, `neo git pr search --query <termo>` ou `neo git pr create`;
- **Então** o sistema consulta ou cria Pull Requests mapeando os estados de forma unificada (`open`, `merged`, `declined`, `all`) e exibindo saída Rich ou JSON.

### AC-3: Consulta e gerenciamento de Tags e Releases (`neo git tag` e `neo git release`)
- **Dado** um repositório alvo informado via `--repo <slug>` ou auto-detectado do diretório Git local;
- **Quando** o usuário executa `neo git tag list|show|create|remove` ou `neo git release list|show|create`;
- **Então** o sistema lista, inspeciona, cria ou remove tags e releases no provedor ativo, ou retorna código de saída `5` (não suportado) com sugestão de alternativa caso o provedor não suporte o recurso via API.

### AC-4: Ações de Repositório (`neo git repo open|clone|create`) e Diff de Commits (`neo git commits diff <sha>`)
- **Dado** um usuário autenticado no provedor resolvido;
- **Quando** executa `neo git repo open [--repo <slug>]`, `neo git repo clone <slug> [--protocol <ssh|https>]`, `neo git repo create <nome> [--private|--public] [--description <texto>] [--yes]` ou `neo git commits diff <sha> [--repo <slug>] [--json]`;
- **Então** o sistema executa a ação correspondente sem atalhos de uma letra e exigindo confirmação em `create` (ou `--yes`).

---

## Matriz de decisão — Mapeamento de Estados de Pull Request (`--state`)

| Flag `--state` na CLI | Filtro na API Bitbucket (`state=`) | Filtro na API GitHub (`state=` + pós-filtro) | Estado normalizado no modelo | AC |
|---|---|---|---|---|
| `open` (default) | `OPEN` | `state=open` | `OPEN` | AC-2 |
| `merged` | `MERGED` | `state=closed` + `merged_at != null` | `MERGED` | AC-2 |
| `declined` | `DECLINED` | `state=closed` + `merged_at == null` | `DECLINED` | AC-2 |
| `all` | `OPEN`, `MERGED`, `DECLINED` | `state=all` | `OPEN` \| `MERGED` \| `DECLINED` | AC-2 |

---

## Casos de borda e erros
- Executar comandos dependentes de repositório fora de um diretório Git e sem `--repo` → erro com código `4` orientando informar `--repo <slug>`.
- Operação não suportada pelo provedor ativo (ex.: `release` no Bitbucket Cloud, que não possui entidade nativa de Releases na API v2.0) → erro com código `5` sugerindo o uso de `neo git tag`.

## Fora de escopo da entrega atual
- Estes itens compõem o **backlog planejado** e **não** devem ser implementados durante a entrega da spec `0014-gramatica-cli-git` (devem aparecer na documentação apenas dentro de blocos `!!! note "Planejado"`).

## Rastreabilidade
- Gramática e Códigos de Saída: [0014-gramatica-cli-git](../0014-gramatica-cli-git/spec.md)
- Arquitetura: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md)
