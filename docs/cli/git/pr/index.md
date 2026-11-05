---
name: cli-git-pr-index
description: Visão geral do gerenciamento de Pull Requests no GitHub e Bitbucket Cloud.
alwaysApply: false
---

# neo git pr

O comando `neo git pr` gerencia o ciclo de vida completo de Pull Requests no GitHub e Bitbucket Cloud: listagem de PRs abertos, abertura interativa ou via opções, aprovação com mensagens de revisão, recusa/fechamento seguro e pesquisa abrangente por ID ou título.

---

## Ações Disponíveis

| Comando | Descrição |
|---|---|
| [`neo git pr list`](list.md) | Lista pull requests abertos no repositório remoto (invocado também como `neo git pr`). |
| [`neo git pr open`](open.md) | Abre um novo pull request no provedor a partir da branch atual. |
| [`neo git pr approve`](approve.md) | Aprova um pull request com mensagem de revisão ou comentário. |
| [`neo git pr decline`](decline.md) | Recusa e fecha um pull request sem mesclar (merge). |
| [`neo git pr search`](search.md) | Pesquisa pull requests por ID numérico exato ou texto no título. |

---

## Resolução de Contexto

Por padrão, as operações utilizam o repositório selecionado e a URL `origin` configurada. As opções `--provider`, `--workspace` e `--repo` estão disponíveis em todos os subcomandos para direcionar consultas a destinos específicos.
Consulte a documentação de cada subcomando nos links acima.

