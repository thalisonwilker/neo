---
name: cli-git-branch-list
description: Lista as branches locais do repositório selecionado e destaca a branch ativa.
alwaysApply: false
---

# neo git branch list
> Lista todas as branches locais do repositório ativo e destaca a branch em checkout.

## Sintaxe

```bash
neo git branch list [--json]
```

## Descrição

O comando `neo git branch list` inspeciona o repositório Git local ativo no contexto e lista todas as branches disponíveis localmente. A branch ativa no momento é indicada com um asterisco (`*`) na saída tabular humana.

## Opções

| Opção | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--json` | Flag booleana | `false` | Retorna a lista de branches estruturada em JSON. |
| `--help` | Flag booleana | — | Exibe as instruções de uso. |

## Exemplos

### Listagem no terminal

```bash
neo git branch list
```

### Extrair a branch atual via JSON

```bash
neo git branch list --json | jq -r '.[] | select(.current == true).name'
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Branches listadas com sucesso. |
| `2` | Erro de contexto | Nenhum repositório local selecionado no contexto ou fora de um diretório Git. |

## Veja também

- [`neo git branch create`](create.md) — Criar uma nova branch local.
- [`neo git branch select`](select.md) — Fazer checkout para outra branch.

