---
name: spec
description: Contrato da refatoração da CLI Neo — unifica Bitbucket/GitHub sob `neo git` e Shortcut sob `neo tasks`.
alwaysApply: true
---

# Spec — Refactor CLI: `neo git` e `neo tasks`

> **Fonte da verdade.** Status: em review
> Tier: **Pequeno** (reorganização da borda `interfaces/`; sem mudança de domínio, integrações ou ADR).

## Resumo
Hoje os comandos estão espalhados no topo (`config auth`, `config set-provider`, `workspace`, `repo`,
`commits`, `story`). A refatoração cria dois guarda-chuvas por **categoria de serviço**:

- **`neo git`** — tudo de provedores Git (Bitbucket/GitHub): config, workspace, repo, commits.
- **`neo tasks`** — tudo de gestão de tarefas (Shortcut hoje; Jira/Linear no futuro), com `--service`.

`neo config` passa a ser apenas **visão geral** (`show`). Os comandos antigos são **removidos** (breaking,
MVP 0.1.0 — decisão do dono da spec). Nenhuma regra de negócio muda: só o caminho dos comandos.

---

## Mapa de comandos (antigo → novo)

| Antigo | Novo |
|---|---|
| `neo config auth set\|get\|delete <bitbucket\|github>` | `neo git config auth set\|get\|delete <bitbucket\|github>` |
| `neo config set-provider` / `get-provider` | `neo git config set-provider` / `get-provider` |
| `neo config auth set\|get\|delete shortcut` | `neo tasks config set\|get\|delete [--service shortcut]` |
| `neo workspace list\|current\|select\|set` | `neo git workspace list\|current\|select\|set` |
| `neo repo list\|search\|clone\|create` | `neo git repo list\|search\|clone\|create` |
| `neo commits search` | `neo git commits search` |
| `neo story whoami\|list\|search\|show\|analyze` | `neo tasks whoami\|list\|search\|show\|analyze [--service shortcut]` |
| `neo config show` | `neo config show` (mantido; agrega git + tasks) |

---

## Critérios de Aceite

### AC-1: Guarda-chuva `neo git`
- **Dado** a CLI instalada;
- **Quando** o usuário executa `neo git --help`;
- **Então** lista os subgrupos `config`, `workspace`, `repo` e `commits`;
- **E** `neo git workspace|repo|commits <cmd>` se comportam exatamente como os antigos `neo workspace|repo|commits <cmd>` (incluindo `--provider/-p` e a resolução de provedor da spec 0006).

### AC-2: Configuração Git em `neo git config`
- **Dado** os serviços Git `bitbucket` e `github`;
- **Quando** o usuário executa `neo git config auth set|get|delete <serviço>`, `neo git config set-provider <p>` ou `neo git config get-provider`;
- **Então** o comportamento (Keyring, fallback 0600, `GITHUB_TOKEN`/Bitbucket env, `default_provider`) é idêntico ao das specs 0002/0003/0006;
- **E** passar `shortcut` a `neo git config auth ...` falha com código 1 e mensagem orientando `neo tasks config`.

### AC-3: Comando `neo tasks` com seletor `--service`
- **Dado** o serviço suportado `shortcut`;
- **Quando** o usuário executa `neo tasks <whoami|list|search|show|analyze>` com ou sem `--service/-s shortcut`;
- **Então** o comportamento é idêntico ao dos antigos `neo story <cmd>` (spec 0004);
- **E** `--service` omitido assume `shortcut` (único serviço hoje);
- **E** serviço inválido (ex.: `--service jira`) falha com código 1 listando os serviços suportados.

### AC-4: Configuração de tasks em `neo tasks config`
- **Dado** o serviço `shortcut`;
- **Quando** o usuário executa `neo tasks config set [--token T]`, `neo tasks config get` ou `neo tasks config delete` (com `--service/-s` opcional);
- **Então** grava/lê/remove o token do Shortcut com o mesmo armazenamento seguro de antes (Keyring, fallback 0600, `SHORTCUT_API_TOKEN`);
- **E** em modo `--json` sem `--token`, `set` falha com código 1 (como hoje).

### AC-5: `neo config` reduzido a visão geral
- **Dado** o novo layout;
- **Quando** o usuário executa `neo config show`;
- **Então** exibe credenciais de **todos** os serviços (git + tasks) e o provedor padrão, com a mesma saída de hoje;
- **E** `neo config` não expõe mais `auth`, `set-provider` nem `get-provider`.

### AC-6: Comandos antigos removidos
- **Dado** o novo layout;
- **Quando** o usuário executa `neo repo`, `neo workspace`, `neo commits` ou `neo story`;
- **Então** o Typer retorna "No such command" com código de saída 2 (sem aliases);
- **E** `neo --help` lista apenas `config`, `git` e `tasks`.

### AC-7: Mensagens e documentação coerentes
- **Dado** qualquer mensagem de erro que oriente o usuário a configurar credenciais;
- **Quando** exibida (ex.: credencial ausente);
- **Então** cita o **novo** comando (`neo git config auth set <svc>` / `neo tasks config set`);
- **E** README, `docs/` (cli/*, getting-started, configuration) e specs vivas refletem os novos caminhos.

---

## Casos de Borda e Erros
- `neo git config auth set shortcut` → erro orientando `neo tasks config set` (AC-2).
- `neo tasks --service jira ...` → erro "serviço não suportado" listando `shortcut` (AC-3).
- Scripts que usavam os caminhos antigos quebram (breaking assumido; registrar no CHANGELOG/README).

---

## Fora de Escopo
- Aliases/deprecação dos comandos antigos (removidos de imediato).
- Novos serviços de tasks (Jira, Linear) — apenas o seletor `--service` fica pronto para eles.
- Mudanças em integrações, resolvedor de provedor, formato de saída ou chaves do `config.toml`.
- Reescrever specs históricas 0002–0006 (permanecem como registro; a spec 0009 as supera nos caminhos).

---

## Rastreabilidade
- Arquitetura: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md) (mudança só na camada `interfaces/`).
- UX/saída: [ADR-0006](../../docs/architecture/adr/0006-observabilidade-e-ux-cli.md).
- Specs anteriores afetadas: 0002, 0003, 0004, 0005, 0006.
