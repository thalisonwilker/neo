---
name: cli-git-config
description: Configuração e contexto dos comandos Git.
alwaysApply: false
---

# neo git config

Use `neo git config set`, `neo git config get`, `neo git config list` e `neo git config unset` para gerenciar preferências e contexto.

| Chave | Comportamento |
|---|---|
| `provider` | Provedor configurado: `github` ou `bitbucket`. Ao definir um novo provedor, as configurações do Git são resetadas e apenas o novo provedor é mantido. |
| `workspace` | Organização ou workspace no provedor. Sem argumento, lista os workspaces disponíveis para seleção interativa; com argumento, valida sua existência na API do provedor. |
| `api-key` | Credencial solicitada com entrada oculta e validada no provedor (retorna "Conexão efetuada" no sucesso ou "Conexão recusada" no erro). |
| `repo` | Caminho do repositório local selecionado. |
| `branch` | Branch ativa; definir uma branch faz checkout. |
| `task` | ID da tarefa associada ao repositório selecionado. |
| `default-branch`, `branch-pattern`, `commit-format` | Preferências Git existentes. |

```bash
neo git config set provider github
neo git config set workspace minha-organizacao
neo git config set api-key  # entrada oculta, exige provedor configurado
neo git config set repo /caminho/do/repo
neo git config set branch feature/minha-branch
neo git config set task 123
neo git config get task --json
neo git config list
neo git config unset task
neo git config unset repo
neo git config unset api-key  # pede confirmação; --yes dispensa a pergunta
```

A chave nunca é exibida por `get`, `list` ou `status`. Quando a validação remota falha, a credencial anterior é preservada e é exibido `Conexão recusada` (código de saída 3). O Bitbucket autentica diretamente via API REST com token Bearer, sem solicitar e-mail. Variáveis de ambiente continuam tendo precedência e não são removidas por `unset api-key`. `unset branch` não altera a branch ativa; use `neo git branch select` para trocar de branch.

Consulte [autenticação](auth.md), [branches](branch/index.md) e [status](status.md).
