---
name: cli-comandos
description: Árvore dos comandos disponíveis no Neo, agrupados por módulo e recurso.
alwaysApply: false
---

# Árvore de comandos

Os itens abaixo mostram os comandos disponíveis agrupados como são digitados no terminal. Selecione o nome de um grupo para abrir sua documentação com argumentos e exemplos. Use `--help` após qualquer comando para consultar suas opções.

- **[`neo config`](config/index.md)**
    - `show` — visão geral das configurações.
    - **[`agent`](agent/config.md)** — preferências do agente:
        - `set` — define uma propriedade.
        - `get` — consulta uma propriedade.
        - `list` — lista as propriedades.
        - `unset` — remove uma propriedade.
- **[`neo git`](git/index.md)**
    - [`status`](git/status.md) — diagnóstico do contexto Git.
    - **[`config`](git/config.md)** — configuração Git:
        - `set` — define uma propriedade.
        - `get` — consulta uma propriedade.
        - `list` — lista as propriedades.
        - `unset` — remove uma propriedade.
    - **[`repo`](git/repo/index.md)** — repositórios:
        - `list` — lista repositórios remotos no workspace do provedor.
        - `remote-list` — alias para listagem de repositórios remotos.
        - `local-list` — lista repositórios locais registrados.
        - `search` — pesquisa repositórios remotos.
        - `show` — exibe detalhes de um repositório.
        - `select` — seleciona um repositório local.
        - `create` — cria e publica um repositório.
        - `edit` — altera a descrição no provedor.
    - **[`branch`](git/branch/index.md)** — branches locais:
        - `list` — lista branches.
        - `select` — seleciona uma branch.
        - `create` — cria uma branch.
        - `delete` — exclui uma branch.
    - **[`commits`](git/commits/index.md)** — histórico de commits:
        - `list` — lista commits.
        - `search` — pesquisa commits.
        - `show` — exibe um commit.
    - **[`pr`](git/pr/index.md)** — pull requests:
        - Sem subcomando: `neo git pr` lista PRs abertas.
        - `open` — abre uma PR.
        - `approve` — aprova uma PR com mensagem.
        - `decline` — recusa ou fecha uma PR.
        - `search` — pesquisa por ID ou título.
- **[`neo tasks`](tasks/index.md)** — tarefas do Shortcut:
    - [`create`](tasks/create.md) — cria uma tarefa.
    - [`list`](tasks/list.md) — lista tarefas.
    - [`search`](tasks/search.md) — pesquisa tarefas.
    - [`show`](tasks/show.md) — exibe uma tarefa.
    - [`analyze`](tasks/analyze.md) — analisa uma tarefa.
    - [`resume`](tasks/resume.md) — apresenta o quadro Kanban.
    - [`iterations`](tasks/iterations.md) — lista iterações.
    - [`whoami`](tasks/whoami.md) — identifica o membro autenticado.
    - **[`check`](tasks/check.md)** — checklist:
        - `list` — lista itens.
        - `add` — adiciona um item.
        - `complete` — conclui um item.
        - `uncomplete` — reabre um item.
    - **[`comment`](tasks/comment.md)** — comentários:
        - `list` — lista comentários.
        - `add` — adiciona um comentário.
    - **[`config`](tasks/config.md)** — configuração do Shortcut:
        - `set` — configura a credencial.
        - `get` — consulta a credencial configurada.
        - `delete` — remove a credencial.
        - `columns` — configura as colunas do quadro.
- **[`neo agent`](agent/index.md)** — agente de codificação:
    - [`status`](agent/status.md) — verifica o ambiente.
    - [`setup`](agent/setup.md) — prepara os arquivos de governança.
    - [`run`](agent/run.md) — inicia o agente.
- **[`neo fin`](fin/index.md)** — finanças pessoais:
    - **[`bank`](fin/bank.md)** — contas:
        - `create` — cria uma conta.
        - `get` — consulta uma conta.
        - `list` — lista contas.
        - `update` — atualiza uma conta.
        - `delete` — exclui uma conta.
    - **[`category`](fin/category.md)** — categorias:
        - `create` — cria uma categoria.
        - `get` — consulta uma categoria.
        - `list` — lista categorias.
        - `delete` — exclui uma categoria.
    - **[`tx`](fin/tx.md)** — transações:
        - `create` — cria uma transação.
        - `get` — consulta uma transação.
        - `list` — lista transações.
        - `update` — atualiza uma transação.
        - `delete` — exclui uma transação.
    - [`expense`](fin/tx.md) — registra uma despesa.
    - [`income`](fin/tx.md) — registra uma receita.
    - [`balance`](fin/summary.md) — exibe o balanço.
    - [`summary`](fin/summary.md) — exibe o resumo mensal.

Consulte também os [recursos Git planejados](git/planejado.md), que ainda não estão disponíveis como operações da CLI.
