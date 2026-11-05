---
name: cli-git-repo-search
description: Pesquisa repositórios remotos por termo ou palavra-chave no provedor configurado.
alwaysApply: false
---

# neo git repo search
> Pesquisa repositórios remotos por nome ou termo no workspace do provedor configurado.

## Sintaxe

```bash
neo git repo search --query <termo> [--workspace <slug>] [--provider <github|bitbucket>] [--limit <num>] [--json]
```

## Descrição

O comando `neo git repo search` realiza busca por correspondência de texto na lista de repositórios do provedor Git. A opção `--query` é obrigatória e deve conter ao menos um caractere não vazio.

## Opções

| Opção | Tipo | Padrão | Obrigatório | Descrição |
|---|---|---|---|---|
| `--query` | Texto | — | Sim | Termo de pesquisa (busca por correspondência). |
| `--workspace` | Texto | Contexto | Não | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Contexto | Não | Provedor Git a consultar. |
| `--limit` | Inteiro | `20` | Não | Limite de resultados. |
| `--json` | Flag booleana | `false` | Não | Saída em JSON para automações. |

## Exemplos

### Busca de repositórios

```bash
neo git repo search --query "api"
```

### Busca em JSON

```bash
neo git repo search --query "service" --json | jq '.[].slug'
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Busca realizada (mesmo com 0 resultados encontrados). |
| `2` | Erro de uso | Opção `--query` ausente ou termo vazio. |
| `3` | Autenticação | Credencial ausente ou token inválido. |

## Veja também

- [`neo git repo remote-list`](remote-list.md) — Listar todos os repositórios remotos.
- [`neo git repo show`](show.md) — Exibir informações completas de um repositório encontrado.

