---
name: spec
description: Contrato da feature (critérios de aceite). Base enquanto a feature está ativa.
alwaysApply: true
---

# Spec — 0030 Refactor git config set workspace

> **Fonte da verdade.** Status: implementado
> Os critérios de aceite são (a) o contrato com o negócio, (b) o oráculo de teste,
> (c) o prompt para o agente de IA implementar. Escreva-os para serem executáveis.

## Resumo
Refatora o comando `neo git config set workspace`. Ao ser executado sem argumento de valor, o comando consulta a API do provedor Git ativo (GitHub ou Bitbucket Cloud), recupera a lista de workspaces/organizações disponíveis para a conta autenticada, exibe uma lista numerada no terminal com Slug e Nome, e solicita ao usuário que selecione um workspace digitando o número correspondente. Quando um slug é fornecido diretamente como argumento, o comando valida a existência do workspace na lista retornada pela API do provedor antes de salvar a configuração.

## Critérios de aceite

### AC-1: Seleção interativa de workspace a partir da lista do provedor
- **Dado** um provedor Git configurado com credenciais válidas.
- **Quando** o usuário executa `neo git config set workspace` sem informar o valor.
- **Então** o Neo consulta a API do provedor ativo e recupera os workspaces disponíveis.
- **E** exibe uma lista ou tabela numerada no terminal contendo o número de índice `[1..N]`, o Slug e o Nome de cada workspace.
- **E** solicita ao usuário: `Número do workspace`.
- **Quando** o usuário escolhe um número válido no intervalo.
- **Então** o Neo salva o slug do workspace correspondente em `config.toml` (`[git].workspace`) e exibe mensagem de sucesso.

### AC-2: Validação de workspace passado como argumento direto
- **Dado** o comando `neo git config set workspace <slug>`.
- **Quando** o usuário informa o slug diretamente como argumento.
- **Então** o Neo consulta a API do provedor ativo para validar a existência do workspace.
- **Se** o workspace/organização existir na lista do provedor (comparação insensível a maiúsculas pelo slug ou login), o Neo salva a configuração e exibe mensagem de sucesso.
- **Se** o workspace não for encontrado na lista retornada pela API, o Neo emite erro indicando que o workspace não existe ou não é acessível pela conta autenticada, encerrando com código `4` (`NOT_FOUND`).

### AC-3: Validação de seleção numérica inválida no prompt
- **Dado** a listagem interativa de workspaces.
- **Quando** o usuário digita um número menor que 1 ou maior que a quantidade de workspaces disponíveis.
- **Então** o Neo cancela a operação emitindo erro de uso (`USAGE_ERROR`, código de saída `2`) e preserva a configuração anterior.

### AC-4: Tratamento de ausência de provedor, credenciais ou workspaces vazios
- **Dado** que o provedor não foi configurado previamente ou as credenciais não existem.
- **Quando** o usuário executa `neo git config set workspace`.
- **Então** o Neo encerra com código apropriado (`USAGE_ERROR` código `2` ou `AUTH_ERROR` código `3`) instruindo a configuração necessária.
- **Quando** a API do provedor responder com uma lista vazia de workspaces.
- **Então** o Neo encerra com código `4` (`NOT_FOUND`) informando que nenhum workspace foi encontrado para a conta.

## Matriz de decisão

| Provedor configurado | Credencial válida | Modo de invocação | Workspaces retornados | Escolha do usuário | Resultado esperado | Código | AC |
|---|---|---|---|---|---|---|---|
| Não | — | Qualquer | — | — | Erro de instrução de configuração | `2` | AC-4 |
| Sim | Não / Inválida | Qualquer | — | — | Erro de autenticação / `api-key` | `3` | AC-4 |
| Sim | Sim | Sem argumento | 0 | — | Painel/Erro "Nenhum workspace encontrado" | `4` | AC-4 |
| Sim | Sim | Sem argumento | >= 1 | Índice válido (1..N) | Workspace salvo em `[git]` + mensagem de sucesso | `0` | AC-1 |
| Sim | Sim | Sem argumento | >= 1 | Índice fora do intervalo | Erro de seleção inválida | `2` | AC-3 |
| Sim | Sim | Com argumento `<slug>` | >= 1 | Slug existente | Workspace salvo em `[git]` + mensagem de sucesso | `0` | AC-2 |
| Sim | Sim | Com argumento `<slug>` | >= 1 | Slug inexistente | Erro "Workspace não encontrado" | `4` | AC-2 |

## Casos de borda e erros
- Entrada não-numérica no prompt de seleção interativa → Typer trata o tipo inteiro e repete ou rejeita com erro sem quebrar com traceback.
- Falha de conexão ou rede com a API do provedor → capturado e emitido com mensagem amigável sem quebrar o terminal.

## Fora de escopo
- Criação de novos workspaces diretamente no provedor via CLI.
- Seleção de múltiplos workspaces simultâneos.

## Rastreabilidade
- ADRs relacionados:
  - `docs/architecture/adr/0002-tech-stack-core.md`
  - `docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md`
  - `docs/architecture/adr/0006-observabilidade-e-ux-cli.md`
