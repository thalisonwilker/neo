---
name: cli-git-pr-decline
description: Recusa e fecha um pull request sem realizar merge no repositório remoto.
alwaysApply: false
---

# neo git pr decline
> Recusa e fecha um pull request sem mesclar as alterações.

## Sintaxe

```bash
neo git pr decline <id> [--yes] [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git pr decline` fecha (no GitHub) ou recusa (no Bitbucket Cloud) o pull request indicado sem mesclar seus commits. A operação solicita confirmação no terminal interativo, a menos que a flag `--yes` seja passada.

## Parâmetros e Opções

| Argumento / Opção | Tipo | Padrão | Obrigatório | Descrição |
|---|---|---|---|---|
| `<id>` | Inteiro | — | Sim | Número identificador do pull request. |
| `--yes` | Flag booleana | `false` | Não | Pula o pedido de confirmação no terminal (obrigatório em `--json`). |
| `--repo` | Texto | Contexto ativo | Não | Slug do repositório remoto. |
| `--workspace` | Texto | Contexto ativo | Não | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Contexto ativo | Não | Provedor Git. |
| `--json` | Flag booleana | `false` | Não | Retorna o status da recusa em JSON. |

## Exemplos

### Recusando com confirmação interativa

```bash
neo git pr decline 42
```

### Recusando sem prompt interativo

```bash
neo git pr decline 42 --yes
```

### Em pipelines com JSON

```bash
neo git pr decline 42 --yes --json
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Pull request fechado/recusado com sucesso. |
| `2` | Erro de uso | ID numérico ausente ou `--yes` ausente em execução não interativa. |
| `4` | Não encontrado | Pull request não existe no repositório. |

## Veja também

- [`neo git pr approve`](approve.md) — Aprovar um pull request.
- [`neo git pr list`](list.md) — Listar PRs abertos.

