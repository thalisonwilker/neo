---
name: cli-git-commits-search
description: Pesquisa commits cuja mensagem contenha o termo especificado no provedor Git.
alwaysApply: false
---

# neo git commits search
> Pesquisa commits no histórico remoto cuja mensagem contenha o termo informado.

## Sintaxe

```bash
neo git commits search --query <termo> [--author <autor>] [--limit <num>] [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git commits search` realiza uma busca de texto na mensagem dos commits no repositório remoto. A opção `--query` é obrigatória e pode ser combinada com filtros adicionais como `--author` e `--limit`.

## Opções

| Opção | Tipo | Padrão | Obrigatório | Descrição |
|---|---|---|---|---|
| `--query` | Texto | — | Sim | Termo textual obrigatório para buscar na mensagem do commit. |
| `--author` | Texto | — | Não | Filtra commits por nome ou e-mail do autor. |
| `--limit` | Inteiro | `20` | Não | Quantidade máxima de commits a retornar. |
| `--repo` | Texto | Contexto ativo | Não | Slug do repositório remoto. |
| `--workspace` | Texto | Contexto ativo | Não | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Contexto ativo | Não | Provedor Git a consultar. |
| `--json` | Flag booleana | `false` | Não | Emite a resposta em JSON puro. |

## Exemplos

### Pesquisando commits de correção

```bash
neo git commits search --query "fix(auth)" --limit 5
```

### Pesquisa combinando autor e termo

```bash
neo git commits search --query "feat" --author "Maria" --limit 10
```

### Extraindo hashes via JSON

```bash
neo git commits search --query "release" --json | jq -r '.[].sha[0:7]'
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Pesquisa realizada com sucesso. |
| `2` | Erro de uso | Opção `--query` ausente ou termo vazio. |
| `3` | Autenticação | Falha de autenticação com o provedor. |

## Veja também

- [`neo git commits list`](list.md) — Listar histórico recente sem filtro textual.
- [`neo git commits show`](show.md) — Ver detalhes de um commit específico encontrado.

