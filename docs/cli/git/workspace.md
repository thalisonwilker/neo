---
name: cli-git-workspace
description: Configuração do workspace ativo para provedores Git.
alwaysApply: false
---

# Configuração de workspace Git

O workspace identifica uma organização ou conta no GitHub e um workspace no Bitbucket Cloud. Configure o slug, consulte seu valor e remova a preferência usando:

```bash
neo git config set workspace minha-organizacao
neo git config get workspace
neo git config unset workspace
neo git status
```

Para uma consulta pontual, use a opção `--workspace <slug>` nos comandos que a aceitam. A precedência é opção de comando, `NEO_GIT_WORKSPACE`, configuração persistida e detecção do remote local. O grupo `neo git workspace` foi removido; consulte o [guia de migração](../../migration.md).

## Veja também
- [neo git config](config.md)
- [neo git status](status.md)
- [neo git repo](repo.md)
