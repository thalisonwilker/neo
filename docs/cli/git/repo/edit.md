---
name: cli-git-repo-edit
description: Atualiza a descrição de um repositório remoto no provedor Git.
alwaysApply: false
---

# neo git repo edit
> Atualiza metadados e descrição de um repositório remoto no provedor Git.

## Sintaxe

```bash
neo git repo edit --description <texto> [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git repo edit` envia uma requisição para a API do provedor Git atualizando a descrição pública/privada do repositório especificado (ou do repositório ativo no contexto).

## Opções

| Opção | Tipo | Padrão | Obrigatório | Descrição |
|---|---|---|---|---|
| `--description` | Texto | — | Sim | Nova descrição a ser aplicada ao repositório remoto. |
| `--repo` | Texto | Contexto ativo | Não | Slug do repositório a ser editado. |
| `--workspace` | Texto | Contexto ativo | Não | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Contexto ativo | Não | Provedor Git a atualizar. |
| `--json` | Flag booleana | `false` | Não | Retorna o resultado da atualização em JSON. |

## Exemplos

### Atualizar a descrição do repositório ativo

```bash
neo git repo edit --description "API RESTful de Pagamentos v2"
```

### Atualizar repositório específico via flags

```bash
neo git repo edit --repo checkout-service --description "Serviço de Checkout" --provider github
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Descrição atualizada com sucesso no provedor. |
| `2` | Erro de uso | Opção `--description` ausente ou repositório não resolvido. |
| `3` | Autenticação / Permissão | Token sem escopo de escrita (`repo` ou `repository:write`). |
| `4` | Não encontrado | Repositório não encontrado no provedor. |

## Veja também

- [`neo git repo show`](show.md) — Visualizar os dados atuais do repositório.
- [`neo git repo remote-list`](remote-list.md) — Listar repositórios do workspace.

