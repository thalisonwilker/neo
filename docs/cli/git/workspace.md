---
name: cli-git-workspace
description: Configuração do workspace ativo para provedores Git.
alwaysApply: false
---

# Configuração de workspace Git

O workspace identifica uma organização ou conta no GitHub e um workspace no Bitbucket Cloud. O Neo permite selecionar o workspace de forma interativa a partir da lista retornada pela API do provedor ou informar diretamente um slug (que é validado na API):

```bash
# Seleção interativa: consulta a API e exibe lista numerada para escolha
neo git config set workspace

# Definição direta com validação de existência no provedor
neo git config set workspace minha-organizacao

# Consulta e remoção
neo git config get workspace
neo git config unset workspace
neo git status
```

Para uma consulta pontual, use a opção `--workspace <slug>` nos comandos que a aceitam. A precedência é opção de comando, `NEO_GIT_WORKSPACE`, configuração persistida e detecção do remote local. O grupo `neo git workspace` foi removido; consulte o [guia de migração](../../migration.md).

## Veja também
- [neo git config](config.md)
- [neo git status](status.md)
- [neo git repo](repo/index.md)
