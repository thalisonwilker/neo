---
name: cli-git-repo-create
description: Cria e clona um repositório remoto, prepara os arquivos e publica o commit inicial.
alwaysApply: false
---

# neo git repo create

Cria um repositório remoto, clona-o e publica os arquivos iniciais.

## Sintaxe

```bash
neo git repo create <nome> [--path <diretório-pai>] [--default-branch <nome>] [--description <texto>] [--public]
```

O Neo valida a conexão, cria o remoto privado por padrão e clona em um subdiretório com o nome do repositório. Em seguida cria `README.md` com o nome e a descrição, se informada, e `AGENTS.md` vazio; faz o commit `first commit` e envia a branch principal. Após o push, registra e seleciona o repositório e exibe um comando `cd` para acessá-lo.

| Opção | Padrão | Descrição |
|---|---|---|
| `--path` | Diretório atual | Diretório pai do clone; deve existir. |
| `--default-branch` | `main` | Nome da branch principal. |
| `--description` | Sem descrição | Descrição no provedor e no README. |
| `--public` | Privado | Cria o repositório público. |

```bash
neo git repo create minha-api --path /Users/dev/Projects --description "Minha API" --default-branch main
```

O clone ficará em `/Users/dev/Projects/minha-api`. O Neo não sobrescreve um destino existente. Em caso de falha, informa a etapa e preserva os recursos já criados para recuperação manual. O modo global `neo --json` fornece saída estruturada.

## Veja também

- [`neo git repo list`](list.md)
- [`neo git repo edit`](edit.md)

No Bitbucket, configure o workspace com `neo git config set workspace` e selecione um projeto antes de criar o repositório. O Neo usa o projeto selecionado para esse workspace; se ele não estiver configurado, o comando orienta refazer a seleção.
