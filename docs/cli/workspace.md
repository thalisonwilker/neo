---
name: cli-workspace
description: Manual dos comandos neo git workspace list, select e show.
alwaysApply: false
---

# `neo git workspace`

Lista, seleciona e exibe detalhes do **Workspace** ativo. No Neo, *Workspace* é o conceito unificado que representa um **Workspace** no Bitbucket Cloud e uma **Organization** ou **conta pessoal de usuário** no GitHub.

---

## `neo git workspace list`

Lista todos os workspaces (Bitbucket) ou organizações e conta pessoal (GitHub) acessíveis pelo token atual, destacando o workspace ativo.

### Uso

```bash
neo git workspace list [--provider <github|bitbucket>] [--limit <n>] [--json]
```

### Opções

| Opção | Obrigatório | Descrição |
|---|---|---|
| `--provider` | Não | Força a consulta em `github` ou `bitbucket`. |
| `--limit` | Não | Quantidade máxima de workspaces a exibir. |
| `--json` | Não | Emite a lista em JSON puro no `stdout`. |

### Exemplo

```bash
neo git workspace list --provider github
neo git workspace list --json | jq '.[] | select(.is_active == true) | .slug'
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
                   Workspaces no GitHub
    ┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
    ┃ Nome          ┃ Slug      ┃ Admin ┃ Status  ┃
    ┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
    │ The Octocat   │ octocat   │ Sim   │ ● Ativo │
    │ Acme Corp     │ acme-corp │ Não   │ -       │
    └───────────────┴───────────┴───────┴─────────┘
    ```

=== "Saída `--json`"
    ```json
    [
      {
        "name": "The Octocat",
        "slug": "octocat",
        "uuid": "1",
        "is_admin": true,
        "is_active": true,
        "provider": "github"
      }
    ]
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Lista exibida no terminal ou em JSON. |
| `2` | Opção ou provedor inválido | Indica os provedores válidos (`bitbucket`, `github`). |
| `3` | Não autenticado ou token inválido | Orienta executar `neo git auth login --provider <github\|bitbucket>`. |

### Suporte por Provedor

- **GitHub:** Suportado (retorna a conta pessoal e as organizações `/user/orgs`).
- **Bitbucket Cloud:** Suportado (retorna `/2.0/user/workspaces`).

---

## `neo git workspace select`

Seleciona o workspace ativo por menu numérico interativo no teclado ou diretamente via `--workspace <slug>`, gravando a escolha em `[git].workspace` no `config.toml`.

### Uso

```bash
neo git workspace select [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

### Opções

| Opção | Obrigatório | Descrição |
|---|---|---|
| `--workspace` | Não *(Sim com `--json`)* | Slug do workspace para ativar diretamente sem menu interativo. |
| `--provider` | Não | Provedor alvo (`github` ou `bitbucket`). |
| `--json` | Não | Emite o resultado em JSON no `stdout` (exige `--workspace`). |

### Exemplo

```bash
# Menu interativo no terminal
neo git workspace select

# Seleção direta sem prompt
neo git workspace select --workspace acme-corp --provider github
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    ✓ Workspace ativo no GitHub definido com sucesso: acme-corp (Acme Corp)
    ```

=== "Saída `--json`"
    ```bash
    neo git workspace select --workspace acme-corp --provider github --json
    ```
    ```json
    {
      "status": "success",
      "provider": "github",
      "workspace": "acme-corp",
      "name": "Acme Corp"
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Workspace validado na API e salvo em `config.toml`. |
| `2` | `--json` sem `--workspace` ou opção inválida no menu | Orienta informar `--workspace <slug>`. |
| `3` | Não autenticado | Orienta executar `neo git auth login --provider <github\|bitbucket>`. |
| `4` | Workspace não encontrado | Lista os slugs disponíveis para a conta autenticada. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

---

## `neo git workspace show`

Exibe os detalhes do workspace ativo (ou do workspace informado em `--workspace`) e de qual camada ele foi resolvido (`cli`, `env`, `config`, `remote` ou `default`).

### Uso

```bash
neo git workspace show [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

### Opções

| Opção | Obrigatório | Descrição |
|---|---|---|
| `--workspace` | Não | Slug de um workspace específico para inspecionar. |
| `--provider` | Não | Provedor alvo (`github` ou `bitbucket`). |
| `--json` | Não | Emite os detalhes em JSON puro no `stdout`. |

### Exemplo

```bash
neo git workspace show
neo git workspace show --json | jq '{workspace, provider, source}'
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    ╭─────────────────── Workspace Ativo (GitHub) ───────────────────╮
    │ Nome: Acme Corp                                                │
    │ Slug: acme-corp                                                │
    │ Admin: Sim                                                     │
    │ Origem: Configuração local (~/.config/neo/config.toml)         │
    ╰────────────────────────────────────────────────────────────────╯
    ```

=== "Saída `--json`"
    ```json
    {
      "workspace": "acme-corp",
      "name": "Acme Corp",
      "uuid": "2",
      "is_admin": true,
      "provider": "github",
      "source": "config"
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Detalhes do workspace exibidos. |
| `2` | Provedor ou opção inválida | Informa o uso correto. |
| `3` | Erro de autenticação | Orienta executar `neo git auth login`. |
| `4` | Workspace inexistente | O slug passado em `--workspace` não foi encontrado na conta. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.
