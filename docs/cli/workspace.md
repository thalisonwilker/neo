---
name: cli-workspace
description: Manual do comando neo workspace para gerenciamento de contas e organizações.
alwaysApply: false
---

# `neo workspace`

O comando `workspace` gerencia a conta ou organização ativa nos provedores Git suportados (**Bitbucket Cloud** e **GitHub**).

---

## Conceitos por Provedor

- **Bitbucket:** Corresponde a um Workspace (ex: `acme_corp`, `minha-empresa`).
- **GitHub:** Corresponde ao usuário logado ou a qualquer organização à qual o token tem acesso.

---

## Comandos

### `neo workspace list`
Lista todos os workspaces/organizações disponíveis, marcando com `[● Ativo]` o que estiver selecionado.

=== "Exemplo Padrão"
    ```bash
    uv run neo workspace list
    ```

=== "Especificando Provedor"
    ```bash
    uv run neo workspace list --provider github
    uv run neo workspace list -p bitbucket
    ```

---

### `neo workspace current`
Exibe o workspace atualmente selecionado e sua origem (configuração local persistida ou detecção remota).

```bash
uv run neo workspace current
```

---

### `neo workspace select`
Abre um menu interativo com navegação por teclado no terminal para seleção visual, ou define diretamente via flag `--slug`:

=== "Interativo"
    ```bash
    uv run neo workspace select
    ```

=== "Por Slug Direto"
    ```bash
    uv run neo workspace select --slug acme_corp
    ```

---

### `neo workspace set <slug>`
Atalho conveniente para definir o workspace ativo:

```bash
uv run neo workspace set meu-time --provider github
```
