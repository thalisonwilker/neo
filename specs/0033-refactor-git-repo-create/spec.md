---
name: spec
description: Contrato da criação remota e clonagem de repositórios Git.
alwaysApply: true
---

# Spec — Criação e clonagem de repositório Git

> **Status:** implementado · Tier: pequeno.

## Resumo

Substituir o fluxo de `neo git repo create` pela criação do repositório remoto, clonagem, preparação dos arquivos e publicação do commit inicial.

## Critérios de aceite

### AC-1: Validação e criação remota
- **Dado** nome válido, provedor e credenciais configurados e destino disponível, **quando** executar `neo git repo create <nome>`, **então** valida a conexão com o provedor antes de criar o repositório remoto e cria o remoto antes de clonar.
- **E** o remoto é privado por padrão; `--public` cria um remoto público.
- **E** `--description <texto>` define a descrição do repositório remoto.

### AC-2: Destino do clone
- **Dado** um repositório remoto criado, **quando** o Neo o clona, **então** usa um subdiretório com o nome do repositório dentro do diretório pai selecionado conforme a matriz.
- **E** não sobrescreve um destino existente.

### AC-3: Arquivos, branch e commit
- **Dado** o clone do repositório remoto vazio, **quando** o Neo o prepara, **então** cria a branch principal conforme a matriz, um `README.md` com o nome e, se informada, a descrição, e um `AGENTS.md` vazio.
- **E** adiciona os dois arquivos e cria o commit com mensagem exata `first commit`.

### AC-4: Publicação e conclusão
- **Dado** o commit inicial criado, **quando** o Neo executa o push da branch ao remoto, **então** a branch é a principal do repositório remoto.
- **E** somente após o push bem-sucedido o comando registra e seleciona o repositório no contexto do Neo, informa a conclusão e exibe um comando `cd` que permite acessar o clone.
- **E** o processo não tenta alterar o diretório do terminal do usuário.

### AC-5: Falhas e segurança
- **Dado** uma falha de validação, criação remota, clone, preparação, commit ou push, **quando** a etapa falha, **então** o comando retorna erro, identifica a etapa e não informa conclusão.
- **E** preserva os recursos já criados, informa se o remoto foi criado e o caminho local quando aplicável, sem expor credenciais.
- **E** nome inválido, diretório pai inexistente ou destino já existente são rejeitados antes de criar o remoto.

## Matriz de decisão

| Opção | Estado | Resultado | AC |
|---|---|---|---|
| `--path` | ausente | diretório pai é o diretório atual | AC-2 |
| `--path` | informado | diretório pai é o caminho informado | AC-2 |
| `--default-branch` | ausente | branch principal `main` | AC-3, AC-4 |
| `--default-branch` | informado | branch principal tem o nome informado | AC-3, AC-4 |
| `--description` | ausente | README contém o nome; remoto sem descrição informada | AC-1, AC-3 |
| `--description` | informado | README contém nome e descrição; remoto recebe a descrição | AC-1, AC-3 |
| `--public` | ausente | remoto privado | AC-1 |
| `--public` | informado | remoto público | AC-1 |

## Casos de borda e erros

- Um caminho pai que não seja diretório, uma branch inválida ou credenciais indisponíveis causam erro sem sobrescrever arquivos existentes.
- Falhas após a criação do remoto não removem automaticamente o remoto nem o clone parcial.
- A saída humana e JSON não expõe segredos; caminhos com espaços devem resultar em instrução `cd` utilizável.

## Fora de escopo

- Implementar o comando independente `neo git repo clone`.
- Alterar o diretório do shell que executou o Neo.
- Excluir automaticamente recursos criados em caso de falha.

## Rastreabilidade

- Este contrato substitui o AC-4 de [0023 — Atualização dos comandos Git](../0023-atualizacao-comandos-git/spec.md).
