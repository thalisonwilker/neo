---
name: cli-git-branch-delete
description: Exclui com segurança uma branch local do repositório ativo.
alwaysApply: false
---

# neo git branch delete
> Exclui uma branch local de forma segura, exigindo confirmação interativa ou flag de bypass.

## Sintaxe

```bash
neo git branch delete <nome> [--yes] [--json]
```

## Descrição

O comando `neo git branch delete` exclui uma branch local existente. Por segurança:
- **Não realiza exclusão forçada:** Se a branch possuir commits não mergeados, a operação é rejeitada para evitar perda acidental de código.
- **Protege a branch ativa:** Não é permitido excluir a branch que estiver atualmente em checkout.
- **Solicita confirmação:** Exige confirmação interativa do usuário no terminal, a menos que `--yes` seja fornecido.

## Parâmetros e Opções

| Argumento / Opção | Tipo | Padrão | Obrigatório | Descrição |
|---|---|---|---|---|
| `<nome>` | Argumento posicional | — | Sim | Nome da branch a ser excluída. |
| `--yes` | Flag booleana | `false` | Não | Pula a confirmação interativa no terminal. |
| `--json` | Flag booleana | `false` | Não | Retorna o status de exclusão em JSON. |

## Exemplos

### Exclusão com confirmação interativa

```bash
neo git branch delete feature/concluida
```

### Exclusão não interativa em scripts/CI

```bash
neo git branch delete feature/concluida --yes
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Branch excluída com sucesso. |
| `2` | Erro de validação | Tentativa de excluir a branch ativa ou branch inexistente. |
| `4` | Branch não mergeada | A branch possui commits não integrados; o Neo bloqueia a exclusão para evitar perda de dados. |

## Veja também

- [`neo git branch list`](list.md) — Listar branches locais remanescentes.
- [`neo git branch select`](select.md) — Fazer checkout para outra branch antes da exclusão.

