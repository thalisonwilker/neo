---
name: spec
description: Reorganização granular da documentação em páginas dedicadas por ação e navegação padronizada com menu suspenso/chevron em todos os níveis.
alwaysApply: true
---

# Spec — 0027 Granularidade da Documentação e Menus Suspensos

> **Fonte da verdade.** Status: implementado · Tier: pequeno

## Resumo

Estabelece como padrão arquitetural da documentação o comportamento de menus suspensos/expansíveis com chevron (`>`) em todos os níveis de agrupamento, e reorganiza a documentação da CLI de forma granular, substituindo arquivos únicos agregadores por pastas com páginas `.md` detalhadas e dedicadas para cada subcomando/ação da CLI (`neo git repo`, `neo git branch`, `neo git commits`, `neo git pr`, etc.), preservando redirecionamentos legados e retrocompatibilidade de testes.

## Critérios de Aceite

### AC-1: Padrão Global de Menus Suspensos com Chevron
- **Dado** o portal de documentação MkDocs compilado,
- **Quando** o usuário navega por qualquer nível da árvore lateral (`Configuração`, `Referência da CLI`, `Guias Práticos`, etc.),
- **Então** todo item que possuir subitens deve exibir o ícone de chevron (`>`), ser interativo ao clique (expandir/recolher) com rotação suave do chevron para baixo (`v`), e permanecer aberto caso uma página filha esteja ativa.

### AC-2: Granularidade por Ação no Módulo `neo git repo`
- **Dado** a referência de comandos de repositórios em `neo git repo`,
- **Quando** consultada a pasta `docs/cli/git/repo/`,
- **Então** deve existir um arquivo dedicado para cada ação:
  - `docs/cli/git/repo/index.md` (visão geral e índice de ações)
  - `docs/cli/git/repo/list.md` (`neo git repo list`)
  - `docs/cli/git/repo/remote-list.md` (`neo git repo remote-list`)
  - `docs/cli/git/repo/search.md` (`neo git repo search`)
  - `docs/cli/git/repo/show.md` (`neo git repo show`)
  - `docs/cli/git/repo/create.md` (`neo git repo create`)
  - `docs/cli/git/repo/edit.md` (`neo git repo edit`)
- **E** cada página deve seguir o molde oficial detalhado: Sintaxe, Descrição, Opções com links, Exemplos (humano e `--json | jq`), Erros comuns/códigos de saída e Veja também.

### AC-3: Granularidade por Ação nos Demais Recursos Git (`branch`, `commits`, `pr`)
- **Dado** os comandos `branch`, `commits` e `pr` do `neo git`,
- **Quando** consultadas as respectivas pastas em `docs/cli/git/`,
- **Então** cada recurso deve possuir pasta própria com `index.md` e páginas individuais por ação:
  - `branch/`: `index.md`, `list.md`, `create.md`, `delete.md`
  - `commits/`: `index.md`, `list.md`, `search.md`, `show.md`
  - `pr/`: `index.md`, `open.md`, `list.md`, `show.md`, `approve.md`, `decline.md`

### AC-4: Árvore no `mkdocs.yml` com Menus Suspensos Granulares
- **Dado** o arquivo `mkdocs.yml`,
- **Quando** inspecionada a seção `nav`,
- **Então** os grupos `repo`, `branch`, `commits` e `pr` devem ser menus suspensos com seus subcomandos expostos individualmente como subitens expansíveis.

### AC-5: Redirecionamentos e Compatibilidade de Links
- **Dado** links internos antigos e URLs anteriores (`cli/git/repo.md`, `cli/git/branch.md`, `cli/git/commits.md`, `cli/git/pr.md`),
- **Quando** o site for compilado em modo estrito (`mkdocs build --strict`),
- **Então** nenhum link quebrado deve ocorrer, e o plugin `redirects` deve direcionar os caminhos antigos para os novos índices correspondentes.

### AC-6: Preservação de Testes e Gates
- **Dado** o conjunto de testes automatizados (`tests/unit/test_docs_build.py` e `tests/unit/test_docs_parity.py`),
- **Quando** executado `uv run pytest tests/unit -v`,
- **Então** todos os testes devem passar sem regressões, atualizando as asserções de paridade e estrutura para contemplar as novas páginas geradas.

## Casos de Borda e Erros
- URLs legadas e referências cruzadas em guias práticos e `cli/comandos.md` devem ser atualizadas para os novos caminhos para evitar 404.
- Páginas-índice (`index.md`) de cada grupo devem funcionar tanto com clique direto quanto mantendo o chevron expansível para os subitens.

## Fora de Escopo
- Alterações no código-fonte Python da CLI (`src/neo/`).
- Criação de novos comandos ou modificação na gramática da CLI.

## Rastreabilidade
- Tasks: `./tasks.md`
- Specs anteriores: `specs/0016-menus-e-submenus-documentacao/`, `specs/0026-navegacao-arvore-cli/`

