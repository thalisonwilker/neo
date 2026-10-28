---
name: cli-auth
description: Manual dos comandos neo git auth login, status e logout.
alwaysApply: false
---

# `neo git auth`

Gerencia a autenticação dos provedores Git (**GitHub** e **Bitbucket Cloud**) armazenando os segredos no **Keyring do sistema operacional** (ou em `~/.config/neo/credentials.toml` com permissão `0600`).

!!! warning "Aviso sobre Bitbucket Cloud: App Passwords descontinuadas"
    As *App Passwords* do Bitbucket Cloud foram descontinuadas. Para autenticar no Bitbucket Cloud, gere um **API Token** na sua conta Atlassian e tenha em mãos o e-mail da conta.

---

## `neo git auth login`

Solicita o token de autenticação com entrada oculta no terminal e o grava no Keyring do sistema operacional. Nunca aceita o token como argumento ou flag.

### Uso

```bash
neo git auth login --provider <github|bitbucket>
```

### Opções

| Opção | Obrigatório | Valores | Descrição |
|---|---|---|---|
| `--provider` | Sim | `github` \| `bitbucket` | Provedor Git no qual autenticar. |

### Exemplo

=== "GitHub (Personal Access Token)"
    ```bash
    neo git auth login --provider github
    # Personal Access Token do GitHub: (digitação oculta)
    ```

=== "Bitbucket Cloud (E-mail + API Token)"
    ```bash
    neo git auth login --provider bitbucket
    # Aviso: App Passwords do Bitbucket Cloud foram descontinuadas. Informe o e-mail da sua conta Atlassian e um API Token.
    # E-mail da conta Bitbucket: dev@empresa.com
    # API Token do Bitbucket: (digitação oculta)
    ```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    ✓ Credencial de GitHub salva com segurança (origem: keyring).
    ```

=== "Automação / `--json`"
    `neo git auth login` é estritamente interativo e rejeita `--json` com código `2`. Em automações e pipelines de CI/CD, exporte as variáveis de ambiente:
    ```bash
    export NEO_GITHUB_TOKEN="ghp_seu_token"
    export NEO_BITBUCKET_EMAIL="dev@empresa.com"
    export NEO_BITBUCKET_TOKEN="seu_api_token"
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Credencial gravada no Keyring ou em `credentials.toml` (`0600`). |
| `1` | Token vazio ou falha de I/O | Informa que o token não pode ser vazio. |
| `2` | Uso com `--json`, `--token` ou provedor inválido | Explica o uso correto ou orienta definir as variáveis `NEO_GITHUB_TOKEN` / `NEO_BITBUCKET_TOKEN`. |

### Suporte por Provedor

- **GitHub:** Suportado (solicita Personal Access Token).
- **Bitbucket Cloud:** Suportado (solicita e-mail da conta + API Token).

---

## `neo git auth status`

Exibe se cada provedor Git está autenticado e qual a fonte da credencial (`env`, `keyring`, `file` ou `none`), sem nunca imprimir o token.

### Uso

```bash
neo git auth status [--provider <github|bitbucket>] [--json]
```

### Opções

| Opção | Obrigatório | Valores | Descrição |
|---|---|---|---|
| `--provider` | Não | `github` \| `bitbucket` | Filtra a consulta para apenas um provedor. |
| `--json` | Não | *(flag booleana)* | Emite o estado de autenticação em JSON puro no `stdout`. |

### Exemplo

```bash
neo git auth status
neo git auth status --provider bitbucket --json | jq '.authenticated'
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
                  Status de Autenticação Git
    ┏━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
    ┃ Provedor  ┃ Autenticado ┃ Origem  ┃ Conta / E-mail  ┃
    ┡━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
    │ github    │ Sim         │ keyring │ -               │
    │ bitbucket │ Sim         │ keyring │ dev@empresa.com │
    └───────────┴─────────────┴─────────┴─────────────────┘
    ```

=== "Saída `--json`"
    ```json
    [
      {
        "provider": "github",
        "authenticated": true,
        "source": "keyring"
      },
      {
        "provider": "bitbucket",
        "authenticated": true,
        "source": "keyring",
        "email": "dev@empresa.com"
      }
    ]
    ```

### Erros e Códigos de Saída

| Código | Cenário |
|---|---|
| `0` | Status consultado com sucesso. |
| `2` | Provedor inválido informado em `--provider`. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado (inclui o campo `email` quando configurado).

---

## `neo git auth logout`

Remove as credenciais salvas de um provedor Git do Keyring do sistema operacional e do arquivo local `credentials.toml`.

### Uso

```bash
neo git auth logout --provider <github|bitbucket> [--yes] [--json]
```

### Opções

| Opção | Obrigatório | Valores | Descrição |
|---|---|---|---|
| `--provider` | Sim | `github` \| `bitbucket` | Provedor cujas credenciais serão removidas. |
| `--yes` | Não | *(flag booleana)* | Pula o prompt interativo de confirmação. |
| `--json` | Não | *(flag booleana)* | Emite a confirmação em JSON no `stdout` (exige `--yes`). |

### Exemplo

```bash
# Com confirmação interativa
neo git auth logout --provider github

# Sem prompt interativo (para scripts)
neo git auth logout --provider bitbucket --yes
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    Deseja remover as credenciais salvas de 'github'? [y/N]: y
    ✓ Credenciais de 'github' removidas com sucesso.
    ```

=== "Saída `--json`"
    ```bash
    neo git auth logout --provider github --yes --json
    ```
    ```json
    {
      "status": "success",
      "provider": "github",
      "logged_out": true
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Credenciais removidas do Keyring e do disco. |
| `1` | Cancelado pelo usuário | Usuário respondeu `N` na confirmação interativa. |
| `2` | `--json` sem `--yes` ou provedor inválido | Informa que `--yes` é obrigatório no modo `--json`. |
| `4` | Credencial não encontrada | Nenhuma credencial estava salva localmente para o provedor informado. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

