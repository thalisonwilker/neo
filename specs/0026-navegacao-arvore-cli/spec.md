---
name: spec
description: Navegação da documentação CLI organizada pela árvore real de comandos do Neo.
alwaysApply: true
---

# Spec — Navegação pela árvore da CLI

> **Fonte da verdade.** Status: implementado · Tier: pequeno

## Resumo

Organizar a referência MkDocs por módulos e recursos da CLI, preservando os caminhos das páginas e seus redirecionamentos. Este contrato substitui a organização por objetivos do AC-1 da spec 0016; os demais critérios continuam aplicáveis.

## Critérios de aceite

### AC-1: Navegação por comandos
- **Dado** o menu Referência da CLI, **quando** o usuário navega pela documentação, **então** encontra os grupos `config`, `git`, `tasks`, `agent` e `fin`, com entradas identificadas pelos nomes de comandos ou recursos disponíveis.
- **E** `git config` agrupa suas páginas de configuração, credenciais e workspace, sem apresentar `auth` ou `workspace` como comandos independentes.
- **E** o menu Git inclui `status`, `repo`, `branch`, `commits` e `pr`; o menu Tasks apresenta seus comandos e os grupos `check`, `comment` e `config`.

### AC-2: Links existentes e legibilidade
- **Dado** os caminhos e redirecionamentos de documentação existentes, **quando** o site é compilado, **então** permanecem válidos e o build estrito passa.
- **E** a navegação permite expandir os grupos conforme necessário, sem expandir todos automaticamente; recursos planejados permanecem identificados.

### AC-3: Árvore de comandos
- **Dado** a referência da CLI, **quando** o usuário acessa a árvore de comandos, **então** encontra os módulos, grupos e ações disponíveis em listas aninhadas, com links para a documentação dos respectivos recursos.
- **E** a árvore distingue a listagem padrão de `neo git pr` dos subcomandos e não apresenta recursos planejados como disponíveis.

## Fora de escopo
- Alterar o comportamento ou criar comandos da CLI.

## Rastreabilidade
- [Tasks](tasks.md) · [Navegação anterior](../0016-menus-e-submenus-documentacao/spec.md)
