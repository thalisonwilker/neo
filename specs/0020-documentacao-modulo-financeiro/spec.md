---
name: spec
description: Contrato e critérios de aceite para a atualização da documentação institucional e guias com o módulo financeiro (neo fin).
alwaysApply: true
---

# Spec — 0020 Atualização da Documentação com o Módulo Financeiro (`neo fin`)

> **Fonte da verdade.** Status: aprovado
> Contrato de entrega para integrar o módulo financeiro pessoal (`neo fin`) em todos os pontos de entrada da documentação do Neo (README raiz, página inicial do MkDocs, primeiros passos, matriz de comandos da CLI e novo guia prático de fluxo financeiro).

## Resumo
Apresenta o módulo financeiro pessoal `neo fin` em todos os canais de documentação institucional do Neo, atualizando o `README.md`, `docs/index.md`, `docs/getting-started.md`, a matriz geral em `docs/cli/index.md` e criando um novo guia prático em `docs/guias/gestao-financeira.md`.

---

## Critérios de Aceite

### AC-1: Destaque na Home do MkDocs e no README Raiz
- **Dado** o `README.md` raiz e a home da documentação (`docs/index.md`),
- **Quando** a seção de módulos e recursos disponíveis for lida,
- **Então** o módulo `neo fin` deve constar expressamente como funcionalidade disponível (promovido de "no roadmap" para "disponível hoje"), com breve explicação de persistência local SQLite e exemplos dos comandos.

### AC-2: Inclusão no Guia de Primeiros Passos
- **Dado** o documento `docs/getting-started.md`,
- **Quando** o usuário seguir o fluxo de introdução ao sistema,
- **Então** deve haver um passo orientando como iniciar o gerenciamento financeiro pessoal (`neo fin bank create`, registro rápido com `neo fin expense` e consulta de balanço).

### AC-3: Atualização da Matriz Recurso × Ação
- **Dado** o documento conceitual `docs/cli/index.md`,
- **Quando** a tabela "Matriz Recurso × Ação" for consultada,
- **Então** devem existir linhas dedicadas para `neo fin` com seus recursos (`bank`, `category`, `tx`, `summary`, `balance`), indicando com precisão os verbos suportados (`create`, `get`, `list`, `update`, `delete` e atalhos).

### AC-4: Guia Prático de Gestão Financeira
- **Dado** a seção de "Guias Práticos" da documentação,
- **Quando** o arquivo `docs/guias/gestao-financeira.md` for acessado,
- **Então** apresenta um passo a passo do fluxo financeiro de um desenvolvedor (configurar contas, registrar despesas e receitas em menos de 2 segundos pelo terminal, acompanhar extrato e fechar o mês com o resumo consolidado), indexado no `mkdocs.yml` e em `docs/guias/index.md`.

### AC-5: Conformidade Estrutural e Paridade de Testes
- **Dado** a suíte de testes de documentação,
- **Quando** `uv run pytest tests/unit/test_docs_parity.py -v && uv run --group docs mkdocs build --strict` for executado,
- **Então** todos os links, páginas e comandos devem ser validados sem warnings ou erros de integridade.

---

## Casos de Borda e Erros
- Links quebrados para os novos guias: prevenidos pela compilação com flag `--strict`.
- Páginas não registradas no nav do `mkdocs.yml`: prevenidas por validação cruzada no teste de paridade.

## Fora de Escopo
- Alterações no código-fonte Python da CLI ou nos esquemas do banco SQLite (já consolidados na feature 0019).

## Rastreabilidade
- Tasks: `./tasks.md`
