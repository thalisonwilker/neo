---
name: migration
description: Guia de migração e tabela de breaking changes para a nova gramática neo git.
alwaysApply: false
---

# Guia de Migração (`neo git`)

A partir desta versão, o módulo `neo git` adota a gramática padronizada `neo git <recurso> <ação> [argumentos] [--opções]`, remove todos os atalhos de uma letra e concentra configuração e autenticação em `neo git config`.

---

## Resumo de Breaking Changes

1. **Remoção de atalhos de uma letra:** Opções curtas (`-p`, `-w`, `-r`, `-a`, `-q`, `-l`, `-s`, `-d`, `-y`, `-t`) foram removidas de `neo git`. Use sempre a forma longa (`--provider`, `--workspace`, `--repo`, `--author`, `--query`, `--limit`, `--yes`).
2. **Autenticação:** configure o provedor com `neo git config set provider <github|bitbucket>` e use `neo git config set api-key`. A chave é solicitada com entrada oculta e validada antes de ser salva.
3. **A chave `token` é proibida em `neo git config`:** use `api-key` para credenciais. As preferências incluem `provider`, `workspace`, `default-branch`, `branch-pattern` e `commit-format`; o contexto também inclui `repo`, `branch` e `task`.
4. **Bitbucket Cloud exige e-mail + API Token:** `neo git config set api-key` solicita o e-mail da conta Atlassian e o API Token. Como alternativa para automações, configure `NEO_BITBUCKET_EMAIL` e `NEO_BITBUCKET_TOKEN` no ambiente.
5. **Busca com `--query` explícito:** `neo git repo search` e `neo git commits search` exigem a opção `--query <termo>`. Para listar commits sem filtro de mensagem, use `neo git commits list`.
6. **Códigos de saída semânticos (`0` a `5`):** Falhas de autenticação agora retornam código `3` e recursos não encontrados retornam código `4` (antes retornavam `1`).

---

## Tabela de Equivalência (Comando Antigo → Comando Novo)

| Comando Antigo | Comando Novo | Notas de Migração |
|---|---|---|
| `neo git config auth set github --token "..."` | `neo git config set api-key` | Solicita o token em prompt oculto; em CI, use `NEO_GITHUB_TOKEN`. |
| `neo git config auth set bitbucket --token "..."` | `neo git config set api-key` | Solicita e-mail + API Token em prompt oculto; em CI, use `NEO_BITBUCKET_EMAIL` e `NEO_BITBUCKET_TOKEN`. |
| `neo git config auth get <provider>` | `neo git config get api-key` | Exibe se está autenticado e a fonte, sem expor o token. |
| `neo git config auth delete <provider>` | `neo git config unset api-key --yes` | Pede confirmação interativa, ou pula com `--yes`. |
| `neo git config set-provider <provider>` | `neo git config set provider <provider>` | Gravado em `[git].provider` no `config.toml`. |
| `neo git config get-provider` | `neo git config get provider` | Lê de `NEO_GIT_PROVIDER` ou `[git].provider`. |
| `neo git workspace current` | `neo git config get workspace` | Exibe o workspace configurado e sua origem. |
| `neo git workspace set <slug> -p <provider>` | `neo git config set workspace <slug>` | Sem flag curta `-p`. |
| `neo git workspace select --slug <slug>` | `neo git config set workspace <slug>` | Define o workspace configurado. |
| `neo git repo list -w <ws> -p <provider>` | `neo git repo remote-list --workspace <ws> --provider <provider>` | Sem flags curtas `-w` ou `-p`. |
| `neo git repo search <termo>` | `neo git repo search --query <termo>` | O termo de busca passa a ser informado via `--query`. |
| `neo git commits search` *(sem termo)* | `neo git commits list` | Use `list` para histórico geral e `search --query` para filtrar por mensagem. |
| `neo git commits search -q <termo> -r <repo> -l 5` | `neo git commits search --query <termo> --repo <repo> --limit 5` | Opções exclusivamente em forma longa. |
| `neo git repo clone <slug>` | *(Planejado no backlog)* | Consulte as URLs de clone com `neo git repo show --repo <slug>`. |
| `neo git repo create <nome>` | `neo git repo create <nome> --path <caminho>` | Cria e publica o repositório; privado por padrão. |

---

## Comportamento ao Executar um Comando Antigo

Se um script antigo invocar um comando substituído (como `neo git config auth`, `neo git config set-provider`, `neo git workspace current` ou `neo git workspace set`), o Neo falha com **código de saída `2`**. Consulte a tabela acima para o comando correspondente.


## Atualização do contexto Git

Os grupos `neo git auth` e `neo git workspace` foram removidos. `neo git auth login` foi substituído por `neo git config set api-key`, após configurar o provedor. `neo git repo list` agora lista repositórios locais registrados; use `neo git repo remote-list` para listar os remotos. Selecione o contexto com `neo git repo select <caminho>`.
