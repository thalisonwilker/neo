---
name: spec
description: Contrato da feature 0013 — higienização da estrutura do repositório, configuração do pacote `neo-cmd` para o PyPI, README enxuto e workflow de publicação no GitHub Actions.
alwaysApply: true
---

# Spec — Pacote PyPI (`neo-cmd`), Limpeza de Estrutura e Publicação via GitHub Actions

> **Fonte da verdade.** Status: implementado
> Tier: **Pequeno** (`spec.md` + `tasks.md` — empacotamento, documentação raiz e automação de release no CI/CD).

## Resumo
Higieniza a estrutura de diretórios do repositório removendo pastas de editores e exemplos desnecessários, enxuga o `README.md` mantendo apenas o essencial (apontando para a documentação completa no GitHub Pages), configura o `pyproject.toml` como pacote PyPI **`neo-cmd`** (mantendo o executável `neo` e o pacote `src/neo`) e adiciona o workflow de publicação no PyPI via GitHub Actions.

---

## Critérios de aceite

### AC-1: Limpeza de pastas e arquivos desnecessários do repositório
- **Dado** o repositório com artefatos de múltiplos editores e exemplos de template;
- **Quando** a limpeza estrutural for aplicada;
- **Então** os diretórios/arquivos `.cursor/`, `.windsurf/`, `.spec-driven/`, `.github/prompts/`, `.github/copilot-instructions.md`, `specs/0001-exemplo-cota-de-uso/`, `src/README.md`, `site/` e `.coverage` não existem mais na árvore do projeto;
- **E** a auditoria SDD (`node scripts/audit-esteira.mjs .`) passa sem nenhum link quebrado.

### AC-2: Configuração do pacote `neo-cmd` em `pyproject.toml`
- **Dado** o arquivo `pyproject.toml`;
- **Quando** configurado para distribuição no PyPI;
- **Então** declara `name = "neo-cmd"`, `license = "MIT"`, `keywords`, `classifiers`, `[project.urls]` (`Homepage`, `Documentation`, `Repository`, `Issues`), `[project.scripts] neo = "neo.cli:app"` e `[tool.uv.build-backend] module-name = "neo"`;
- **E** `uv build` gera os arquivos `neo_cmd-<version>.tar.gz` e `neo_cmd-<version>-py3-none-any.whl` sem erros.

### AC-3: `README.md` resumido e objetivo
- **Dado** que a documentação detalhada já é publicada no GitHub Pages (`https://thalisonwilker.github.io/neo/`);
- **Quando** o `README.md` da raiz for atualizado;
- **Então** apresenta apenas o essencial: logo, subtítulo, badges (estilo FastAPI), breve descrição, instruções de instalação (`uv tool install neo-cmd` / `pip install neo-cmd` e desenvolvimento local com `uv sync`), resumo rápido dos módulos (`neo git`, `neo tasks`, `neo config`) com link para a documentação completa e seção de licença MIT.

### AC-4: Workflow de publicação no PyPI via GitHub Actions (`.github/workflows/publish.yml`)
- **Dado** o arquivo `.github/workflows/publish.yml`;
- **Quando** uma release é publicada, uma tag `v*` (ex.: `v0.1.0`) é enviada por push ou o workflow é acionado manualmente (`workflow_dispatch`);
- **Então** o workflow valida os testes/lint, executa `uv build` para construir `sdist` e `wheel` e publica no PyPI utilizando **Trusted Publishing (OIDC)** (`permissions: id-token: write`, ambiente `pypi`, `pypa/gh-action-pypi-publish@release/v1`).

---

## Casos de borda e erros
- **Diferença entre nome do pacote (`neo-cmd`) e módulo importável (`neo`):** sem `module-name = "neo"` em `[tool.uv.build-backend]`, o `uv_build` procuraria `src/neo_cmd/`. Configurar explicitamente `module-name = "neo"` garante que `src/neo/` continue funcionando sem renomear nenhum import.
- **Links de documentação no PyPI:** imagens e links no `README.md` devem funcionar tanto no GitHub quanto na página do pacote no PyPI.

## Fora de escopo
- Alteração de lógica de negócio nos módulos `git` ou `tasks`.
- Publicação automática a cada commit na `main` (a publicação ocorre apenas em tags `v*` / Releases ou disparo manual).

## Rastreabilidade
- Tech Stack & Empacotamento: [ADR-0002](../../docs/architecture/adr/0002-tech-stack-core.md)
- CI/CD: [0008-ci-cd-e-deploy-github-actions](../0008-ci-cd-e-deploy-github-actions/spec.md)
