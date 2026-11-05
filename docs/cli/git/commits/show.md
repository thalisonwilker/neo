---
name: cli-git-commits-show
description: Inspeciona e exibe os detalhes completos de um commit específico pelo hash SHA.
alwaysApply: false
---

# neo git commits show
> Exibe os detalhes completos de um commit específico a partir do seu hash SHA.

## Sintaxe

```bash
neo git commits show <sha> [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git commits show` recupera todas as informações de um commit no repositório remoto: mensagem completa, autor, e-mail, data e hora de autoria, e links de visualização no provedor.

## Parâmetros e Opções

| Argumento / Opção | Tipo | Padrão | Obrigatório | Descrição |
|---|---|---|---|---|
| `<sha>` | Argumento posicional | — | Sim | Hash SHA completo ou abreviado (mínimo 7 caracteres). |
| `--repo` | Texto | Contexto ativo | Não | Slug do repositório remoto. |
| `--workspace` | Texto | Contexto ativo | Não | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Contexto ativo | Não | Provedor Git a consultar. |
| `--json` | Flag booleana | `false` | Não | Saída em JSON puro. |

## Exemplos

### Visualizar commit pelo hash

```bash
neo git commits show a1b2c3d
```

### Variante JSON

```bash
neo git commits show a1b2c3d --json | jq '{author: .author, message: .message}'
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Detalhes do commit exibidos com sucesso. |
| `2` | Erro de uso | Hash `<sha>` ausente ou com formato inválido. |
| `3` | Autenticação | Falha de autenticação com o provedor. |
| `4` | Não encontrado | Commit ou repositório não encontrado no provedor remoto. |

## Veja também

- [`neo git commits list`](list.md) — Listar histórico para obter hashes recentes.
- [`neo git commits search`](search.md) — Pesquisar commits por mensagem.

