---
name: cli-git-branch-select
description: Faz checkout para uma branch local existente e atualiza a branch ativa do contexto.
alwaysApply: false
---

# neo git branch select
> Faz checkout para a branch local indicada e atualiza o contexto ativo do Neo.

## Sintaxe

```bash
neo git branch select <nome> [--json]
```

## Descrição

O comando `neo git branch select` realiza a operação de checkout do Git para a branch indicada e persiste o nome da branch no contexto local do Neo. Isso altera o estado do diretório de trabalho de forma transparente para todas as ferramentas e IDEs.

## Parâmetros e Opções

| Argumento / Opção | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `<nome>` | Argumento posicional | Sim | Nome da branch local existente para fazer checkout. |
| `--json` | Flag booleana | Não | Retorna o resultado da seleção em formato JSON. |
| `--help` | Flag booleana | Não | Exibe as opções de uso. |

## Exemplos

### Alternando para a branch principal

```bash
neo git branch select main
```

### Alternando para uma branch de feature

```bash
neo git branch select feature/minha-task
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Checkout realizado e contexto atualizado. |
| `2` | Erro de uso | Nome não fornecido ou branch inexistente localmente. |
| `4` | Conflito no workspace | Alterações locais não commitadas impedem o checkout seguro. |

## Veja também

- [`neo git branch list`](list.md) — Listar branches locais disponíveis.
- [`neo git status`](../status.md) — Visualizar o status do repositório e branch ativa.

