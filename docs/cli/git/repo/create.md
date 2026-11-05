---
name: cli-git-repo-create
description: Cria um repositório local e no provedor Git com commit inicial e push da branch padrão.
alwaysApply: false
---

# neo git repo create
> Cria um repositório Git localmente e no provedor remoto, gerando commit inicial e enviando a branch padrão.

## Sintaxe

```bash
neo git repo create <nome> --path <caminho> [--public] [--workspace <slug>] [--provider <github|bitbucket>] [--json]
```

## Descrição

O comando `neo git repo create` automatiza o fluxo de bootstrap de novos projetos:
1. Valida se o diretório de destino não existe (recusa sobrescrever diretórios preexistentes).
2. Cria o repositório no provedor remoto (**privado por padrão**, a menos que `--public` seja informado).
3. Inicializa o repositório Git local com os arquivos `README.md` e `AGENTS.md`.
4. Cria o commit inicial, vincula o remote `origin` e faz o push da branch principal padrão.
5. Registra e seleciona o novo repositório no contexto local do Neo.

Se qualquer etapa remota falhar (ex.: rede ou permissão), o Neo preserva o diretório local e reporta com precisão o estado de cada etapa para recuperação manual sem perda de dados.

## Parâmetros e Opções

| Argumento / Opção | Tipo | Padrão | Obrigatório | Descrição |
|---|---|---|---|---|
| `<nome>` | Argumento posicional | — | Sim | Nome / slug do repositório a ser criado. |
| `--path` | Caminho no sistema | — | Sim | Caminho local onde o diretório do projeto será criado. |
| `--public` | Flag booleana | `false` | Não | Cria o repositório como público (padrão é privado). |
| `--workspace` | Texto | Contexto | Não | Workspace ou organização de destino. |
| `--provider` | `github` \| `bitbucket` | Contexto | Não | Provedor Git onde o repositório remoto será criado. |
| `--json` | Flag booleana | `false` | Não | Retorna o status e metadados de criação em JSON. |

## Exemplos

### Criando um repositório privado (padrão)

```bash
neo git repo create minha-api --path /Users/dev/Projects/minha-api
```

### Criando um repositório público

```bash
neo git repo create biblioteca-open --path /Users/dev/Projects/biblioteca-open --public
```

### Saída estruturada em JSON

```bash
neo git repo create auth-service --path /Users/dev/Projects/auth-service --json
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Repositório criado, versionado e enviado com sucesso. |
| `2` | Erro de uso | Opção `--path` não informada ou nome inválido. |
| `3` | Autenticação | Falha de credenciais para criar no provedor remoto. |
| `4` | Conflito / Erro | Caminho local já existe ou repositório com mesmo nome já existe no provedor. |

## Veja também

- [`neo git repo list`](list.md) — Listar repositórios registrados.
- [`neo git repo edit`](edit.md) — Editar descrição de repositório existente.

