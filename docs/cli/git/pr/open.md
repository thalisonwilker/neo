---
name: cli-git-pr-open
description: Abre um novo pull request no provedor a partir da branch local atual.
alwaysApply: false
---

# neo git pr open
> Abre um novo pull request no provedor a partir da branch local atual.

## Sintaxe

```bash
neo git pr open [--base <branch>] [--title <titulo>] [--description <texto>] [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git pr open` cria uma nova solicitação de pull request no provedor Git:
- **Origem automática:** Utiliza a branch local atual em checkout.
- **Destino (`--base`):** Se omitido no modo interativo, o Neo busca as branches remotas disponíveis e exibe um seletor no terminal.
- **Título e Descrição:** Se omitidos no modo interativo, são solicitados via prompt no terminal.
- **Pré-requisito:** A branch de origem deve existir previamente no provedor remoto (`origin`); o Neo valida e recusa a abertura caso a branch ainda não tenha sido enviada (`push`).

## Opções

| Opção | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--base` | Texto | Seleção interativa / `main` | Branch de destino da mesclagem (ex.: `main`, `develop`). |
| `--title` | Texto | Prompt interativo | Título do pull request. |
| `--description` | Texto | Prompt interativo | Descrição e notas da mudança. |
| `--repo` | Texto | Contexto ativo | Slug do repositório remoto. |
| `--workspace` | Texto | Contexto ativo | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Contexto ativo | Provedor Git. |
| `--json` | Flag booleana | `false` | Emite o pull request criado em formato JSON. |

## Exemplos

### Abertura interativa

```bash
neo git pr open
```

### Abertura com parâmetros explícitos

```bash
neo git pr open --base main --title "feat: adiciona busca de registros" --description "Implementa busca otimizada."
```

### Abertura em pipelines de CI

```bash
neo git pr open --base main --title "chore: build de release" --description "Versão gerada pelo CI" --json
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Pull request aberto com sucesso no provedor. |
| `2` | Erro de validação | Branch de origem não enviada para o remoto (`push` pendente) ou parâmetros ausentes em modo não interativo. |
| `3` | Autenticação | Token sem escopo de escrita (`pull-requests:write` ou `repo`). |

## Veja também

- [`neo git pr list`](list.md) — Listar PRs abertos.
- [`neo git pr approve`](approve.md) — Aprovar um PR aberto.

