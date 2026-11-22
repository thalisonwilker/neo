---
name: spec
description: Contrato da apresentação das configurações Git no comando neo git config show.
alwaysApply: true
---

# Spec — Apresentação das configurações Git

> **Status:** implementado. Tier: pequeno.

## Resumo

Apresentar as configurações de `neo git config show` em um componente visual separado, legível e focado no estado atual de Git.

## Critérios de aceite

### AC-1: Componente e campos
- **Dado** qualquer configuração Git;
- **Quando** `neo git config show` for executado sem JSON;
- **Então** um componente de apresentação separado exibe o título `Git` e somente os campos abaixo, nesta ordem: `provider`, `workspace`, `branch`, `branch-pattern`, `commit-format`, `api-key`, `repo`, `task`;
- **E** cada campo é exibido como rótulo e valor, sem a coluna de origem;
- **E** `branch` apresenta o valor efetivo de `default-branch`, não a branch ativa;
- **E** `branch-pattern` e `commit-format` apresentam os valores efetivos, inclusive os padrões quando não houver valor configurado.

### AC-2: Estado dos campos
- **Dado** os valores efetivos e o contexto selecionado;
- **Quando** a apresentação humana for renderizada;
- **Então** aplica os textos e cores da matriz abaixo aos valores indicados;
- **E** o nome do repositório é o último componente do caminho selecionado, sem exibir o caminho completo;
- **E** a task configurada aparece com um único `#` antes do ID.

### AC-3: Credenciais e JSON
- **Dado** uma credencial presente ou ausente e os modos JSON local e global;
- **Quando** o usuário executar `neo git config show`, `neo git config show --json` ou `neo --json git config show`;
- **Então** nenhum segredo é exibido;
- **E** ambos os modos JSON preservam a estrutura, os valores e as origens da saída JSON existente, independentemente da apresentação humana.

## Matriz de decisão

| Campo | Estado | Valor exibido | Cor do valor | AC |
|---|---|---|---|---|
| provider | Configurado | `github (Configurado)` ou `bitbucket (Configurado)` | verde | AC-2 |
| provider | Ausente | `Não configurado` | branco | AC-2 |
| workspace | Configurado | nome do workspace | verde | AC-2 |
| workspace | Ausente | `Não configurado` | branco | AC-2 |
| api-key | Configurada para o provider | `Configurado` | verde | AC-2, AC-3 |
| api-key | Ausente ou sem provider | `Não configurado` | branco | AC-2, AC-3 |
| repo | Selecionado | nome do repositório | verde | AC-2 |
| repo | Ausente | `Não configurado` | branco | AC-2 |
| task | Definida | `#ID` | verde | AC-2 |
| task | Ausente | `Sem task definida` | branco | AC-2 |

## Casos de borda e erros

- Sem repositório selecionado, `repo` e `task` são apresentados como ausentes, sem falha do comando.
- Valores de configuração são tratados como texto, inclusive caracteres de marcação Rich.
- Em terminal sem suporte a cores, os textos permanecem legíveis sem depender de cores para indicar ausência.

## Fora de escopo

- Alterar persistência, precedência de configurações, credenciais ou comportamento dos comandos `set`, `get` e `unset`.
- Alterar `neo config show` ou as configurações de outros módulos.
- Alterar o contrato JSON existente ou restabelecer `neo git config list`.

## Rastreabilidade

- Contrato anterior de modularização: [feature 0031](../0031-modularizacao-comandos-provedores/spec.md).
- A saída humana de `neo git config show` desta feature substitui a preservação de saída correspondente em AC-2 da feature 0031.
