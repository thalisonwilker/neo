---
name: spec
description: Contrato e critérios de aceite da documentação MkDocs conteinerizada inspirada no HTTPX.
alwaysApply: true
---

# Spec — 0007 Documentação MkDocs Conteinerizada

> **Fonte da verdade.** Status: aprovado
> Contrato de entrega para o sistema de documentação conteinerizado com MkDocs e tema Material for MkDocs.

## Resumo
Configura e disponibiliza a documentação técnica do Neo utilizando **MkDocs Material** com design, paleta claro/escuro, navegação rica e componentes visuais inspirados no portal do **HTTPX** (`https://www.python-httpx.org/`), empacotada em contêiner Docker com live-reload via Docker Compose e suporte nativo a execução local via `uv`.

## Critérios de Aceite

### AC-1: Configuração do MkDocs com Tema Material e Recursos Visuais Estilo HTTPX
- **Dado** o repositório do Neo,
- **Quando** o arquivo `mkdocs.yml` é inspecionado,
- **Então** deve estar configurado com `theme: name: material`, paleta claro/escuro (`default` com primary indigo / accent indigo e `slate` com primary indigo / accent indigo) com ícone de alternância automática/manual, navegação em abas superiores (`navigation.tabs`), seções expansíveis (`navigation.sections`, `navigation.expand`), botão de rolagem ao topo (`navigation.top`), busca integrada com realces (`search.highlight`, `search.suggest`) e suporte às extensões PyMdown (`highlight`, `inlinehilite`, `superfences`, `admonition`, `tabbed`, `details`).

### AC-2: Estrutura Completa e Navegação Amigável das Páginas
- **Dado** o diretório de documentação,
- **Quando** o MkDocs é compilado,
- **Então** o índice de navegação deve apresentar de forma clara e organizada as seguintes seções:
  1. **Visão Geral** (`index.md`): introdução, filosofia e destaques do Neo.
  2. **Primeiros Passos** (`getting-started.md`): instalação, pré-requisitos e primeiro comando.
  3. **Configuração** (`configuration.md`): gerenciamento de credenciais e provedores.
  4. **Guia de Comandos** (`cli/`): manuais dedicados com tabs de exemplos para `workspace.md`, `repo.md`, `commits.md` e `story.md`.
  5. **Arquitetura & SDD** (`architecture.md`): explicação da esteira Spec-Driven Development e links vivos.

### AC-3: Dockerfile Otimizado para Documentação
- **Dado** o arquivo `Dockerfile.docs` no repositório,
- **Quando** o contêiner for construído com Docker,
- **Então** a imagem deve instalar `mkdocs-material` e extensões necessárias de forma enxuta, expor a porta `8000` e configurar o entrypoint padrão para `mkdocs serve --dev-addr 0.0.0.0:8000`.

### AC-4: Orquestração Conteinerizada com Docker Compose
- **Dado** o arquivo `docker-compose.docs.yml`,
- **Quando** o desenvolvedor executar `docker compose -f docker-compose.docs.yml up`,
- **Então** o serviço `docs` deve ser iniciado na porta `8000`, mapeando os volumes de `docs/` e `mkdocs.yml` para garantir **live-reload instantâneo** durante a edição de arquivos Markdown.

### AC-5: Suporte a Execução Local sem Docker via `uv`
- **Dado** o arquivo `pyproject.toml`,
- **Quando** inspecionado o grupo de dependências `[dependency-groups.docs]`,
- **Então** deve incluir `mkdocs-material>=9.6.0` e `pymdown-extensions>=10.14.0`, permitindo executar `uv run --group docs mkdocs serve` no ambiente de desenvolvimento.

### AC-6: Validação de Build Estrito sem Links Quebrados
- **Dado** a documentação e os arquivos markdown configurados,
- **Quando** for executado `uv run --group docs mkdocs build --strict`,
- **Então** o build estático em `site/` deve concluir com sucesso (código de retorno 0) sem advertências de links quebrados ou erros de formatação.

## Casos de Borda e Erros
- Edições de arquivos Markdown refletem automaticamente via websocket live-reload do MkDocs tanto no contêiner quanto no host local.
- Links internos devem ser relativos entre arquivos `.md` para permitir navegação nativa no GitHub e compilação do MkDocs.

## Fora de Escopo
- Deploy automatizado em produção (GitHub Pages ou Netlify) — será tratado em feature de CI/CD subsequente.
- Internacionalização multi-idioma das páginas (i18n).

## Rastreabilidade
- Tasks: `./tasks.md`
- Referência visual: [HTTPX Documentation](https://www.python-httpx.org/)
