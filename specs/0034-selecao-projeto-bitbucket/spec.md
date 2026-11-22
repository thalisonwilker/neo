---
name: spec
description: Contrato da seleção de projeto Bitbucket por workspace e uso na criação de repositórios.
alwaysApply: true
---

# Spec — Seleção de projeto Bitbucket

> **Status:** implementado · Tier: pequeno.

## Resumo

Ao configurar um workspace Bitbucket, selecionar um projeto acessível e salvar seu identificador para criar repositórios nesse projeto. O GitHub mantém seu comportamento atual.

## Critérios de aceite

### AC-1: Seleção do projeto
- **Dado** o provedor Bitbucket e um workspace válido selecionado interativamente ou informado como argumento, **quando** o Neo busca os projetos acessíveis desse workspace, **então** apresenta todos os projetos em lista numerada com nome e identificador e pede ao usuário que selecione um.
- **E** após seleção válida persiste juntos o workspace e o identificador do projeto selecionado, vinculando o projeto ao workspace; informa sucesso somente após salvar ambos.

### AC-2: Falhas e preservação
- **Dado** a configuração anterior, **quando** a busca de projetos falha, retorna lista vazia ou a seleção é inválida ou cancelada, **então** o comando informa o problema e preserva o workspace e o projeto anteriores.
- **E** a configuração nunca associa silenciosamente um projeto do workspace anterior ao novo workspace.

### AC-3: Exibição de configuração
- **Dado** o comando `neo git config show`, **quando** o provedor configurado é Bitbucket, **então** a saída humana e a saída JSON, nos modos local e global, exibem o projeto configurado ou indicam sua ausência.
- **E** quando o provedor é GitHub, as saídas humana e JSON não exibem o campo de projeto e preservam o contrato existente.

### AC-4: Criação no projeto selecionado
- **Dado** o provedor Bitbucket, um workspace efetivo e um projeto configurado para esse workspace, **quando** executar `neo git repo create`, **então** a requisição de criação usa o identificador do projeto selecionado.
- **E** se o projeto estiver ausente ou pertencer a outro workspace, o comando falha antes de criar o remoto e orienta executar `neo git config set workspace`.
- **E** nenhum projeto é fixado no código para todos os usuários ou workspaces.

### AC-5: GitHub e modo JSON
- **Dado** o GitHub como provedor, **quando** o usuário configura o workspace ou cria um repositório, **então** mantém o comportamento existente sem consulta ou seleção de projeto Bitbucket.
- **Dado** o Bitbucket e modo JSON, **quando** executar `neo git config set workspace`, **então** retorna erro orientando usar modo interativo e preserva a configuração.

## Matriz de decisão

| Provedor | Operação | Estado | Resultado | AC |
|---|---|---|---|---|
| Bitbucket | Configurar workspace, modo interativo | Projeto selecionado | Salva workspace e projeto juntos | AC-1 |
| Bitbucket | Configurar workspace, modo interativo | Lista vazia, falha ou cancelamento | Erro; configuração anterior preservada | AC-2 |
| Bitbucket | Configurar workspace, JSON | Qualquer | Erro orientando modo interativo; preserva configuração | AC-5 |
| Bitbucket | Mostrar configuração | Projeto presente ou ausente | Exibe projeto ou ausência | AC-3 |
| Bitbucket | Criar repositório | Projeto associado ao workspace efetivo | Cria no projeto selecionado | AC-4 |
| Bitbucket | Criar repositório | Projeto ausente ou de outro workspace | Erro antes da criação remota | AC-4 |
| GitHub | Configurar workspace, mostrar configuração ou criar repositório | Qualquer | Sem seleção ou exibição de projeto Bitbucket; comportamento atual mantido | AC-3, AC-5 |

## Casos de borda e erros

- A listagem inclui todas as páginas retornadas pelo Bitbucket; erros de autenticação, permissão e rede não expõem credenciais.
- Cancelamento e seleção numérica inválida não alteram o estado anterior.
- O identificador enviado ao Bitbucket é o UUID do projeto retornado pela API, usando o formato aceito pela API de criação de repositórios.
- O workspace efetivo segue a precedência de configuração existente; um projeto vinculado a outro workspace não é reutilizado.

## Fora de escopo

- Criar ou modificar projetos no Bitbucket.
- Selecionar projeto para GitHub ou alterar o comportamento de outros comandos Git.

## Rastreabilidade

- A exibição JSON de projeto Bitbucket substitui a preservação correspondente do contrato JSON de [0032](../0032-apresentacao-configuracoes-git/spec.md).
- Complementa [0030 — Configurar workspace](../0030-refactor-git-config-set-workspace/spec.md) e [0033 — Criar repositório](../0033-refactor-git-repo-create/spec.md).
