---
name: cli-git-pr-search
description: Pesquisa pull requests por ID numérico exato ou correspondência de texto no título.
alwaysApply: false
---

# neo git pr search
> Pesquisa pull requests por ID numérico ou texto no título (abrangendo abertos, recusados e mesclados).

## Sintaxe

```bash
neo git pr search <termo> [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git pr search` permite localizar pull requests em qualquer estado (`OPEN`, `MERGED`, `DECLINED`/`CLOSED`):
- **Termo numérico:** Se `<termo>` for puramente numérico (ex.: `42`), busca o pull request pelo ID exato.
- **Termo textual:** Se `<termo>` contiver texto, realiza busca por substring case-insensitive no título dos pull requests percorrendo o histórico.

## Parâmetros e Opções

| Argumento / Opção | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `<termo>` | Argumento posicional | Sim | Número identificador exato ou trecho de texto do título. |
| `--repo` | Texto | Não | Slug do repositório remoto. |
| `--workspace` | Texto | Não | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Não | Provedor Git a consultar. |
| `--json` | Flag booleana | Não | Retorna os resultados encontrados em JSON. |

## Exemplos

### Buscar por número exato

```bash
neo git pr search 42
```

### Buscar por palavra-chave no título

```bash
neo git pr search "auth"
```

### Variante JSON com jq

```bash
neo git pr search "release" --json | jq '.[] | {id: .id, state: .state, title: .title}'
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Pesquisa realizada com sucesso (inclusive com 0 resultados). |
| `2` | Erro de uso | Termo de busca ausente ou vazio. |
| `3` | Autenticação | Falha de autenticação no provedor remoto. |

## Veja também

- [`neo git pr list`](list.md) — Listar somente os pull requests abertos.
- [`neo git pr show`](open.md) — Ver detalhes e criar novos PRs.

