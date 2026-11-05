---
name: cli-git-repo-local-list
description: Lista os repositórios locais registrados no Neo e destaca o repositório selecionado no contexto.
alwaysApply: false
---

# neo git repo local-list
> Lista os repositórios locais registrados no Neo e destaca o repositório atualmente selecionado.

## Sintaxe

```bash
neo git repo local-list [--json]
```

## Descrição

O comando `neo git repo local-list` exibe todos os repositórios locais que já foram registrados no Neo (via `neo git repo create` ou `neo git repo select`). Na saída tabular humana, o repositório ativo no contexto é sinalizado visualmente com "Sim" na coluna "Selecionado", além de exibir a Task vinculada localmente (se houver).

## Opções

| Opção | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--json` | Flag booleana | `false` | Exibe a lista de repositórios locais em formato JSON puro. |
| `--help` | Flag booleana | — | Exibe as instruções de uso do comando. |

## Exemplos

### Visualização no terminal

```bash
neo git repo local-list
```

### Variante em JSON para automações

```bash
neo git repo local-list --json
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Repositórios locais listados com sucesso. |
| `1` | Erro geral | Falha de leitura do registro local de contexto. |

## Veja também

- [`neo git repo list`](list.md) — Listar repositórios remotos no workspace do provedor.
- [`neo git repo select`](select.md) — Selecionar um repositório local existente no contexto.
- [`neo git status`](../status.md) — Visualizar o contexto ativo completo de Git e Tasks.

