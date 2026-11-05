---
name: spec
description: Contrato da feature (critérios de aceite). Base enquanto a feature está ativa.
alwaysApply: true
---

# Spec — 0028 Refactor comando neo git repo list

> **Fonte da verdade.** Status: implementado
> Os critérios de aceite são (a) o contrato com o negócio, (b) o oráculo de teste,
> (c) o prompt para o agente de IA implementar. Escreva-os para serem executáveis.

## Resumo
Refatora o comando `neo git repo list` para consultar a API do provedor Git ativo (GitHub ou Bitbucket Cloud), validar a conexão e listar os repositórios remotos do workspace selecionado em uma tabela com colunas Nome, Data Criação (MM/DD/YYYY), Última atualização (MM/DD/YYYY) e Task (`#<TASK-ID>`), mantendo compatibilidade com `remote-list` e disponibilizando a listagem de repositórios locais via `local-list`.

## Critérios de aceite

### AC-1: Listagem remota de repositórios via `neo git repo list`
- **Dado** um provedor Git configurado com credenciais válidas e um workspace ativo (resolvido via `--workspace`, config, env ou padrão).
- **Quando** o usuário executa `neo git repo list`.
- **Então** o Neo valida a conexão e consulta a API do provedor (GitHub ou Bitbucket).
- **E** exibe uma tabela com o título do provedor contendo as colunas: `Nome`, `Data Criação`, `Última atualização`, `Task`.
- **E** as datas são exibidas no formato americano `MM/DD/YYYY`.
- **E** a coluna `Task` exibe `#{task_id}` caso o repositório possua vínculo no registro local (`git-context.json`), ou `-` caso contrário.

### AC-2: Validação de conexão e credenciais do provedor
- **Dado** que as credenciais do provedor não estão configuradas ou são inválidas/rejeitadas pela API do provedor (HTTP 401/403).
- **Quando** o usuário executa `neo git repo list`.
- **Então** o Neo interrompe a execução com código de saída semântico `3` (`AUTH_ERROR`).
- **E** exibe uma mensagem de erro orientando a configuração da credencial com `neo git config set api-key`.

### AC-3: Suporte a flags `--workspace`, `--provider`, `--limit` e `--json`
- **Dado** o comando `neo git repo list`.
- **Quando** o usuário passa `--workspace <slug>`, `--provider <github|bitbucket>` ou `--limit <n>`.
- **Então** a consulta respeita o workspace, o provedor e a quantidade máxima solicitados.
- **Quando** o usuário passa a flag `--json`.
- **Então** o Neo emite a lista de repositórios estruturada em JSON contendo `name`, `created_on`, `updated_on`, `task` (e campos de DTO do repositório) sem renderizar tabelas Rich.

### AC-4: Tratamento de workspace sem repositórios
- **Dado** um workspace válido que não possui nenhum repositório cadastrado.
- **Quando** o usuário executa `neo git repo list`.
- **Então** o Neo exibe uma mensagem amigável no painel indicando que nenhum repositório foi encontrado no workspace informado (ou lista vazia `[]` em modo `--json`), encerrando com código `0`.

### AC-5: Compatibilidade com `remote-list` e preservação da listagem local via `local-list`
- **Dado** a refatoração do comando `list`.
- **Quando** o usuário executa `neo git repo remote-list`.
- **Então** o comportamento é idêntico ao `neo git repo list` (alias de compatibilidade).
- **Quando** o usuário executa `neo git repo local-list`.
- **Então** o Neo lista os repositórios locais registrados no contexto do Neo (`git-context.json`) com as colunas `Caminho`, `Selecionado`, `Task`.

## Matriz de decisão

| Provedor configurado | Credencial válida | Workspace resolvido | Repositórios encontrados | Resultado observado | AC |
|---|---|---|---|---|---|
| Não configurado | — | — | — | Erro de uso / instrução de configuração (`code 2`) | AC-2 |
| Sim | Não / Inválida | — | — | Erro de autenticação (`code 3`) | AC-2 |
| Sim | Sim | Não resolvido | — | Erro indicando necessidade de workspace (`code 2`) | AC-2 |
| Sim | Sim | Sim | 0 | Painel "Nenhum repositório encontrado" (`code 0`) | AC-4 |
| Sim | Sim | Sim | >= 1 (terminal) | Tabela `Nome` \| `Data Criação` (MM/DD/YYYY) \| `Última atualização` (MM/DD/YYYY) \| `Task` (`#<TASK-ID>` ou `-`) | AC-1 |
| Sim | Sim | Sim | >= 1 (`--json`) | Saída JSON com `created_on`, `updated_on`, `task`, etc. (`code 0`) | AC-3 |

## Casos de borda e erros
- Repositório com data de criação ou atualização nula ou ausente na API → exibir `-` no lugar da data.
- Task ID já cadastrado com `#` prefixado ou sem `#` no `git-context.json` → normalizar para exibir exatamente `#<TASK-ID>` na tabela.
- Falha de conexão de rede ou timeout com a API → erro emitido com código semântico (`code 1` ou correspondente de rede) sem quebrar o CLI com stack trace cru.

## Fora de escopo
- Edição remota de repositórios diretamente pelo comando `list` (utilizar `neo git repo edit`).
- Criação de novos repositórios remotos (utilizar `neo git repo create`).
- Modificação na API de provedores de tasks (Shortcut).

## Rastreabilidade
- Spec anterior substituída em parte: `specs/0023-atualizacao-comandos-git/spec.md`
- ADRs relacionados:
  - `docs/architecture/adr/0002-tech-stack-core.md`
  - `docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md`
  - `docs/architecture/adr/0006-observabilidade-e-ux-cli.md`

