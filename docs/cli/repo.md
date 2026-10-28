---
name: cli-repo
description: Manual do comando neo git repo para gerenciamento de repositórios Git.
alwaysApply: false
---

# `neo git repo`

O módulo `repo` permite listar, pesquisar, clonar e criar repositórios no **GitHub** e **Bitbucket Cloud**.

---

## Comandos

### `neo git repo list`
Lista os repositórios disponíveis no workspace ativo.

```bash
neo git repo list
# Forçando provedor ou workspace específico
neo git repo list --provider github --workspace minha-org
```

---

### `neo git repo search <termo>`
Pesquisa repositórios por nome, slug ou palavras-chave na descrição.

```bash
neo git repo search auth
neo git repo search api --provider bitbucket
```

---

### `neo git repo clone <slug>`
Clona um repositório resolvendo automaticamente a URL remota via API:

=== "SSH (Padrão)"
    ```bash
    neo git repo clone core-backend --ssh
    ```

=== "HTTPS"
    ```bash
    neo git repo clone core-backend --https
    ```

---

### `neo git repo create <nome>`
Cria um novo repositório com confirmação interativa de segurança.

=== "Com Confirmação Interativa"
    ```bash
    neo git repo create servico-pagamento --private
    ```

=== "Sem Prompt (CI / Scripts)"
    ```bash
    neo git repo create servico-pagamento --private -d "API de pagamentos" -y
    ```
