---
name: index
description: Página inicial da documentação do Neo (Personal Command Assistant).
alwaysApply: false
---

# Neo — Personal Command Assistant

> **Compreenda seus sistemas. Seja dono das suas escolhas.**

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
    Investigação contextual de tickets e chamados do Shortcut (`neo story analyze`), sugerindo branches, padrões de commit e critérios de aceite automaticamente.

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
    uv run neo story list --mine
    ```

=== "Navegar em Repositórios"
    ```bash
    # Listar repositórios do provedor ativo (GitHub ou Bitbucket)
    uv run neo repo list
    ```

=== "Pesquisar Commits"
    ```bash
    # Busca commits auto-detectando o repositório git atual
    uv run neo commits search --query "fix" --limit 5
    ```

=== "Alternar Workspace"
    ```bash
    # Selecionar workspace ativo interativamente
    uv run neo workspace select
    ```

---

## 🧭 Metodologia Spec-Driven Development

O Neo é concebido sob rigoroso **Spec-Driven Development (SDD)**. Cada recurso, decisão arquitetural e modelo de dados é rastreável ponta a ponta desde as especificações de negócio até a suíte de testes automatizados com cobertura garantida $\ge 80\%$.
