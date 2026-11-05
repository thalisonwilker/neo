---
name: cli-git-pr-list
description: Lista os pull requests abertos no repositório com paginação automática.
alwaysApply: false
---

# neo git pr list
> Lista os pull requests abertos no repositório remoto com suporte a paginação automática.

## Sintaxe

```bash
neo git pr [list] [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git pr list` (também executado simplesmente como `neo git pr` sem subcomandos) consulta o provedor Git e recupera todos os pull requests em estado aberto (`OPEN`). A listagem percorre as páginas do provedor e exibe ID, título, estado, branches de origem e destino, e URL direta para o navegador.

## Opções

| Opção | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--repo` | Texto | Contexto ativo | Slug do repositório remoto. |
| `--workspace` | Texto | Contexto ativo | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Contexto ativo | Provedor Git a consultar. |
| `--json` | Flag booleana | `false` | Emite a lista de pull requests em formato JSON estruturado. |

## Exemplos

### Listagem no terminal

```bash
neo git pr
```

### Variante JSON para automações

```bash
neo git pr --json | jq '.[] | {id: .id, title: .title, source: .source}'
```

**Saída JSON:**
```json
[
  {
    "id": 42,
    "title": "feat(auth): adiciona suporte a JWT",
    "source": "feature/auth-jwt"
  }
]
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Pull requests listados com sucesso (inclusive se lista vazia `[]`). |
| `2` | Erro de uso | Repositório não pôde ser resolvido. |
| `3` | Autenticação | Credencial ausente ou token sem permissão de leitura de PRs. |

## Veja também

- [`neo git pr open`](open.md) — Abrir um novo pull request.
- [`neo git pr search`](search.md) — Pesquisar PRs (abertos, fechados ou mesclados).

