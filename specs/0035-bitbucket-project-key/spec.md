---
name: spec
description: Contrato para utilização da Key de projeto Bitbucket na listagem, configuração e criação de repositórios.
alwaysApply: true
---

# Spec — Uso da Key do Projeto Bitbucket

> **Status:** implementado · Tier: pequeno.

## Resumo

Utilizar a chave (`key`) do projeto Bitbucket (em vez do UUID) na listagem interativa, na persistência de configuração e no payload de criação de repositórios, evitando erros de rejeição pela API do Bitbucket.

## Critérios de aceite

### AC-1: Listagem e seleção interativa com Key
- **Dado** o provedor Bitbucket e um workspace válido selecionado interativamente ou via argumento,
- **Quando** o Neo lista os projetos acessíveis do workspace,
- **Então** apresenta a lista numerada exibindo o nome e a chave do projeto no formato `Nome (KEY)` (ex.: `Easygestor (EASY)`).
- **E** após seleção válida, persiste juntos o workspace e a `key` do projeto selecionado em `config.toml` (`project = "<KEY>"`), informando sucesso com a chave salva.

### AC-2: Exibição da Key na visualização de configurações
- **Dado** o comando `neo git config show` (modo texto ou `--json`),
- **Quando** o provedor configurado for Bitbucket,
- **Então** exibe a `key` do projeto configurado no campo de projeto (ou indica ausência se não houver).

### AC-3: Criação de repositório com Key do projeto
- **Dado** o provedor Bitbucket, um workspace efetivo e um projeto configurado com sua `key`,
- **Quando** executar `neo git repo create`,
- **Então** a requisição de criação de repositório envia o payload com `{"project": {"key": "<KEY>"}}`.
- **E** a criação é aceita pelo Bitbucket sem erro de identificador inválido.

### AC-4: Modelo de dados e validação de Key
- **Dado** a consulta de projetos à API REST 2.0 do Bitbucket (`/workspaces/{workspace}/projects`),
- **Quando** a resposta for processada,
- **Então** o DTO `GitProject` valida e mapeia obrigatoriamente o campo `key` (e `name`); caso a `key` não esteja presente ou seja vazia, falha com erro amigável informando que o projeto não possui chave válida.

### AC-5: Preservação em falhas ou cancelamentos
- **Dado** erro de rede, lista vazia de projetos ou cancelamento/índice inválido na seleção de projeto,
- **Quando** a operação for abortada,
- **Então** o workspace e o projeto configurados anteriormente são preservados intactos.

## Matriz de decisão

| Provedor | Operação | Entrada / Estado | Resultado Esperado | AC |
|---|---|---|---|---|
| Bitbucket | `git config set workspace` | Projetos com `key` e `name` | Exibe `Nome (KEY)`, salva `key` em `config.toml` | AC-1, AC-4 |
| Bitbucket | `git config set workspace` | Falha, lista vazia ou abort | Preserva configuração anterior | AC-5 |
| Bitbucket | `git config show` | Projeto com `key` configurado | Exibe valor da `key` (humano e JSON) | AC-2 |
| Bitbucket | `git repo create` | Projeto configurado com `key` | Envia `{"project": {"key": "<KEY>"}}` | AC-3 |
| Bitbucket | API retorna projeto sem `key` | Payload inválido | Lança erro indicando ausência de chave | AC-4 |

## Casos de borda e erros

- Projetos com nomes contendo caracteres especiais ou espaços exibem o nome completo e sua `key` entre parênteses.
- O campo `key` do Bitbucket geralmente é composto por caracteres alfanuméricos e sublinhados; não deve conter `{}` de UUID.
- Erros de comunicação na API do Bitbucket continuam sem expor credenciais no output.

## Fora de escopo

- Alterar o comportamento do provedor GitHub.
- Criar novos projetos no Bitbucket via CLI.

## Rastreabilidade

- Corrige e refina [0034 — Seleção de projeto Bitbucket](../0034-selecao-projeto-bitbucket/spec.md), substituindo o uso de UUID por Key.
