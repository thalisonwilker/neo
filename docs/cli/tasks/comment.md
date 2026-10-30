---
name: cli-tasks-comment
description: Manual do comando neo tasks comment add para registrar notas e comentários em stories do Shortcut.
alwaysApply: false
---

# neo tasks comment
> Registra notas, apontamentos e links de pull requests como comentários em uma story no Shortcut.

Com o comando `neo tasks comment add`, você registra comentários diretamente pelo terminal para manter o time atualizado sobre o andamento da demanda.

---

## Sintaxe

```bash
neo tasks comment add <task-id> "<texto>" [--service shortcut]
```

---

## Comandos Disponíveis

| Comando | Descrição | Exemplo de comando |
|---|---|---|
| `list` | Lista todos os comentários da story | `neo tasks comment list <task-id>` |
| `add` | Adiciona um comentário à story | `neo tasks comment add <task-id> "<comentário>"` |

---

## Exemplos

### 1. Listar comentários de uma story
```bash
neo tasks comment list 2153
# ou em modo JSON:
neo --json tasks comment list 2153
```

### 2. Adicionar comentário com link do PR
```bash
neo tasks comment add 2153 "PR aberto para revisão: https://github.com/empresa/repo/pull/42"
```

### 2. Registrar apontamento técnico em modo JSON
```bash
neo --json tasks comment add 2153 "Testes de carga executados com sucesso (p99 < 120ms)"
```

### 3. Visualizar comentários registrados
```bash
neo tasks show 2153
```
