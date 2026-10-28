---
name: cli-repo
description: Manual dos comandos neo git repo list, search e show.
alwaysApply: false
---

# `neo git repo`

Lista, filtra e inspeciona repositórios remotos no **GitHub** e no **Bitbucket Cloud** com suporte a paginação automática.

---

## `neo git repo list`

Lista os repositórios disponíveis no workspace resolvido.

### Uso

```bash
neo git repo list [--workspace <slug>] [--provider <github|bitbucket>] [--limit <n>] [--json]
```

### Opções

| Opção | Obrigatório | Descrição |
|---|---|---|
| `--workspace` | Não | Workspace (Bitbucket) ou organização/usuário (GitHub) alvo. |
| `--provider` | Não | Provedor Git (`github` ou `bitbucket`). |
| `--limit` | Não | Quantidade máxima de repositórios a retornar. |
| `--json` | Não | Emite a lista de repositórios em JSON puro no `stdout`. |

### Exemplo

```bash
neo git repo list --limit 10
neo git repo list --provider github --workspace minha-org --json | jq '.[].slug'
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
                              Repositórios no GitHub
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
    ┃ Nome         ┃ Slug         ┃ Visibilidade ┃ Branch Padrão ┃ Atualizado em ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
    │ neo          │ neo          │ Público      │ main          │ 2026-10-28    │
    │ core-backend │ core-backend │ Privado      │ main          │ 2026-10-27    │
    └──────────────┴──────────────┴──────────────┴───────────────┴───────────────┘
    ```

=== "Saída `--json`"
    ```json
    [
      {
        "name": "neo",
        "slug": "neo",
        "is_private": false,
        "description": "Assistente pessoal de linha de comando",
        "updated_on": "2026-10-28T10:00:00Z",
        "main_branch": "main",
        "workspace": "thalisonwilker",
        "web_url": "https://github.com/thalisonwilker/neo",
        "clone_links": [
          {
            "name": "https",
            "href": "https://github.com/thalisonwilker/neo.git"
          },
          {
            "name": "ssh",
            "href": "git@github.com:thalisonwilker/neo.git"
          }
        ]
      }
    ]
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Repositórios listados (ou aviso de lista vazia). |
| `2` | Opção ou provedor inválido | Informa o erro de sintaxe. |
| `3` | Erro de autenticação (`401`/`403`) | Orienta executar `neo git auth login --provider <github\|bitbucket>`. |
| `4` | Workspace não encontrado (`404`) | Informa que o workspace não existe no provedor. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado (segue paginação automática `next`).

---

## `neo git repo search`

Filtra repositórios do workspace ativo buscando um termo no nome, no slug ou na descrição.

### Uso

```bash
neo git repo search --query <termo> [--workspace <slug>] [--provider <github|bitbucket>] [--limit <n>] [--json]
```

### Opções

| Opção | Obrigatório | Descrição |
|---|---|---|
| `--query` | **Sim** | Termo de busca (case-insensitive) para filtrar nome, slug ou descrição. |
| `--workspace` | Não | Workspace ou organização alvo. |
| `--provider` | Não | Provedor Git (`github` ou `bitbucket`). |
| `--limit` | Não | Quantidade máxima de resultados a retornar. |
| `--json` | Não | Emite a lista filtrada em JSON no `stdout`. |

### Exemplo

```bash
neo git repo search --query "auth"
neo git repo search --query "api" --provider bitbucket --limit 5 --json | jq '.[].slug'
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
            Repositórios no Bitbucket encontrados para 'auth'
    ┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃ Nome         ┃ Slug         ┃ Visibilidade ┃ Descrição                ┃
    ┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │ Serviço Auth │ servico-auth │ Privado      │ Autenticação e OAuth2    │
    └──────────────┴──────────────┴──────────────┴──────────────────────────┘
    ```

=== "Saída `--json`"
    ```json
    [
      {
        "name": "Serviço Auth",
        "slug": "servico-auth",
        "is_private": true,
        "description": "Autenticação e OAuth2",
        "updated_on": "2026-10-27T10:00:00Z",
        "main_branch": "main",
        "workspace": "minha-empresa",
        "web_url": "",
        "clone_links": []
      }
    ]
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Resultados exibidos (mesmo quando nenhum repositório corresponde ao termo). |
| `2` | `--query` omitido | Informa que `--query <termo>` é obrigatório em `neo git repo search`. |
| `3` | Erro de autenticação | Orienta executar `neo git auth login`. |
| `4` | Workspace não encontrado | Informa que o workspace não foi localizado (`404`). |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

---

## `neo git repo show`

Exibe os metadados completos e as URLs de clone (SSH e HTTPS) de um repositório específico ou do repositório Git do diretório atual.

### Uso

```bash
neo git repo show [<slug>] [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

### Opções e Argumentos

| Nome | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `<slug>` / `--repo` | Argumento ou Opção | Não *(se em diretório Git)* | Slug do repositório. Se omitido, o Neo detecta pelo `remote origin` local. |
| `--workspace` | Opção | Não | Workspace ou organização proprietária do repositório. |
| `--provider` | Opção | Não | Provedor Git (`github` ou `bitbucket`). |
| `--json` | Opção | Não | Emite os detalhes completos em JSON puro no `stdout`. |

### Exemplo

```bash
# Dentro de um repositório Git local (auto-detectado)
neo git repo show

# Especificando o repositório explicitamente e extraindo a URL SSH com jq
neo git repo show --repo core-backend --json | jq -r '.ssh_clone_url'
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    ╭─────────────── Repositório: core-backend (GitHub) ───────────────╮
    │ Nome: core-backend                                               │
    │ Slug: core-backend                                               │
    │ Workspace: minha-org                                             │
    │ Visibilidade: Privado                                            │
    │ Branch Padrão: main                                              │
    │ Descrição: API principal de serviços                             │
    │ Clone SSH: git@github.com:minha-org/core-backend.git             │
    │ Clone HTTPS: https://github.com/minha-org/core-backend.git       │
    │ Atualizado em: 2026-10-28                                        │
    ╰──────────────────────────────────────────────────────────────────╯
    ```

=== "Saída `--json`"
    ```json
    {
      "name": "core-backend",
      "slug": "core-backend",
      "is_private": true,
      "description": "API principal de serviços",
      "updated_on": "2026-10-28T10:00:00Z",
      "main_branch": "main",
      "workspace": "minha-org",
      "web_url": "https://github.com/minha-org/core-backend",
      "clone_links": [
        {
          "name": "https",
          "href": "https://github.com/minha-org/core-backend.git"
        },
        {
          "name": "ssh",
          "href": "git@github.com:minha-org/core-backend.git"
        }
      ],
      "ssh_clone_url": "git@github.com:minha-org/core-backend.git",
      "https_clone_url": "https://github.com/minha-org/core-backend.git",
      "provider": "github"
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Painel ou JSON exibido. |
| `3` | Erro de autenticação | Orienta executar `neo git auth login`. |
| `4` | Repositório não encontrado ou não informado fora de pasta Git | Orienta passar `--repo <slug>` ou verificar o nome do repositório. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

---

!!! note "Planejado"
    As ações adicionais de repositório abaixo estão especificadas no backlog e serão disponibilizadas nas próximas versões:

    - `neo git repo open [--repo <slug>]`: abre a página web do repositório no navegador padrão.
    - `neo git repo clone <slug> [--workspace <slug>] [--provider <github|bitbucket>]`: clona o repositório resolvendo a URL via API (hoje você pode clonar combinando `git clone "$(neo git repo show --repo <slug> --json | jq -r '.ssh_clone_url')"`).
    - `neo git repo create <nome> [--private|--public] [--description <texto>] [--yes]`: cria um novo repositório remoto com confirmação interativa.
