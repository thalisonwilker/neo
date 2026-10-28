---
name: cli-status
description: Manual do comando neo git status e visão geral dos recursos planejados no backlog Git.
alwaysApply: false
---

# `neo git status`

Inspeciona o diretório atual e exibe um diagnóstico completo do repositório Git local, do provedor e workspace resolvidos e do estado da autenticação.

---

## `neo git status`

Consolida em uma única chamada o estado da working tree local e a resolução de contexto do Neo (`provider`, `workspace`, `repo` e credenciais).

### Uso

```bash
neo git status [--json]
```

### Opções

| Opção | Obrigatório | Descrição |
|---|---|---|
| `--json` | Não | Emite o diagnóstico completo em JSON puro no `stdout`. |

### Exemplo

```bash
# Diagnóstico visual no terminal
neo git status

# Verificar em um script qual provedor e workspace estão ativos no diretório atual
neo git status --json | jq '{provider, workspace, repo, authenticated}'
```

### Saída Humana e `--json`

=== "Saída Humana"
    ```text
    ╭─────────────────── Status do Contexto Git ───────────────────╮
    │ Repositório Local: Sim (branch: main, working tree limpa)    │
    │ Remote Origin: git@github.com:thalisonwilker/neo.git         │
    │ Provedor Ativo: github (config)                              │
    │ Workspace Ativo: thalisonwilker (remote)                     │
    │ Repositório Detectado: neo                                   │
    │ Autenticação: Autenticado (keyring)                          │
    ╰──────────────────────────────────────────────────────────────╯
    ```

=== "Saída `--json`"
    ```json
    {
      "local": {
        "is_git_repo": true,
        "current_branch": "main",
        "clean": true,
        "modified_files": 0,
        "remote_url": "git@github.com:thalisonwilker/neo.git"
      },
      "provider": "github",
      "provider_source": "config",
      "workspace": "thalisonwilker",
      "workspace_source": "remote",
      "repo": "neo",
      "authenticated": true,
      "auth_source": "keyring"
    }
    ```

### Erros e Códigos de Saída

| Código | Cenário | Mensagem e Ação |
|---|---|---|
| `0` | Sucesso | Diagnóstico exibido (funciona tanto dentro quanto fora de um repositório Git). |
| `2` | Valor inválido em `NEO_GIT_PROVIDER` | Informa que o provedor configurado na variável de ambiente não é suportado. |

### Suporte por Provedor

- **GitHub:** Suportado.
- **Bitbucket Cloud:** Suportado.

---

## Recursos Adicionais no Backlog

!!! note "Planejado"
    Os recursos abaixo fazem parte da especificação de evolução da gramática `neo git` e estão mapeados no backlog ([Spec 0010](https://github.com/thalisonwilker/neo/blob/main/specs/0010-branches-prs-e-detalhes-repo/spec.md)):

    - **Branches (`neo git branch`):**
      - `neo git branch list [--repo <slug>] [--limit <n>] [--json]`
      - `neo git branch show <nome> [--repo <slug>] [--json]`
      - `neo git branch create <nome> [--repo <slug>]`
      - `neo git branch remove <nome> [--repo <slug>] [--yes]`
    - **Pull Requests (`neo git pr`):**
      - `neo git pr list [--repo <slug>] [--state <open|merged|declined|all>] [--limit <n>] [--json]`
      - `neo git pr show <id> [--repo <slug>] [--json]`
      - `neo git pr search --query <termo> [--repo <slug>] [--json]`
      - `neo git pr create [--repo <slug>]`
    - **Tags (`neo git tag`):**
      - `neo git tag list | show <nome> | create <nome> | remove <nome> [--yes]`
    - **Releases (`neo git release`):**
      - `neo git release list | show <tag> | create <tag>` *(no Bitbucket Cloud, retornará código `5` sugerindo `neo git tag`)*.

