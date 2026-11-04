---
name: cli-git-auth
description: Autenticação segura de provedores Git.
alwaysApply: false
---

# Autenticação Git

Configure o provedor e informe sua chave por entrada oculta:

```bash
neo git config set provider github
neo git config set api-key
neo git config get api-key
neo git config unset api-key
```

Para Bitbucket, use `neo git config set provider bitbucket` antes de `neo git config set api-key` e informe também o e-mail da conta. O Neo testa a nova credencial no provedor antes de salvá-la; uma falha preserva a credencial anterior. A chave não é aceita como argumento e não aparece em logs ou nas consultas.

O Keyring do sistema operacional é usado para armazenamento, com fallback para `~/.config/neo/credentials.toml` com permissões restritas. Variáveis de ambiente têm precedência: `NEO_GITHUB_TOKEN` para GitHub e `NEO_BITBUCKET_EMAIL` mais `NEO_BITBUCKET_TOKEN` para Bitbucket. Remover a credencial armazenada não altera o ambiente.

`neo git config unset api-key` pede confirmação e aceita `--yes`. `neo git config get api-key --json` mostra estado e origem para o provedor configurado. O grupo `neo git auth` foi removido; veja o [guia de migração](../../migration.md).

Consulte [configuração](config.md) e [diagnóstico de contexto](status.md).
