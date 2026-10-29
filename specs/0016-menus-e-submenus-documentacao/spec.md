---
name: spec
description: Contrato e critérios de aceite para reorganização da documentação do Neo em menus e submenus hierárquicos.
alwaysApply: true
---

# Spec — 0016 Menus e Submenus na Documentação do Neo

> **Fonte da verdade.** Status: aprovado
> Contrato de entrega para reorganizar a árvore de navegação e as páginas da documentação MkDocs Material em menus e submenus estruturados por objetivos funcionais.

## Resumo
Reestrutura o menu lateral e as páginas de documentação da CLI Neo no MkDocs Material, substituindo a listagem plana por uma hierarquia em menus e submenus agrupados por objetivo de uso (`Git`, `Tasks`, `Agente`, `Guias`), com páginas padronizadas no molde oficial, suporte a `navigation.indexes` e redirecionamentos para preservar URLs antigas.

## Critérios de Aceite

### AC-1: Hierarquia de Navegação com Menus e Submenus por Objetivo
- **Dado** o arquivo `mkdocs.yml`,
- **Quando** a seção `nav` for inspecionada,
- **Então** a documentação de comandos deve estar organizada sob "Referência da CLI" com submenus para:
  - **Conceitos Gerais** (`cli/index.md`)
  - **Git**:
    - **Contexto e Acesso**: `Autenticação` (`cli/git/auth.md`), `Configuração` (`cli/git/config.md`), `Status do Contexto` (`cli/git/status.md`), `Workspaces` (`cli/git/workspace.md`)
    - **Recursos**: `Repositórios` (`cli/git/repo.md`), `Commits` (`cli/git/commits.md`)
    - **Planejado**: `Recursos Futuros (🚧)` (`cli/git/planejado.md`)
  - **Tasks**:
    - **Visão do Dia**: `Quadro Kanban (resume)` (`cli/tasks/resume.md`), `Membro Autenticado (whoami)` (`cli/tasks/whoami.md`), `Sprints e Iterações` (`cli/tasks/iterations.md`)
    - **Consulta**: `Listar Stories (list)` (`cli/tasks/list.md`), `Pesquisar Stories (search)` (`cli/tasks/search.md`), `Detalhes da Story (show)` (`cli/tasks/show.md`)
    - **Análise**: `Análise de Contexto (analyze)` (`cli/tasks/analyze.md`)
    - **Configuração**: `Configurar Shortcut` (`cli/tasks/config.md`)
  - **Agente & SDD**:
    - `Configuração do Agente` (`cli/agent/config.md`), `Diagnóstico (status)` (`cli/agent/status.md`), `Preparação SDD (setup)` (`cli/agent/setup.md`), `Execução Interativa (run)` (`cli/agent/run.md`)
  - **Guias (por objetivo)**:
    - `Uso em CI com --json` (`guias/ci-json.md`), `Trocar de Provedor (GitHub ↔ Bitbucket)` (`guias/trocar-provedor.md`), `Fluxo Diário: Tasks → Branch → Commit` (`guias/fluxo-diario.md`)

### AC-2: Ativação de `navigation.indexes` e Páginas-Índice de Módulo
- **Dado** o tema `material` em `mkdocs.yml`,
- **Quando** `features` for consultado,
- **Então** deve incluir `navigation.indexes`, permitindo que cada pasta raiz (`cli/git/index.md`, `cli/tasks/index.md`, `cli/agent/index.md`, `guias/index.md`) funcione como página-índice do seu respectivo grupo ao clicar no cabeçalho do menu.

### AC-3: Padronização Obrigatória das Páginas de Comando
- **Dado** qualquer página de documentação em `cli/git/`, `cli/tasks/` ou `cli/agent/`,
- **Quando** o arquivo markdown for renderizado,
- **Então** ele deve seguir estritamente o molde:
  ```markdown
  # neo <módulo> <recurso>
  > Uma linha explicando para que serve.

  ## Sintaxe
  ## Ações (tabela: ação | descrição | exemplo)
  ## Opções (específicas com link para globais)
  ## Exemplos (saída humana + variante --json | jq)
  ## Erros comuns e códigos de saída
  ## Veja também
  ```

### AC-4: Seção "Qual comando usar?" e Matriz Recurso × Ação
- **Dado** o documento `docs/cli/index.md`,
- **Quando** renderizado,
- **Então** deve conter:
  1. A matriz completa recurso × ação abrangendo os módulos `git`, `tasks` e `agent` (com marcadores ✅ disponível, 🚧 planejado, ➖ não se aplica).
  2. Tabela de verbos separada claramente em **Disponíveis** e **Planejados (🚧)**.
  3. A seção **"Qual comando usar?"** esclarecendo a diferença entre os 3 comandos `status` (`neo git status`, `neo git auth status`, `neo agent status`) e as opções de configuração (`neo config show`, `neo git config`, `neo config agent`, `neo tasks config`).
  4. Separação explícita entre opções globais (`--json`, `--help`, etc.) e opções de recurso (`--workspace`, `--repo`, `--query`, `--limit`, `--provider`, `--yes`).

### AC-5: Remoção de Atalhos Inexistentes e Cheat Sheet na Home
- **Dado** o documento `docs/index.md`,
- **Quando** inspecionado,
- **Então** não deve conter nenhuma referência ao atalho `-p` para `--provider` em `neo git`, deve exibir um fluxo completo de 4 a 5 comandos (`auth login` → `workspace select` → `repo list` → `tasks resume`) e uma tabela Cheat Sheet com os 10 comandos mais usados.

### AC-6: Redirecionamento de URLs Legadas via Plugin `redirects`
- **Dado** acessos a URLs anteriores (`cli/auth.md`, `cli/config.md`, `cli/status.md`, `cli/workspace.md`, `cli/repo.md`, `cli/commits.md`, `cli/tasks.md`, `cli/agent.md`),
- **Quando** o site for compilado com o plugin `redirects` ativado no `mkdocs.yml`,
- **Então** redirects automáticos (HTTP 301 / meta refresh) devem conduzir o usuário para os novos caminhos em submenus sem gerar erros 404.

### AC-7: Compilação Estrita do MkDocs sem Erros (`--strict`)
- **Dado** o conjunto completo de documentação atualizado,
- **Quando** executado `uv run mkdocs build --strict`,
- **Então** a compilação deve finalizar com código `0`, sem nenhum aviso de link quebrado, página órfã fora do `nav` ou erro de formatação.

## Casos de Borda e Erros
- Links relativos cruzados entre guias e comandos devem apontar para os caminhos corretos.
- Comandos não implementados não devem constar como disponíveis em nenhuma página.

## Fora de Escopo
- Modificação de código-fonte de implementação da CLI (`src/neo/`).
- Criação de novos comandos em tempo de execução.

## Rastreabilidade
- Tasks: `./tasks.md`
- Contexto de documentação: `docs/architecture.md`, `mkdocs.yml`

