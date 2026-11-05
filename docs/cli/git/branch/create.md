---
name: cli-git-branch-create
description: Cria uma nova branch local no repositório ativo a partir do estado atual.
alwaysApply: false
---

# neo git branch create
> Cria uma nova branch local no repositório ativo a partir do HEAD atual.

## Sintaxe

```bash
neo git branch create <nome> [--json]
```

## Descrição

O comando `neo git branch create` cria uma nova branch local no repositório Git do contexto ativo. A nova branch é baseada no commit atual da branch ativa.

## Parâmetros e Opções

| Argumento / Opção | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `<nome>` | Argumento posicional | Sim | Nome da nova branch a ser criada (ex.: `feature/auth-jwt`). |
| `--json` | Flag booleana | Não | Retorna o status de criação em JSON. |
| `--help` | Flag booleana | Não | Exibe a ajuda do subcomando. |

## Exemplos

### Criando uma branch de feature

```bash
neo git branch create feature/minha-task
```

### Variante JSON

```bash
neo git branch create bugfix/fix-login --json
```

## Erros comuns e códigos de saída

| Código | Significado | Causa e Resolução |
|---|---|---|
| `0` | Sucesso | Branch criada com sucesso. |
| `2` | Erro de uso / Conflito | Nome da branch não fornecido, inválido ou branch com mesmo nome já existe. |

## Veja também

- [`neo git branch select`](select.md) — Alternar para a nova branch criada.
- [`neo git branch list`](list.md) — Listar branches existentes.

