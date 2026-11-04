---
name: spec
description: Contrato da feature 0022 — refatoração do comando neo config show em 4 blocos tabulares (Git, Tasks, Agents e Serviços Configurados).
alwaysApply: true
---

# Spec — Refatoração do Comando `neo config show`

> **Fonte da verdade.** Status: implementado
> Tier: **Pequeno** (`spec.md` + `tasks.md` — evolução da interface CLI do comando `neo config show`).

## Resumo
Refatora a saída do comando `neo config show` para apresentar quatro blocos tabulares claros e focados:
1. **Git:** diagnóstico do repositório local, provedor ativo, workspace, branch atual e task relacionada;
2. **Tasks:** status do serviço de tarefas, provedor, workspace, colunas do board (To-Do-List com quebra de linha) e tarefa atual em andamento com progresso de checklist;
3. **Agents:** configuração minimalista do agente de codificação (`Code-Agent` e `Code-Agent-Model`);
4. **Serviços configurados:** tabela filtrada exibindo exclusivamente os serviços com credenciais ativas (`Serviço | Status`).

Além da exibição visual no terminal com Rich, suporta saída `--json` completa e estruturada.

---

## Critérios de Aceite

### AC-1: Bloco Git (`Status | Provedor | Workspace | Branch | Tasks`)
- **Dado** o comando `neo config show`;
- **Quando** renderizado no terminal;
- **Então** exibe uma tabela para o bloco **Git** contendo as colunas:
  - `Status`: `Ativo` se executado dentro de um repositório git válido, ou `Inativo` caso contrário;
  - `Provedor`: nome do provedor git configurado (`github`, `bitbucket`, etc.);
  - `Workspace`: slug do workspace configurado para o provedor git ativo (ou `-`);
  - `Branch`: nome da branch git local ativa (ex.: `main`, `feature/0022-...`) ou `-`;
  - `Tasks`: `#<id>` da tarefa associada (extraído do nome da branch se contiver número ou da tarefa ativa no Shortcut), ou `-`.

### AC-2: Bloco Tasks (`Status | Provedor | Workspace | To-Do-List | Tarefa atual`)
- **Dado** o comando `neo config show`;
- **Quando** renderizado no terminal;
- **Então** exibe uma tabela para o bloco **Tasks** contendo as colunas:
  - `Status`: `Configurado` se há credencial ativa para o serviço de tasks, ou `Não configurado`;
  - `Provedor`: nome do serviço (`shortcut`, etc.);
  - `Workspace`: workspace configurado ou padrão (ou `-`);
  - `To-Do-List`: nomes dos estados/colunas configurados para *A fazer*, *Fazendo* e *Feito*, formatados com um por linha:
    ```text
    A fazer: [nomes]
    Fazendo: [nomes]
    Feito: [nomes]
    ```
    (ou `Não configurado` se ausente);
  - `Tarefa atual`: identificação da tarefa em andamento. Se houver checklist: `#<id> <título> <completos>/<total>` (ex.: `#2182 Plano de Ataque 0/9`); se não houver checklist: `#<id> <título>`; ou `-` se nenhuma tarefa for localizada.

### AC-3: Bloco Agents (`Code-Agent | Code-Agent-Model`)
- **Dado** o comando `neo config show`;
- **Quando** renderizado no terminal;
- **Então** exibe uma tabela minimalista para o bloco **Agents** contendo as colunas:
  - `Code-Agent`: nome/comando do agente de codificação configurado (ex.: `antigravity` ou `agy`);
  - `Code-Agent-Model`: modelo configurado para o agente (ex.: `Gemini 3.8 Flash`) ou `-`.

### AC-4: Bloco de Serviços configurados (`Serviço | Status`)
- **Dado** o conjunto de serviços suportados pelo Neo (`github`, `bitbucket`, `shortcut`);
- **Quando** executado `neo config show`;
- **Então** a tabela de serviços exibe **apenas os serviços com status `Configurado`** (oculta serviços não configurados);
- **E** contém exatamente as colunas `Serviço` e `Status`. Caso nenhum serviço esteja configurado, exibe mensagem informativa indicando ausência de credenciais configuradas.

### AC-5: Suporte a `--json` Estruturado
- **Dado** a flag global `--json` (`neo --json config show`);
- **Quando** executado;
- **Então** retorna um payload JSON contendo as chaves estruturadas:
  - `git`: objeto com `{status, provider, workspace, branch, task_id}`;
  - `tasks`: objeto com `{status, provider, workspace, todo_list, current_task}`;
  - `agents`: objeto com `{code_agent, code_agent_model}`;
  - `services`: lista de objetos `[{"service": "...", "status": "Configurado"}]` contendo apenas serviços ativos.
- **E** encerra com código de saída `0`.
