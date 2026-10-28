---
name: spec
description: Contrato e critérios de aceite da pipeline de CI/CD e deploy no GitHub Actions.
alwaysApply: true
---

# Spec — 0008 CI/CD e Deploy com GitHub Actions

> **Fonte da verdade.** Status: aprovado
> Contrato de entrega para a automação de Quality Gates e Deploy do portal de documentação no GitHub Pages.

## Resumo
Configura a esteira automatizada de CI/CD via **GitHub Actions** para o Neo, garantindo a execução de Quality Gates completos (auditoria SDD, lint, checagem estática de tipos, testes e trava de cobertura $\ge 80\%$) em Pull Requests e pushes, seguido pelo deploy automático do portal MkDocs Material no **GitHub Pages** (v4) na branch `main`.

## Critérios de Aceite

### AC-1: Quality Gates na Pipeline de Integração Contínua (CI)
- **Dado** uma abertura de Pull Request ou push na branch `main`,
- **Quando** o workflow de CI for acionado pelo GitHub Actions,
- **Então** os seguintes estágios devem ser executados em ordem com bloqueio em caso de falha:
  1. **Auditoria SDD & Fidelidade de Specs:** execução de `node scripts/audit-esteira.mjs` e `node scripts/eval-spec-fidelity.mjs`.
  2. **Lint & Formatação:** execução de `uv run ruff check .` e `uv run ruff format --check .`.
  3. **Verificação Estática de Tipagem:** execução de `uv run mypy src`.
  4. **Testes Automatizados & Trava de Cobertura:** execução de `uv run pytest --cov=neo --cov-fail-under=80` garantindo no mínimo 80% de cobertura.

### AC-2: Deploy Automatizado da Documentação no GitHub Pages
- **Dado** um push na branch `main` com os Quality Gates aprovados com sucesso,
- **Quando** o estágio de deploy for disparado,
- **Então** o workflow deve:
  1. Configurar permissões de segurança estritas (`contents: read`, `pages: write`, `id-token: write`).
  2. Instalar as dependências do grupo `docs` com `uv sync --group docs`.
  3. Compilar o portal de documentação em modo estrito via `uv run --group docs mkdocs build --strict`.
  4. Gerar e subir o artefato com `actions/upload-pages-artifact@v3` a partir do diretório `site/`.
  5. Efetuar a publicação no GitHub Pages utilizando `actions/deploy-pages@v4`.

### AC-3: Configuração do `site_url` no `mkdocs.yml`
- **Dado** o arquivo `mkdocs.yml`,
- **Quando** inspecionado o campo `site_url`,
- **Então** deve estar apontando para a URL canônica do GitHub Pages do projeto (`https://thalisonwilker.github.io/neo/`).

### AC-4: Validação Sintática e de Integridade dos Workflows
- **Dado** os arquivos YAML em `.github/workflows/`,
- **Quando** analisados via analisador de YAML e suíte de testes automatizados,
- **Então** não devem conter erros de sintaxe, devem declarar versões atualizadas das GitHub Actions e definir dependências explícitas (`needs: [test]`).

### AC-5: Documentação de CI/CD e Guia de Ativação do GitHub Pages
- **Dado** a documentação do projeto (`README.md` e `docs/architecture.md`),
- **Quando** o desenvolvedor consultar as instruções de deploy,
- **Então** deve encontrar o passo a passo para ativar o GitHub Pages em *Settings > Pages > Source: GitHub Actions*, bem como a descrição dos jobs da esteira.

## Casos de Borda e Erros
- Pushes em branches que não sejam `main` executam os testes e quality gates, mas **não** disparam o deploy no GitHub Pages.
- Falhas em lint, tipo ou testes abortam a pipeline imediatamente antes de tentar compilar a documentação.

## Fora de Escopo
- Publicação de pacote binário no PyPI (será abordado quando houver release formal v1.0).
- Suporte a múltiplos ambientes de deploy (staging/pre-prod).

## Rastreabilidade
- Tasks: `./tasks.md`
- Quality Gates do Projeto: `docs/engineering/TESTING.md`
