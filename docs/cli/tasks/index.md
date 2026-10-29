---
name: cli-tasks-index
description: Visão geral do módulo neo tasks para integração com Shortcut e gestão ágil no terminal.
alwaysApply: false
---

# neo tasks
> Consulta e análise de tarefas e sprints sem sair do terminal via REST API v3 do Shortcut.

O módulo `neo tasks` permite acompanhar o fluxo de trabalho diário de forma integrada: visualização de quadro Kanban no terminal, busca de cards, análise contextual de histórias para início de desenvolvimento e gerenciamento de sprints.

---

## Sintaxe

```bash
neo tasks <ação> [argumentos] [--opções]
```

Diferente do módulo `git`, o módulo `tasks` suporta atalhos de uma letra para maior agilidade no fluxo diário (`-s`, `-i`, `-m`, `-a`, `-c`, `-l`, `-t`).

---

## Organização dos Comandos

O módulo `neo tasks` está organizado nos seguintes submenus funcionais:

### 1. Visão do Dia
Comandos focados no início do expediente e acompanhamento da sprint:
- [**Quadro Kanban (`neo tasks resume`)**](resume.md): Renderiza seu quadro Kanban com colunas *A fazer*, *Fazendo* e *Feito*.
- [**Membro Autenticado (`neo tasks whoami`)**](whoami.md): Confirma identidade e valida o token ativo.
- [**Sprints e Iterações (`neo tasks iterations`)**](iterations.md): Lista iterações cadastradas e identifica a sprint atual.

### 2. Consulta de Demandas
Pesquisa e detalhamento de cards:
- [**Listar Stories (`neo tasks list`)**](list.md): Tabela de histórias da iteração com filtro opcional por atribuição (`--mine`).
- [**Pesquisar Stories (`neo tasks search`)**](search.md): Busca de cards por palavra-chave em títulos ou descrições.
- [**Detalhes da Story (`neo tasks show`)**](show.md): Descrição completa, tipo, proprietários e links.

### 3. Análise e Vínculo de Contexto
- [**Análise de Story (`neo tasks analyze`)**](analyze.md): Extrai critérios de aceite e sugere nomes de branches e mensagens de commit.
- [**Vincular Demanda (`neo tasks bind` / `neo tasks unbind`)**](bind.md): Associa ou remove o vínculo explícito entre uma tarefa do Shortcut e o repositório Git local.

### 4. Configuração
- [**Configurar Shortcut (`neo tasks config`)**](config.md): Gerencia token de acesso e mapeamento das colunas do workflow.

---

## Opções Comuns do Módulo Tasks

| Opção | Atalho | Padrão | Descrição |
|---|---|---|---|
| `--service` | `-s` | `shortcut` | Provedor de tarefas (atualmente: `shortcut`). |
| `--iteration` | `-i` | *(atual)* | Nome, número ou ID da sprint (ou `'all'` para ignorar filtro). |
| `--limit` | `-l` | *(específico)* | Limita a quantidade máxima de registros. |
| `--json` | — | `False` | Emite JSON puro. Invoque no nível raiz (`neo --json tasks ...`). |

---

## Veja também
- [Conceitos Gerais da CLI](../index.md)
- [Guia: Fluxo Diário (Tasks → Branch → Commit)](../../guias/fluxo-diario.md)
- [neo git status](../git/status.md)

