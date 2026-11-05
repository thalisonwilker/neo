---
name: config-tasks
description: Guia de configuração do módulo neo tasks e integração com o Shortcut.
alwaysApply: false
---

# Configuração de Tasks (Shortcut)

O módulo `neo tasks` integra-se com a API do **Shortcut** para gerenciar stories, iterações e quadros Kanban diretamente pelo terminal.

---

## Token da API do Shortcut

Para autenticar com o Shortcut, gere um API Token nas configurações da sua conta no Shortcut e execute:

```bash
# Salvar token do Shortcut de forma segura (prompt com entrada oculta)
neo tasks config set
```

O token é armazenado no Keyring do sistema operacional ou em `~/.config/neo/credentials.toml` com permissão `0600`.

### Variável de Ambiente (Automação e CI/CD)

Em pipelines e scripts automatizados, defina a variável de ambiente:

| Contexto | Variável Principal | Alternativa | Descrição |
|---|---|---|---|
| **Shortcut (Tasks)** | `SHORTCUT_API_TOKEN` | `SHORTCUT_TOKEN` | Token da API v3 do Shortcut para `neo tasks`. |

---

## Mapeamento de Colunas Kanban

O comando `neo tasks resume` exibe um resumo das stories distribuídas nas colunas **A fazer**, **Fazendo** e **Feito**. Você pode configurar os nomes das colunas de acordo com o fluxo do seu time:

```bash
# Mapear colunas do quadro Kanban
neo tasks config columns
```

Consulte todos os comandos em [Referência de Tasks](../../cli/tasks/index.md).

