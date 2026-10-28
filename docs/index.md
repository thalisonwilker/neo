---
name: index
description: Página inicial da documentação do Neo (Um assistente pessoal via linha de comando para organizar a vida de um dev).
alwaysApply: false
---

# <center>Trabalho, estudos, lazer e finanças. Sua vida organizada, a um comando de distância.</center>
<div class="hero-container">
  <img style="width: 240px" src="assets/neo-logo.jpg" alt="Neo CLI — Um assistente pessoal via linha de comando para organizar a vida de um dev" class="hero-logo" />
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

O **Neo** é um assistente pessoal de linha de comando feito por dev, para devs que resolvem tudo pelo teclado. Sem abrir abas no navegador, você consulta tarefas, investiga commits e gerencia repositórios direto do terminal.

- **Disponível hoje:** integração unificada com **GitHub**, **Bitbucket Cloud** e **Shortcut** (`neo git` e `neo tasks`), saída estruturada via `--json` e credenciais protegidas no Keyring do sistema operacional.
- **No roadmap:** módulos para organizar estudos, hobbies, lazer, finanças pessoais (receitas e despesas) e uma API para conectar qualquer ferramenta ao seu fluxo.

---

## Por que usar o Neo

=== "Linha de Comando por Escolha"
    Troque cliques e trocas de aba por comandos previsíveis no padrão `neo git <recurso> <ação>`. O Neo detecta o repositório Git atual automaticamente e responde no terminal com tabelas formatadas via **Rich**.

=== "GitHub, Bitbucket e Shortcut em um Lugar"
    Use a mesma gramática para listar, buscar e inspecionar repositórios e commits no **GitHub** ou no **Bitbucket Cloud** (`--provider` ou detecção automática pelo `remote`) e acompanhe suas demandas do **Shortcut** sem sair do código.

=== "Pronto para Scripts e CI (`--json`)"
    Todo comando de leitura aceita `--json`. Combine o Neo com `jq`, scripts shell e pipelines de CI/CD usando códigos de saída semânticos (`0` a `5`).

=== "Credenciais Fora de Texto Puro"
    `neo git auth login` solicita o token com entrada oculta e salva no **Keyring nativo do SO** (macOS Keychain, Linux Secret Service, Windows Credential Manager), com fallback para `~/.config/neo/credentials.toml` (`0600`) ou variáveis de ambiente em CI.

---

## Instalação Rápida

=== "Via uv ou pipx (Recomendado)"
    ```bash
    # Instale globalmente em ambiente isolado
    uv tool install neo-cmd
    # ou: pipx install neo-cmd

    # Confirme a instalação
    neo --help
    ```

=== "Desenvolvimento Local"
    ```bash
    uv sync
    uv run neo --help
    ```

---

## Veja na Prática

=== "Diagnóstico do Contexto Git"
    ```bash
    # Veja branch atual, provedor ativo, workspace resolvido e status de autenticação
    neo git status
    ```

=== "Busca de Commits e Repositórios"
    ```bash
    # Liste repositórios do workspace ativo (GitHub ou Bitbucket Cloud)
    neo git repo list

    # Busque os últimos 5 commits com "fix" na mensagem no repositório atual
    neo git commits search --query "fix" --limit 5
    ```

=== "Quadro Kanban no Terminal"
    ```bash
    # Veja suas tarefas em A fazer | Fazendo | Feito na sprint atual
    neo tasks resume
    ```

=== "Contexto para Começar a Codar"
    ```bash
    # Analise uma story do Shortcut e receba sugestões de branch, commits e critérios de aceite
    neo tasks analyze 12345
    ```

=== "Automação com `--json` e `jq`"
    ```bash
    # Extraia os slugs e URLs SSH dos seus repositórios direto para um script
    neo git repo list --json | jq '.[] | {slug, ssh: .clone_links[0].href}'
    ```

=== "Alternar Workspace"
    ```bash
    # Selecione o workspace ou organização ativa pelo teclado
    neo git workspace select
    ```

---

## Construído com Spec-Driven Development

O Neo é desenvolvido em **Python 3.13** e **Typer** seguindo **Spec-Driven Development (SDD)**. Nenhuma funcionalidade vai para o código sem uma especificação aprovada, critérios de aceite determinísticos e cobertura de testes automatizados `>= 80%`.
