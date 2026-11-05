---
name: cli-git-repo-list
description: Lista os repositórios Git locais registrados e indica o repositório selecionado no contexto.
alwaysApply: false
---

# neo git repo list
> Lista os repositórios locais registrados no Neo e destaca o repositório atualmente selecionado.

## Sintaxe

```bash
neo git repo list [--json]
```

## Descrição

O comando `neo git repo list` exibe todos os repositórios locais que já foram registrados no Neo (via `neo git repo create` ou `neo git repo select`). Na saída tabular humana, o repositório ativo no contexto é sinalizado visualmente com uma estrela (`*`) ou indicador de seleção.

## Opções

| Opção | Tipo | Padrão | Descrição |
|---|---|---|---|
| `--json` | Flag booleana | `false` | Exibe a lista de repositórios em formato JSON puro. |
| `--help` | Flag booleana | — | Exibe as instruções de uso do comando. |

## Exemplos

### Visualização no terminal

```bash
neo git repo list
```

**Saída humana típica:**
```text
┌───┬────────────┬─────────────────────────────┬───────────┐
│   │ Repositório│ Caminho                     │ Provedor  │
├───┼────────────┼─────────────────────────────┼───────────┤
│ * │ neo        │ /Users/dev/Projects/neo     │ github    │
│   │ backend    │ /Users/dev/Projects/backend │ bitbucket │
└───┴────────────┴─────────────────────────────┴───────────┘
```

### Variante em JSON para automações

```bash
neo git repo list --json | jq '.[] | select(.selected == true).path'
```

**Saída JSON:**
```json
[
  {
    "name": "neo",
    "path": "/Users/dev/Projects/neo",
    "provider": "github",
    "selected": true
  },
  {
    "name": "backend",
    "path": "/Users/dev/Projects/backend",
    "provider": "bitbucket",
    "selected": false
  }
]
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Repositórios listados com sucesso (inclusive se lista vazia). |
| `2` | Erro de uso | Parâmetro ou opção inválida fornecida na linha de comando. |

## Veja também

- [`neo git repo select`](select.md) — Selecionar um repositório local existente no contexto.
- [`neo git repo remote-list`](remote-list.md) — Listar repositórios remotos na organização/workspace.
- [`neo git status`](../status.md) — Visualizar o contexto ativo completo de Git e Tasks.

