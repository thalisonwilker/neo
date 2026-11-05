---
name: cli-git-repo-select
description: Registra e seleciona um repositório Git local existente como contexto ativo.
alwaysApply: false
---

# neo git repo select
> Registra um repositório Git local existente no Neo e define-o como o contexto ativo.

## Sintaxe

```bash
neo git repo select <caminho> [--json]
```

## Descrição

O comando `neo git repo select` recebe o caminho absoluto ou relativo de um diretório que seja a raiz de um repositório Git válido (contendo `.git/`). Ele registra o repositório na lista do Neo e define a chave `repo` no contexto local, permitindo que outros comandos operem sobre ele sem mudar de diretório no terminal.

## Parâmetros e Opções

| Argumento / Opção | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `<caminho>` | Argumento posicional | Sim | Caminho do repositório local existente (ex.: `/projetos/meu-repo` ou `.`). |
| `--json` | Flag booleana | Não | Retorna o status da seleção em formato JSON. |
| `--help` | Flag booleana | Não | Exibe a ajuda do comando. |

## Exemplos

### Selecionar repositório pelo caminho

```bash
neo git repo select /Users/dev/Projects/minha-api
```

### Selecionar o diretório atual

```bash
cd /Users/dev/Projects/minha-api
neo git repo select .
```

### Variante JSON

```bash
neo git repo select . --json
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Repositório selecionado com sucesso. |
| `2` | Erro de uso | Caminho não informado ou inválido. |
| `4` | Não encontrado | O caminho fornecido não existe ou não é um repositório Git válido. |

## Veja também

- [`neo git repo list`](list.md) — Listar repositórios registrados e verificar a seleção.
- [`neo git status`](../status.md) — Exibir status do contexto atual.

