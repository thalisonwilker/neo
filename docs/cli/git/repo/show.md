---
name: cli-git-repo-show
description: Exibe detalhes, metadados e URLs de clone de um repositório remoto.
alwaysApply: false
---

# neo git repo show
> Exibe detalhes detalhados, metadados e URLs de um repositório remoto.

## Sintaxe

```bash
neo git repo show [--repo <slug>] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git repo show` recupera as informações detalhadas de um repositório remoto (nome, descrição, visibilidade pública/privada, URLs SSH e HTTPS para clone e branch padrão). Se `--repo` não for fornecido, utiliza o repositório selecionado no contexto ou o detectado no diretório atual.

## Opções

| Opção | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--repo` | Texto | Contexto ativo | Nome ou slug do repositório remoto a ser consultado. |
| `--workspace` | Texto | Contexto ativo | Workspace ou organização remota. |
| `--provider` | `github` \| `bitbucket` | Contexto ativo | Provedor Git a consultar. |
| `--json` | Flag booleana | `false` | Saída formatada em JSON. |

## Exemplos

### Visualizar repositório atual

```bash
neo git repo show
```

### Visualizar repositório específico

```bash
neo git repo show --repo minha-api --provider github
```

### Extrair URL de clone via JSON

```bash
neo git repo show --repo minha-api --json | jq -r '.clone_urls.https'
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Detalhes exibidos com sucesso. |
| `2` | Erro de uso | Repositório não pôde ser resolvido e `--repo` não foi informado. |
| `3` | Autenticação | Falha de autenticação no provedor remoto. |
| `4` | Não encontrado | Repositório não encontrado no workspace ou conta remota. |

## Veja também

- [`neo git repo remote-list`](remote-list.md) — Listar repositórios disponíveis.
- [`neo git repo edit`](edit.md) — Atualizar descrição do repositório remoto.

