---
name: index
description: Página inicial da documentação do Neo (Personal Command Assistant).
alwaysApply: false
---

# <center>Neo — Personal Command Assistant</center>
<div class="hero-container">
  <img style="width: 140px" src="assets/neo-logo.jpg" alt="Neo CLI — Personal Command Assistant" class="hero-logo" />
</div>

<p align="center" class="hero-subtitle">
  <em>Assistente pessoal de linha de comando, alta produtividade, modular, seguro e pronto para automação</em>
</p>

<p align="center" class="hero-badges">
  <a href="https://github.com/thalisonwilker/neo/actions/workflows/ci.yml?query=branch%3Amain" target="_blank">
    <img src="https://github.com/thalisonwilker/neo/actions/workflows/ci.yml/badge.svg?event=push&branch=main" alt="CI & Deploy">
  </a>
  <a href="https://thalisonwilker.github.io/neo/" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://thalisonwilker.github.io/neo/coverage-badge.json" alt="Coverage">
  </a>
  <a href="https://github.com/thalisonwilker/neo" target="_blank">
    <img src="https://img.shields.io/badge/version-v0.1.0-34D058" alt="Version">
  </a>
  <a href="https://www.python.org/" target="_blank">
    <img src="https://img.shields.io/badge/python-3.13+-34D058" alt="Python 3.13+">
  </a>
  <a href="https://github.com/thalisonwilker/neo/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/badge/license-MIT-34D058" alt="License MIT">
  </a>
</p>

O **Neo** é um assistente pessoal de linha de comando de alta produtividade construído em **Python 3.13**, utilizando **Typer** e **Rich**. Ele centraliza e automatiza operações técnicas de trabalho — integrando-se nativamente com **GitHub**, **Bitbucket Cloud** e **Shortcut** — investigando informações com autonomia e fornecendo interfaces ricas no terminal.

---

## ⚡ Recursos Principais

=== "Multi-Provedor Git"
    Suporte unificado a **GitHub** e **Bitbucket**. Resolução transparente por flag explícita (`--provider / -p`), auto-detecção via remote do repositório local ou preferência configurada em `config.toml`.

=== "Segurança Nativa"
    Armazenamento seguro de credenciais via **Keyring do SO** (macOS Keychain, Linux Secret Service, Windows Credential Manager) com fallback inteligente para arquivo restrito (`0600`) e variáveis de ambiente.

=== "Terminal Moderno & Rico"
    Interfaces visuais modernas estilizadas com **Rich** (tabelas, alertas, painéis) e suporte à flag global `--json` para integração transparente com `jq`, pipelines de CI e scripts de automação.

=== "Análise de Contexto"
    Investigação contextual de tickets e chamados do Shortcut (`neo tasks analyze`), sugerindo branches, padrões de commit e critérios de aceite automaticamente.

---

## 🚀 Instalação Rápida

```bash
# Sincronizar o ambiente com uv
uv sync

# Executar a CLI localmente
uv run neo --help
```

---

## 🛠️ Exemplo de Uso

=== "Consultar Stories"
    ```bash
    # Listar apenas as stories atribuídas a você
    uv run neo tasks list --mine
    ```

=== "Navegar em Repositórios"
    ```bash
    # Listar repositórios do provedor ativo (GitHub ou Bitbucket)
    uv run neo git repo list
    ```

=== "Pesquisar Commits"
    ```bash
    # Busca commits auto-detectando o repositório git atual
    uv run neo git commits search --query "fix" --limit 5
    ```

=== "Alternar Workspace"
    ```bash
    # Selecionar workspace ativo interativamente
    uv run neo git workspace select
    ```

---

## 🧭 Metodologia Spec-Driven Development

O Neo é concebido sob rigoroso **Spec-Driven Development (SDD)**. Cada recurso, decisão arquitetural e modelo de dados é rastreável ponta a ponta desde as especificações de negócio até a suíte de testes automatizados com cobertura garantida $\ge 80\%$.
