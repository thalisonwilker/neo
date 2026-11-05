---
name: cli-git-repo-list
description: Lista os repositórios remotos disponíveis no workspace ou organização do provedor configurado.
alwaysApply: false
---

# neo git repo list
> Lista os repositórios remotos disponíveis no workspace do provedor Git ativo.

## Sintaxe

```bash
neo git repo list [--workspace <slug>] [--provider <github|bitbucket>] [--limit <num>] [--json]
```

## Descrição

O comando `neo git repo list` consulta a API do provedor Git configurado (GitHub ou Bitbucket Cloud), valida a conexão com o provedor e lista os repositórios remotos pertencentes ao workspace ou organização ativo.

A visualização em tabela do terminal apresenta:
- **Nome**: Nome do repositório no provedor.
- **Data Criação**: Data de criação no formato americano `MM/DD/YYYY`.
- **Última atualização**: Data da última alteração no formato americano `MM/DD/YYYY`.
- **Task**: Identificador da tarefa vinculada localmente (`#<TASK-ID>`) ou `-` quando não houver vínculo.

## Opções

| Opção | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--workspace` | Texto | Contexto/Padrão | Slug do workspace (Bitbucket) ou organização/usuário (GitHub). |
| `--provider` | `github` \| `bitbucket` | Contexto/Padrão | Provedor Git da consulta. |
| `--limit` | Inteiro | `20` | Quantidade máxima de repositórios retornados. |
| `--json` | Flag booleana | `false` | Saída formatada em JSON estruturado com metadados e task. |
| `--help` | Flag booleana | — | Exibe as instruções de uso. |

## Exemplos

### Listagem no terminal

```bash
neo git repo list --limit 10
```

### Especificando workspace e provedor

```bash
neo git repo list --workspace minha-org --provider github
```

### Saída estruturada em JSON

```bash
neo git repo list --json | jq '.[] | {name, task, created_on, updated_on}'
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Consulta executada com sucesso. |
| `2` | Erro de uso | Opção inválida (ex.: provedor desconhecido). |
| `3` | Autenticação | Credencial ausente ou inválida. Configure com `neo git config set api-key`. |
| `4` | Não encontrado | Workspace ou organização remota não existe. |

## Veja também

- [`neo git repo remote-list`](remote-list.md) — Alias de compatibilidade para `neo git repo list`.
- [`neo git repo local-list`](local-list.md) — Listar repositórios locais registrados no Neo.
- [`neo git repo search`](search.md) — Pesquisar repositórios remotos por nome ou termo.
- [`neo git repo show`](show.md) — Ver detalhes de um repositório remoto específico.
