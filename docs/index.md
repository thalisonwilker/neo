---
name: index
description: Página inicial da documentação do Neo — assistente pessoal via linha de comando para organizar a vida de um dev.
alwaysApply: false
---

# <center>Trabalho, estudos, lazer e finanças. Sua vida organizada, a um comando de distância.</center>
<div class="hero-container">
  <img style="width: 240px" src="assets/neo-logo.jpg" alt="Neo CLI — Assistente pessoal via linha de comando" class="hero-logo" />
</div>

<p align="center" class="hero-subtitle">
  <em>Um assistente pessoal para quem prefere o terminal à interface gráfica. Comece hoje pelo fluxo de desenvolvimento e escale suas automações em uma linha.</em>
</p>

<p align="center" class="hero-badges">
  <a href="https://github.com/thalisonwilker/neo/actions/workflows/ci.yml?query=branch%3Amain" target="_blank">
    <img src="https://github.com/thalisonwilker/neo/actions/workflows/ci.yml/badge.svg?event=push&branch=main" alt="CI & Deploy">
  </a>
  <a href="https://thalisonwilker.github.io/neo/" target="_blank">
    <img src="https://img.shields.io/endpoint?url=https://thalisonwilker.github.io/neo/coverage-badge.json" alt="Coverage">
  </a>
  <a href="https://pypi.org/project/neo-cmd/" target="_blank">
    <img src="https://img.shields.io/badge/version-v0.2.0-34D058" alt="Version">
  </a>
  <a href="https://www.python.org/" target="_blank">
    <img src="https://img.shields.io/badge/python-3.13+-34D058" alt="Python 3.13+">
  </a>
  <a href="https://github.com/thalisonwilker/neo/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/badge/license-MIT-34D058" alt="License MIT">
  </a>
</p>

O **Neo** é um assistente pessoal de linha de comando feito por dev, para devs que resolvem tudo pelo teclado. Sem alternar abas no navegador, você consulta tarefas do Shortcut, investiga repositórios e commits no GitHub e Bitbucket Cloud, e orquestra agentes de IA no terminal.

- **Disponível hoje:** integração unificada com **GitHub**, **Bitbucket Cloud** e **Shortcut** (`neo git` e `neo tasks`), orquestração do Google Antigravity CLI e esteiras SDD (`neo agent`), saída estruturada via `--json` e credenciais protegidas no Keyring nativo do sistema operacional.
- **No roadmap:** módulos para organizar estudos, finanças e acompanhamento de branches e PRs.

---

## Por que usar o Neo

=== "Linha de Comando Unificada"
    Troque cliques por comandos previsíveis no padrão `neo <módulo> <recurso> <ação>`. O Neo detecta o repositório Git local automaticamente e responde no terminal com tabelas e painéis formatados via **Rich**.

=== "GitHub, Bitbucket e Shortcut em um Lugar"
    Use a mesma gramática para listar, buscar e inspecionar repositórios e commits no **GitHub** ou no **Bitbucket Cloud** (`--provider` ou detecção automática pelo `remote origin`) e acompanhe suas histórias do **Shortcut** sem sair do código.

=== "Pronto para Scripts e CI (`--json`)"
    Todo comando de leitura aceita `--json`. Combine o Neo com `jq`, scripts shell e pipelines de CI/CD usando códigos de saída semânticos (`0` a `5`).

=== "Credenciais Seguras no Keyring"
    `neo git auth login` solicita tokens com entrada oculta e salva no **Keyring nativo do SO** (macOS Keychain, Linux Secret Service, Windows Credential Manager), com fallback para variáveis de ambiente em CI.

---

## Instalação Rápida

=== "Via uv (Recomendado)"
    ```bash
    # Instale globalmente em ambiente isolado
    uv tool install neo-cmd

    # Confirme a instalação
    neo --help
    ```

=== "Via pipx"
    ```bash
    pipx install neo-cmd
    neo --version
    ```

=== "Desenvolvimento Local"
    ```bash
    git clone https://github.com/thalisonwilker/neo.git
    cd neo
    uv sync
    uv run neo --help
    ```

---

## Fluxo Inicial em 4 Passos

Configure seu ambiente e consulte suas demandas em menos de 1 minuto:

=== "GitHub"
    ```bash
    # 1. Autentique seu provedor Git com segurança
    neo git auth login --provider github

    # 2. Selecione a organização ou conta ativa
    neo git workspace select

    # 3. Liste os repositórios disponíveis
    neo git repo list --limit 5

    # 4. Veja suas tarefas na sprint atual no quadro Kanban
    neo tasks resume
    ```

=== "Bitbucket Cloud"
    ```bash
    # 1. Autentique com e-mail e API Token da Atlassian
    neo git auth login --provider bitbucket

    # 2. Selecione o workspace de trabalho
    neo git workspace select

    # 3. Liste os repositórios do workspace
    neo git repo list --limit 5

    # 4. Veja suas tarefas na sprint atual no quadro Kanban
    neo tasks resume
    ```

---

## Cheat Sheet (Os 10 Comandos Mais Usados)

| Comando | O que faz | Módulo |
|---|---|---|
| `neo tasks resume` | Abre o quadro Kanban no terminal com suas tarefas da sprint atual | `tasks` |
| `neo tasks analyze <id>` | Analisa a story e sugere nome de branch, commits e critérios de aceite | `tasks` |
| `neo git status` | Inspeciona branch, remote, workspace ativo e status de autenticação | `git` |
| `neo git repo list` | Lista repositórios remotos do workspace ativo | `git` |
| `neo git repo search --query "<termo>"` | Busca repositórios remotos por nome ou descrição | `git` |
| `neo git commits search --query "<termo>"` | Pesquisa histórico de commits por mensagem | `git` |
| `neo git workspace select` | Menu interativo para alternar organização ou workspace | `git` |
| `neo git auth status` | Confere o estado de autenticação dos provedores Git | `git` |
| `neo config show` | Visão agregada de todas as preferências e credenciais do Neo | `config` |
| `neo agent run` | Inicia sessão interativa com o agente de IA (Antigravity CLI) | `agent` |

---

## Construído com Spec-Driven Development

O Neo é desenvolvido em **Python 3.13** e **Typer** seguindo **Spec-Driven Development (SDD)**. Cada funcionalidade é guiada por especificações vivas com critérios de aceite determinísticos e cobertura de testes automatizados `>= 80%`.
