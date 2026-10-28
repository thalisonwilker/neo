---
name: cli-config
description: Manual dos comandos neo git config set, get, list e unset.
alwaysApply: false
---

# `neo git config`

Gerencia as preferências do módulo Git na seção `[git]` de `~/.config/neo/config.toml`.

Chaves válidas: `provider`, `workspace`, `default-branch`, `branch-pattern` e `commit-format`. A chave `token` não existe em `neo git config` (para credenciais, use [`neo git auth`](auth.md)).

---

## `neo git config set`

Define o valor de uma chave de configuração na seção `[git]` de `~/.config/neo/config.toml`.

### Uso

```bash
neo git config set <chave> <valor>
```

### Opções e Argumentos

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `<chave>` | Argumento | Sim | Uma das chaves: `provider`, `workspace`, `default-branch`, `branch-pattern`, `commit-format`. |
| `<valor>` | Argumento | Sim | Valor a salvar (`provider` aceita apenas `github` ou `bitbucket`). |

### Exemplo

```bash
neo git config set provider github
neo git config set workspace minha-organizacao
neo git config set default-branch main
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    ✓ Configuração Git atualizada: provider = github
    ```

=== "Saída `--json` (`neo --json git config set provider github`)"
    ```json
    {
      "status": "success",
      "key": "provider",
      "value": "github"
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Valor gravado em `~/.config/neo/config.toml`. |
| `2` | Chave `token` informada | Informa que `token` não existe em `config` e orienta usar `neo git auth login --provider <github\|bitbucket>`. |
| `2` | Chave desconhecida ou provedor inválido | Lista as chaves válidas ou os provedores suportados (`bitbucket`, `github`). |

### Suporte por Provedor

- **GitHub:** Suportado (`provider = "github"`).
- **Bitbucket Cloud:** Suportado (`provider = "bitbucket"`).

---

## `neo git config get`

Consulta o valor efetivo de uma chave de configuração Git e informa sua origem (`env`, `config` ou `default`).

### Uso

```bash
neo git config get <chave> [--json]
```

### Opções e Argumentos

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `<chave>` | Argumento | Sim | Chave a consultar (`provider`, `workspace`, `default-branch`, `branch-pattern`, `commit-format`). |
| `--json` | Opção | Não | Emite o resultado em JSON puro no `stdout`. |

### Exemplo

```bash
neo git config get provider
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    ╭───────── Configuração Git: provider ─────────╮
    │ Chave: provider                              │
    │ Valor: github                                │
    │ Origem: config                               │
    ╰──────────────────────────────────────────────╯
    ```

=== "Saída `--json`"
    ```bash
    neo git config get provider --json
    ```
    ```json
    {
      "key": "provider",
      "value": "github",
      "source": "config"
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Valor retornado com sua respectiva origem. |
| `2` | Chave inválida ou `token` | Orienta as chaves suportadas ou o comando `neo git auth status`. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

---

## `neo git config list`

Lista todas as cinco chaves de configuração do módulo `neo git` com seus valores ativos e a camada de origem.

### Uso

```bash
neo git config list [--json]
```

### Opções

| Opção | Obrigatório | Descrição |
|---|---|---|
| `--json` | Não | Emite um objeto JSON com todas as chaves e suas origens. |

### Exemplo

```bash
neo git config list
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
               Configurações Git ([git])
    ┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
    ┃ Chave          ┃ Valor             ┃ Origem  ┃
    ┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
    │ provider       │ github            │ config  │
    │ workspace      │ minha-organizacao │ config  │
    │ default-branch │ main              │ default │
    │ branch-pattern │ {type}/{id}-{slug}│ default │
    │ commit-format  │ {type}: {message} │ default │
    └────────────────┴───────────────────┴─────────┘
    ```

=== "Saída `--json`"
    ```bash
    neo git config list --json | jq '.provider'
    ```
    ```json
    {
      "value": "github",
      "source": "config"
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário |
|---|---|
| `0` | Listagem concluída com sucesso. |
| `2` | Opção desconhecida informada na linha de comando. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

---

## `neo git config unset`

Remove uma chave personalizada da seção `[git]` de `~/.config/neo/config.toml`, restaurando o comportamento padrão.

### Uso

```bash
neo git config unset <chave>
```

### Opções e Argumentos

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `<chave>` | Argumento | Sim | Chave a remover (`provider`, `workspace`, `default-branch`, `branch-pattern`, `commit-format`). |

### Exemplo

```bash
neo git config unset workspace
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    ✓ Chave workspace removida de config.toml (restaurada para o padrão).
    ```

=== "Saída `--json` (`neo --json git config unset workspace`)"
    ```json
    {
      "status": "success",
      "key": "workspace",
      "unset": true,
      "existed": true
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário |
|---|---|
| `0` | Chave removida (ou já ausente) com sucesso. |
| `2` | Chave inválida ou tentativa de passar `token`. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

