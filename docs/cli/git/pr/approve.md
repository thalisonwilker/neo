---
name: cli-git-pr-approve
description: Aprova um pull request aberto com mensagem de revisão ou comentário associado.
alwaysApply: false
---

# neo git pr approve
> Aprova um pull request com mensagem de revisão ou comentário no provedor.

## Sintaxe

```bash
neo git pr approve <id> [--message <texto>] [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git pr approve` registra uma aprovação no pull request indicado:
- **No GitHub:** Envia a revisão com o evento `APPROVE` acompanhada da mensagem.
- **No Bitbucket Cloud:** Publica um comentário com a mensagem e, em seguida, registra a aprovação. Se o comentário for publicado com sucesso mas a aprovação falhar (ex.: regras de autorização), o Neo reporta a falha parcial e preserva o comentário.
- Se `--message` for omitida no modo interativo, o terminal solicita a mensagem; em modo `--json`, `--message` é obrigatória.

## Parâmetros e Opções

| Argumento / Opção | Tipo | Padrão | Obrigatório | Descrição |
|---|---|---|---|---|
| `<id>` | Inteiro | — | Sim | Número identificador do pull request. |
| `--message` | Texto | Prompt interativo | Sim (em `--json`) | Mensagem da revisão/aprovação. |
| `--repo` | Texto | Contexto ativo | Não | Slug do repositório remoto. |
| `--workspace` | Texto | Contexto ativo | Não | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Contexto ativo | Não | Provedor Git. |
| `--json` | Flag booleana | `false` | Não | Retorna o status da aprovação em JSON. |

## Exemplos

### Aprovação com mensagem explícita

```bash
neo git pr approve 42 --message "Revisado e aprovado com sucesso."
```

### Aprovação não interativa com JSON

```bash
neo git pr approve 42 --message "LGTM via CI" --json
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Pull request aprovado com sucesso. |
| `2` | Erro de uso | ID numérico ausente ou `--message` não informada em modo `--json`. |
| `3` | Permissão | O usuário logado não tem permissão de aprovação ou tentou aprovar o próprio PR em repositório com restrição. |
| `4` | Não encontrado | Pull request com o ID indicado não existe. |

## Veja também

- [`neo git pr decline`](decline.md) — Recusar ou fechar um pull request.
- [`neo git pr search`](search.md) — Localizar o ID do PR antes de aprovar.

