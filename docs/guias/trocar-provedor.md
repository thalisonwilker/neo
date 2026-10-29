---
name: guias-trocar-provedor
description: Guia para alternar e trabalhar simultaneamente com GitHub e Bitbucket Cloud no Neo.
alwaysApply: false
---

# Trocar de Provedor (GitHub ↔ Bitbucket)

O Neo foi projetado para devs e times que atuam em ecossistemas mistos, permitindo alternar de forma transparente entre **GitHub** e **Bitbucket Cloud**.

---

## 1. Como o Provedor é Resolvido

Quando você executa comandos como `neo git repo list` ou `neo git commits list`, o Neo resolve o provedor ativo na seguinte ordem:

1. **Flag explícita:** `--provider github` ou `--provider bitbucket` (sobrescreve tudo para a execução atual).
2. **Variável de ambiente:** `NEO_GIT_PROVIDER`.
3. **Configuração persistida:** chave `provider` na seção `[git]` do `~/.config/neo/config.toml`.
4. **Detecção automática:** URL do `remote origin` do repositório Git local (`github.com` ou `bitbucket.org`).
5. **Fallback:** Provedor com credencial válida ativa.

---

## 2. Autenticando Ambos os Provedores

Você pode manter credenciais salvas para ambos os provedores ao mesmo tempo no Keyring:

=== "Autenticar no GitHub"
    ```bash
    neo git auth login --provider github
    ```

=== "Autenticar no Bitbucket Cloud"
    ```bash
    neo git auth login --provider bitbucket
    # Informe o e-mail da conta Atlassian e o API Token gerado
    ```

Verifique o estado com:
```bash
neo git auth status
```

---

## 3. Alternando o Provedor Padrão

Para definir qual provedor utilizar quando estiver fora de um repositório Git local:

```bash
# Definir GitHub como padrão
neo git config set provider github

# Definir Bitbucket como padrão
neo git config set provider bitbucket
```

---

## 4. Consultas Pontuais em Provedor Específico

Não é necessário alterar a configuração global para fazer uma consulta em outro serviço:

```bash
# Listar repositórios de uma organização no GitHub
neo git repo list --provider github --workspace minha-org

# Listar repositórios de um workspace no Bitbucket
neo git repo list --provider bitbucket --workspace meu-workspace
```

---

## Veja também
- [neo git auth](../cli/git/auth.md) — Gerenciamento de credenciais
- [neo git config](../cli/git/config.md) — Configurações persistidas
- [neo git workspace](../cli/git/workspace.md) — Gerenciamento de workspaces e organizações

