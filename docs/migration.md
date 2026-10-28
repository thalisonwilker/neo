---
name: migration
description: Guia de migração e tabela de breaking changes para a nova gramática neo git.
alwaysApply: false
---

# Guia de Migração (`neo git`)

A partir desta versão, o módulo `neo git` adota a gramática padronizada `neo git <recurso> <ação> [argumentos] [--opções]`, remove todos os atalhos de uma letra e separa configuração (`neo git config`) de autenticação (`neo git auth`).

---

## Resumo de Breaking Changes

1. **Remoção de atalhos de uma letra:** Opções curtas (`-p`, `-w`, `-r`, `-a`, `-q`, `-l`, `-s`, `-d`, `-y`, `-t`) foram removidas de `neo git`. Use sempre a forma longa (`--provider`, `--workspace`, `--repo`, `--author`, `--query`, `--limit`, `--yes`).
2. **Autenticação separada de configuração:** Tokens não são mais gerenciados em `neo git config auth` e **nunca** são passados por argumento/flag (`--token` foi removido). Use `neo git auth login --provider <github|bitbucket>`.
3. **A chave `token` é proibida em `neo git config`:** O comando `neo git config` gerencia apenas as chaves `provider`, `workspace`, `default-branch`, `branch-pattern` e `commit-format` na seção `[git]` de `~/.config/neo/config.toml`.
4. **Bitbucket Cloud exige e-mail + API Token:** Como as *App Passwords* foram descontinuadas no Bitbucket Cloud, `neo git auth login --provider bitbucket` solicita o e-mail da conta Atlassian e o API Token (ou lê `NEO_BITBUCKET_EMAIL` + `NEO_BITBUCKET_TOKEN`).
5. **Busca com `--query` explícito:** `neo git repo search` e `neo git commits search` exigem a opção `--query <termo>`. Para listar commits sem filtro de mensagem, use `neo git commits list`.
6. **Códigos de saída semânticos (`0` a `5`):** Falhas de autenticação agora retornam código `3` e recursos não encontrados retornam código `4` (antes retornavam `1`).

---

## Tabela de Equivalência (Comando Antigo → Comando Novo)

| Comando Antigo | Comando Novo | Notas de Migração |
|---|---|---|
| `neo git config auth set github --token "..."` | `neo git auth login --provider github` | Solicita o token em prompt oculto; em CI, use `NEO_GITHUB_TOKEN`. |
| `neo git config auth set bitbucket --token "..."` | `neo git auth login --provider bitbucket` | Solicita e-mail + API Token em prompt oculto; em CI, use `NEO_BITBUCKET_EMAIL` e `NEO_BITBUCKET_TOKEN`. |
| `neo git config auth get <provider>` | `neo git auth status --provider <provider>` | Exibe se está autenticado e a fonte, sem expor o token. |
| `neo git config auth delete <provider>` | `neo git auth logout --provider <provider> --yes` | Pede confirmação interativa, ou pula com `--yes`. |
| `neo git config set-provider <provider>` | `neo git config set provider <provider>` | Gravado em `[git].provider` no `config.toml`. |
| `neo git config get-provider` | `neo git config get provider` | Lê de `NEO_GIT_PROVIDER` ou `[git].provider`. |
| `neo git workspace current` | `neo git workspace show` | Exibe nome, slug, admin e origem da resolução. |
| `neo git workspace set <slug> -p <provider>` | `neo git config set workspace <slug>` ou `neo git workspace select --workspace <slug> --provider <provider>` | Sem flag curta `-p`. |
| `neo git workspace select --slug <slug>` | `neo git workspace select --workspace <slug>` | A opção `--slug` foi padronizada para `--workspace`. |
| `neo git repo list -w <ws> -p <provider>` | `neo git repo list --workspace <ws> --provider <provider>` | Sem flags curtas `-w` ou `-p`. |
| `neo git repo search <termo>` | `neo git repo search --query <termo>` | O termo de busca passa a ser informado via `--query`. |
| `neo git commits search` *(sem termo)* | `neo git commits list` | Use `list` para histórico geral e `search --query` para filtrar por mensagem. |
| `neo git commits search -q <termo> -r <repo> -l 5` | `neo git commits search --query <termo> --repo <repo> --limit 5` | Opções exclusivamente em forma longa. |
| `neo git repo clone <slug>` | *(Planejado no backlog)* | Consulte as URLs de clone com `neo git repo show --repo <slug>`. |
| `neo git repo create <nome>` | *(Planejado no backlog)* | Movido para o backlog planejado da próxima onda. |

---

## Comportamento ao Executar um Comando Antigo

Se um script antigo invocar um comando substituído (como `neo git config auth`, `neo git config set-provider`, `neo git workspace current` ou `neo git workspace set`), o Neo falha imediatamente com **código de saída `2`** e imprime no `stderr` (ou em JSON se `--json` estiver ativo) qual é o novo comando que deve ser utilizado.

