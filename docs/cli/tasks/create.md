---
name: cli-tasks-create
description: Manual do comando neo tasks create para criação de stories associadas à iteração atual no Shortcut.
alwaysApply: false
---

# neo tasks create
> Cria uma nova tarefa (story) no Shortcut, associando-a automaticamente à iteração atual ativa e ao usuário logado.

O comando `neo tasks create` permite registrar demandas rapidamente a partir do terminal sem necessidade de abrir a interface web do Shortcut, atribuindo automaticamente o card à sprint atual e ao seu perfil.

---

## Sintaxe

```bash
neo tasks create <título> [--opções]
```

---

## Opções

| Opção | Atalho | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `<título>` | — | Sim | — | Título / nome da nova task. |
| `--description` | `-d` | Não | — | Descrição detalhada do card. |
| `--type` | `-t` | Não | `feature` | Tipo da story: `feature`, `bug`, `chore`. |
| `--iteration` | `-i` | Não | `current` | Iteração (Sprint): `current` (padrão), `none` (sem sprint) ou ID/nome. |
| `--owner` | — | Não | `me` | Responsável: `me` (usuário logado), `none` (sem owner) ou ID do membro. |
| `--workflow-state-id` | — | Não | — | ID do estado inicial no workflow do Shortcut. |
| `--service` | `-s` | Não | `shortcut` | Provedor de tarefas (`shortcut`). |

---

## Exemplos

### 1. Criar uma nova tarefa associada à sprint atual
```bash
neo tasks create "Implementar autenticação JWT" -d "Adicionar middleware de validação e refresh token"
```

### 2. Criar um bug sem vincular à sprint
```bash
neo tasks create "Corrigir vazamento de memória no worker" -t bug -i none
```

### 3. Criar uma task em modo JSON para scripts e automações
```bash
neo --json tasks create "Nova automação de deploy"
```
