---
name: cli-workspace
description: Manual do comando neo git workspace para gerenciamento de contas e organizações.
alwaysApply: false
---

# `neo git workspace`

Define em qual conta, organização (**GitHub**) ou workspace (**Bitbucket Cloud**) os comandos de repositório e commit vão operar por padrão.

- **No GitHub:** representa seu usuário pessoal ou qualquer organização acessível pelo token.
- **No Bitbucket Cloud:** representa o slug do Workspace (ex.: `acme_corp`, `minha-empresa`).

---

## Comandos

### `neo git workspace select`
Abre um seletor interativo no terminal para trocar de workspace usando o teclado, ou define diretamente via `--slug`:

=== "Menu Interativo"
    ```bash
    # Busca seus workspaces na API e permite escolher pelo número
    neo git workspace select
    ```

=== "Direto por Slug"
    ```bash
    neo git workspace select --slug acme_corp
    ```

---

### `neo git workspace set <slug>`
Atalho direto para fixar o workspace ativo sem abrir menu interativo:

```bash
# Define a organização ativa para o GitHub
neo git workspace set meu-time --provider github

# Define o workspace ativo para o Bitbucket
neo git workspace set acme_corp -p bitbucket
```

---

### `neo git workspace list`
Lista todos os workspaces/organizações disponíveis para o seu token e marca o selecionado com `[● Ativo]`:

=== "Provedor Padrão"
    ```bash
    neo git workspace list
    ```

=== "Escolhendo o Provedor (`-p`)"
    ```bash
    neo git workspace list --provider github
    neo git workspace list -p bitbucket
    ```

=== "Saída JSON (`--json`)"
    ```bash
    neo --json git workspace list | jq '.[] | {slug, name, is_active}'
    ```

---

### `neo git workspace current`
Mostra qual workspace está ativo no momento e se ele veio do `config.toml` ou do repositório Git local:

```bash
neo git workspace current
```
