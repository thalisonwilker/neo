---
name: cli-tasks-check
description: Manual dos comandos neo tasks check para gerenciamento de checklist items em stories do Shortcut.
alwaysApply: false
---

# neo tasks check
> Gerencia itens de checklist (subtarefas/tasks) dentro de uma story no Shortcut.

Com o grupo `neo tasks check`, você pode adicionar novos itens ao checklist da história, marcá-los como concluídos à medida que avança na implementação ou reabri-los caso seja necessário.

---

## Sintaxe

```bash
neo tasks check <ação> [argumentos] [--opções]
```

---

## Comandos Disponíveis

| Comando | Descrição | Exemplo de comando |
|---|---|---|
| `list` | Lista todos os itens de checklist da story | `neo tasks check list <task-id>` |
| `add` | Adiciona um item de checklist à story | `neo tasks check add <task-id> "<descrição>"` |
| `complete` | Marca o item de checklist como concluído (alias `done`) | `neo tasks check complete <task-id> <check-id>` |
| `uncomplete` | Desmarca o item de checklist, reabrindo-o (alias `undone`) | `neo tasks check uncomplete <task-id> <check-id>` |

---

## Exemplos

### 1. Listar itens de checklist de uma story
```bash
neo tasks check list 2153
# ou em modo JSON:
neo --json tasks check list 2153
```

### 2. Adicionar itens de checklist a uma story
```bash
neo tasks check add 2153 "Criar migration do banco de dados"
neo tasks check add 2153 "Implementar endpoints REST"
neo tasks check add 2153 "Cobrir com testes unitários e E2E"
```

### 2. Concluir um item de checklist
```bash
neo tasks check complete 2153 1001
# ou utilizando o atalho:
neo tasks check done 2153 1001
```

### 3. Reabrir um item de checklist
```bash
neo tasks check uncomplete 2153 1001
# ou utilizando o atalho:
neo tasks check undone 2153 1001
```

### 4. Consultar os itens atualizados no detalhe da story
```bash
neo tasks show 2153
```
