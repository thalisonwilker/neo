---
name: config-index
description: Visão geral das configurações, preferências e credenciais do Neo CLI.
alwaysApply: false
---

# Guia de Configurações

O Neo separa **configuração de preferências** (`~/.config/neo/config.toml`) de **credenciais de autenticação** (Keyring do sistema operacional ou `~/.config/neo/credentials.toml`).

A documentação de configuração está organizada nas seguintes categorias:

- [**Git**](git/basic.md): preferências da seção `[git]`, chaves suportadas, precedência de resolução, credenciais e variáveis de ambiente para CI/CD.
- [**Agents**](agents/code-agent.md): preferências do agente de código por IA (**Google Antigravity CLI**) e integração com ferramentas SDD.
- [**Tasks**](tasks/index.md): autenticação com a API do Shortcut e mapeamento de colunas do Kanban.

---

## Estrutura de Arquivos de Configuração

| Arquivo | Permissão | Finalidade |
|---|---|---|
| `~/.config/neo/config.toml` | `0600` | Preferências de provedor Git, workspace, branch, commits e agente de IA. |
| `~/.config/neo/credentials.toml` | `0600` | Fallback para armazenamento de tokens e credenciais caso o Keyring do SO não esteja disponível. |

Consulte também o comando [`neo config show`](../cli/comandos.md) para visualizar um resumo do seu ambiente atual.
