---
name: cli-git-repo-remote-list
description: Lista os repositórios remotos disponíveis no workspace ou organização do provedor configurado (alias para repo list).
alwaysApply: false
---

# neo git repo remote-list
> Alias de compatibilidade para [`neo git repo list`](list.md).

## Sintaxe

```bash
neo git repo remote-list [--workspace <slug>] [--provider <github|bitbucket>] [--limit <num>] [--json]
```

## Descrição

O comando `neo git repo remote-list` é um alias para [`neo git repo list`](list.md). Ele consulta a API do provedor Git (GitHub ou Bitbucket Cloud) e lista os repositórios remotos associados ao workspace ou organização ativo.

## Opções

| Opção | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--workspace` | Texto | Contexto/Padrão | Slug do workspace (Bitbucket) ou organização/usuário (GitHub). |
| `--provider` | `github` \| `bitbucket` | Contexto/Padrão | Provedor Git da consulta. |
| `--limit` | Inteiro | `20` | Quantidade máxima de repositórios retornados. |
| `--json` | Flag booleana | `false` | Saída formatada em JSON estruturado. |
| `--help` | Flag booleana | — | Exibe as instruções de uso. |

## Exemplos

### Listagem no terminal

```bash
neo git repo remote-list --limit 10
```

### Filtrando via JSON com jq

```bash
neo git repo remote-list --provider github --json | jq '.[].name'
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Consulta executada com sucesso. |
| `2` | Erro de uso | Opção inválida (ex.: provedor desconhecido). |
| `3` | Autenticação | Credencial ausente ou inválida. Configure com `neo git config set api-key`. |
| `4` | Não encontrado | Workspace ou organização remota não existe. |

## Veja também

- [`neo git repo list`](list.md) — Comando principal de listagem remota.
- [`neo git repo local-list`](local-list.md) — Listar repositórios locais registrados no Neo.
- [`neo git repo search`](search.md) — Pesquisar repositórios remotos por nome ou termo.
- [`neo git repo show`](show.md) — Ver detalhes de um repositório remoto específico.
