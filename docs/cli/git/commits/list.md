---
name: cli-git-commits-list
description: Lista os commits recentes do repositório remoto com filtros opcionais por autor e limite.
alwaysApply: false
---

# neo git commits list
> Lista commits recentes do repositório remoto com filtros opcionais por autor e limite.

## Sintaxe

```bash
neo git commits list [--author <autor>] [--limit <num>] [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git commits list` consulta a API do provedor Git e recupera o histórico recente de commits da branch ativa no repositório remoto. É possível restringir a consulta por autor e delimitar o número máximo de registros retornados.

## Opções

| Opção | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--author` | Texto | — | Filtra commits por nome ou e-mail do autor. |
| `--limit` | Inteiro | `20` | Quantidade máxima de commits a retornar. |
| `--repo` | Texto | Contexto ativo | Slug do repositório (inferido se dentro de repositório Git local). |
| `--workspace` | Texto | Contexto ativo | Workspace ou organização de destino. |
| `--provider` | `github` \| `bitbucket` | Contexto ativo | Provedor Git a consultar. |
| `--json` | Flag booleana | `false` | Emite a resposta em JSON puro. |

## Exemplos

### Listando o histórico recente

```bash
neo git commits list --limit 5
```

### Filtrando commits por autor

```bash
neo git commits list --author "Maria" --limit 10
```

### Processamento via JSON com jq

```bash
neo git commits list --json | jq '.[0] | {sha: .sha[0:7], message: .message, author: .author}'
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Histórico listado com sucesso. |
| `2` | Erro de uso | Parâmetro inválido ou repositório não resolvido. |
| `3` | Autenticação | Credencial ausente ou inválida no provedor. |
| `4` | Não encontrado | Repositório remoto não encontrado. |

## Veja também

- [`neo git commits search`](search.md) — Pesquisar commits por texto na mensagem.
- [`neo git commits show`](show.md) — Exibir detalhes completos de um commit específico.

