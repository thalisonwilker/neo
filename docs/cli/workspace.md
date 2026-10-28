---
name: cli-workspace
description: Manual do comando neo git workspace para gerenciamento de contas e organizações.
alwaysApply: false
---

# `neo git workspace`

O comando `workspace` gerencia a conta ou organização ativa nos provedores Git suportados (**Bitbucket Cloud** e **GitHub**).

---

## Conceitos por Provedor

- **Bitbucket:** Corresponde a um Workspace (ex: `acme_corp`, `minha-empresa`).
- **GitHub:** Corresponde ao usuário logado ou a qualquer organização à qual o token tem acesso.

---

## Comandos

### `neo git workspace list`
Lista todos os workspaces/organizações disponíveis, marcando com `[● Ativo]` o que estiver selecionado.

=== "Exemplo Padrão"
    ```bash
    neo git workspace list
    ```

=== "Especificando Provedor"
    ```bash
    neo git workspace list --provider github
    neo git workspace list -p bitbucket
    ```

---

### `neo git workspace current`
Exibe o workspace atualmente selecionado e sua origem (configuração local persistida ou detecção remota).

```bash
neo git workspace current
```

---

### `neo git workspace select`
Abre um menu interativo com navegação por teclado no terminal para seleção visual, ou define diretamente via flag `--slug`:

=== "Interativo"
    ```bash
    neo git workspace select
    ```

=== "Por Slug Direto"
    ```bash
    neo git workspace select --slug acme_corp
    ```

---

### `neo git workspace set <slug>`
Atalho conveniente para definir o workspace ativo:

```bash
neo git workspace set meu-time --provider github
```
