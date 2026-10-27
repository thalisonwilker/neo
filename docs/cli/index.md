---
name: cli-index
description: Visão geral da interface de linha de comando e opções globais do Neo.
alwaysApply: false
---

# Guia de Comandos da CLI

A interface de linha de comando do Neo foi projetada para ser rápida, visualmente agradável com **Rich** e totalmente integrável a pipelines de automação.

---

## Opções Globais

Todas as invocações aceitam as seguintes opções no início do comando:

| Flag | Descrição |
|---|---|
| `--help` | Exibe a mensagem de ajuda contextual do comando. |
| `--version`, `-V` | Exibe a versão atual instalada do Neo. |
| `--json` | Emite a saída em formato JSON estrito no `stdout`, suprimindo formatação visual. |
| `-v`, `--verbose` | Habilita logs detalhados de requisições HTTP e depuração interna. |

### Exemplo de Uso com `--json` e `jq`

```bash
# Filtrar nomes de repositórios diretamente com jq
uv run neo --json repo list | jq -r '.[].slug'
```

---

## Módulos Disponíveis

```mermaid
graph LR
    Neo["neo"] --> Workspace["workspace: Gestão de Contas/Organizações"]
    Neo --> Repo["repo: Gestão de Repositórios"]
    Neo --> Commits["commits: Histórico e Pesquisa"]
    Neo --> Story["story: Tarefas e Tickets no Shortcut"]
    Neo --> Config["config: Credenciais e Provedores"]
```

- [Workspaces](workspace.md): Alternância e listagem de workspaces/organizações ativas.
- [Repositórios](repo.md): Listagem, busca, clonagem e criação de repositórios.
- [Commits](commits.md): Investigação de histórico com auto-detecção git.
- [Stories](story.md): Consulta de chamados e análise automática de contexto.
