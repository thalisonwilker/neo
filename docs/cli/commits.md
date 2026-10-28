---
name: cli-commits
description: Manual dos comandos neo git commits list, search e show.
alwaysApply: false
---

# `neo git commits`

Lista, pesquisa e inspeciona commits no **GitHub** e no **Bitbucket Cloud**. Quando executado dentro de um repositório Git local, detecta automaticamente o provedor, o workspace e o slug do repositório a partir do `remote origin`.

---

## `neo git commits list`

Lista os commits mais recentes de um repositório, com filtro opcional por autor.

### Uso

```bash
neo git commits list [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--author <autor>] [--limit <n>] [--json]
```

### Opções

| Opção | Obrigatório | Padrão | Descrição |
|---|---|---|---|
| `--repo` | Não *(se em diretório Git)* | *(auto via `origin`)* | Slug do repositório. |
| `--workspace` | Não | *(workspace ativo)* | Workspace ou organização proprietária. |
| `--provider` | Não | *(provedor ativo)* | Provedor Git (`github` ou `bitbucket`). |
| `--author` | Não | — | Filtra commits pelo nome ou e-mail do autor. |
| `--limit` | Não | `20` | Quantidade máxima de commits a retornar. |
| `--json` | Não | `false` | Emite a lista de commits em JSON puro no `stdout`. |

### Exemplo

```bash
# No diretório do repositório Git atual
neo git commits list --limit 5

# Filtrando por autor em um repositório específico
neo git commits list --repo neo --provider github --author "Thalyson" --limit 10
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
                  Histórico de Commits (neo via GitHub)
    ┏━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ Hash    ┃ Autor    ┃ Data       ┃ Mensagem                           ┃
    ┡━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ 30ca84c │ Thalyson │ 2026-10-28 │ chore(release): bump version       │
    │ ad9015d │ Thalyson │ 2026-10-28 │ docs: revisa documentacao da CLI   │
    └─────────┴──────────┴────────────┴────────────────────────────────────┘
    ```

=== "Saída `--json`"
    ```bash
    neo git commits list --limit 1 --json
    ```
    ```json
    [
      {
        "hash": "30ca84c958d580abcdef1234567890abcdef1234",
        "message": "chore(release): bump version",
        "date": "2026-10-28T11:45:00Z",
        "web_url": "https://github.com/thalisonwilker/neo/commit/30ca84c",
        "author": {
          "raw": "Thalyson <thalison.wilker@gmail.com>",
          "display_name": "Thalyson"
        }
      }
    ]
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Tabela ou lista JSON impressa. |
| `2` | Opção inválida | Informa erro de sintaxe. |
| `3` | Erro de autenticação | Orienta executar `neo git auth login --provider <github\|bitbucket>`. |
| `4` | Repositório não detectado ou inexistente (`404`) | Orienta informar `--repo <slug>`. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

---

## `neo git commits search`

Pesquisa commits cuja mensagem contenha o termo especificado em `--query`.

### Uso

```bash
neo git commits search --query <termo> [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--author <autor>] [--limit <n>] [--json]
```

### Opções

| Opção | Obrigatório | Padrão | Descrição |
|---|---|---|---|
| `--query` | **Sim** | — | Termo ou ID de ticket procurado na mensagem do commit. |
| `--repo` | Não *(se em diretório Git)* | *(auto via `origin`)* | Slug do repositório. |
| `--workspace` | Não | *(workspace ativo)* | Workspace ou organização proprietária. |
| `--provider` | Não | *(provedor ativo)* | Provedor Git (`github` ou `bitbucket`). |
| `--author` | Não | — | Filtra também pelo nome ou e-mail do autor. |
| `--limit` | Não | `20` | Quantidade máxima de commits a retornar. |
| `--json` | Não | `false` | Emite os resultados em JSON puro no `stdout`. |

### Exemplo

```bash
# Buscar commits que mencionam um ticket do Shortcut
neo git commits search --query "sc-2108" --limit 10

# Exportar hashes de commits de bugfix para um script
neo git commits search --query "fix" --limit 5 --json | jq -r '.[].hash'
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
                  Histórico de Commits (neo via GitHub)
    ┏━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ Hash    ┃ Autor    ┃ Data       ┃ Mensagem                           ┃
    ┡━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ a1b2c3d │ Thalyson │ 2026-10-27 │ fix: resolve timeout na query      │
    └─────────┴──────────┴────────────┴────────────────────────────────────┘
    ```

=== "Saída `--json`"
    ```json
    [
      {
        "hash": "a1b2c3d4e5f67890",
        "message": "fix: resolve timeout na query",
        "date": "2026-10-27T14:30:00Z",
        "web_url": "https://github.com/thalisonwilker/neo/commit/a1b2c3d4e5f67890",
        "author": {
          "raw": "Thalyson <thalison.wilker@gmail.com>",
          "display_name": "Thalyson"
        }
      }
    ]
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Commits correspondentes listados. |
| `2` | `--query` ausente | Informa que `--query <termo>` é obrigatório e sugere `neo git commits list` para listagem sem filtro. |
| `3` | Erro de autenticação | Orienta executar `neo git auth login`. |
| `4` | Repositório não encontrado ou não informado fora de pasta Git | Orienta passar `--repo <slug>`. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

---

## `neo git commits show`

Exibe os detalhes completos de um commit individual a partir do seu hash (SHA completo ou curto).

### Uso

```bash
neo git commits show <sha> [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

### Opções e Argumentos

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `<sha>` | Argumento | **Sim** | Hash SHA (completo ou curto) do commit. |
| `--repo` | Opção | Não *(se em diretório Git)* | Slug do repositório. |
| `--workspace` | Opção | Não | Workspace ou organização proprietária. |
| `--provider` | Opção | Não | Provedor Git (`github` ou `bitbucket`). |
| `--json` | Opção | Não | Emite os dados completos do commit em JSON no `stdout`. |

### Exemplo

```bash
neo git commits show a1b2c3d
neo git commits show a1b2c3d --repo neo --provider github --json | jq '{hash, author_name, date}'
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    ╭─────────────── Commit a1b2c3d (neo via GitHub) ───────────────╮
    │ Hash: a1b2c3d4e5f67890                                        │
    │ Autor: Thalyson <thalison.wilker@gmail.com>                   │
    │ Data: 2026-10-27T14:30:00Z                                    │
    │ URL: https://github.com/thalisonwilker/neo/commit/a1b2c3d4    │
    │                                                               │
    │ Mensagem:                                                     │
    │ fix: resolve timeout na query                                 │
    │                                                               │
    │ Ajusta limite de espera na chamada HTTP.                      │
    ╰───────────────────────────────────────────────────────────────╯
    ```

=== "Saída `--json`"
    ```json
    {
      "hash": "a1b2c3d4e5f67890",
      "short_hash": "a1b2c3d",
      "message": "fix: resolve timeout na query\n\nAjusta limite de espera na chamada HTTP.",
      "date": "2026-10-27T14:30:00Z",
      "web_url": "https://github.com/thalisonwilker/neo/commit/a1b2c3d4",
      "author": {
        "raw": "Thalyson <thalison.wilker@gmail.com>",
        "display_name": "Thalyson"
      },
      "author_name": "Thalyson",
      "repo": "neo",
      "provider": "github"
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Detalhes do commit exibidos. |
| `2` | `<sha>` omitido | Erro de argumento obrigatório ausente. |
| `3` | Erro de autenticação | Orienta executar `neo git auth login`. |
| `4` | Commit `<sha>` ou repositório não encontrado (`404`) | Informa que o commit ou repositório não existe. |

### Suporte por Provedor

- **GitHub:** Suportado (`GET /repos/{owner}/{repo}/commits/{sha}`).
- **Bitbucket Cloud:** Suportado (`GET /2.0/repositories/{workspace}/{repo_slug}/commit/{sha}`).

---

!!! note "Planejado"
    O comando abaixo está especificado no backlog para implementação futura:

    - `neo git commits diff <sha> [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>]`: exibe o patch/diff unificado das alterações introduzidas pelo commit `<sha>`.
