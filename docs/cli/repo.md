---
name: cli-repo
description: Manual do comando neo git repo para gerenciamento de repositórios Git.
alwaysApply: false
---

# `neo git repo`

Lista, busca, clona e cria repositórios remotos no **GitHub** e no **Bitbucket Cloud** sem abrir o navegador.

---

## Comandos

### `neo git repo list`
Lista os repositórios do workspace ativo com visibilidade, linguagem/descrição e data de atualização:

```bash
# Usa o provedor e workspace padrão configurados
neo git repo list

# Consulta um provedor e organização específicos
neo git repo list --provider github --workspace minha-org

# Exporta lista em JSON para scripts
neo --json git repo list
```

---

### `neo git repo search <termo>`
Filtra repositórios por nome, slug ou descrição:

```bash
# Busca repositórios contendo "auth" no provedor ativo
neo git repo search auth

# Busca no Bitbucket Cloud
neo git repo search api --provider bitbucket
```

---

### `neo git repo clone <slug>`
Resolve a URL remota na API do provedor e executa o `git clone` no diretório atual:

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
Cria um repositório remoto no workspace ativo. Por segurança, pede confirmação interativa antes de criar (use `-y` em scripts de automação):

=== "Com Confirmação no Terminal"
    ```bash
    neo git repo create servico-pagamento --private
    ```

=== "Sem Prompt (Scripts / CI)"
    ```bash
    neo git repo create servico-pagamento --private -d "API de pagamentos" -y
    ```
