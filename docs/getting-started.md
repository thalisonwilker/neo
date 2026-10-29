---
name: getting-started
description: Guia de instalação, pré-requisitos e primeiros passos com o Neo.
alwaysApply: false
---

# Primeiros Passos

Instale o Neo em ambiente isolado, autentique sua conta no GitHub ou Bitbucket Cloud e configure seu provedor e workspace padrão.

---

## Pré-requisitos

- **Python >= 3.13**
- **Git** instalado e acessível no `PATH`
- Gerenciador de ferramentas CLI [`uv`](https://docs.astral.sh/uv/) ou [`pipx`](https://pipx.pypa.io/):
  ```bash
  # Instalar uv no macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## 1. Instale o Neo

```bash
# Opção 1: com uv (recomendado)
uv tool install neo-cmd

# Opção 2: com pipx
pipx install neo-cmd
```

!!! warning "Erro `externally-managed-environment` (PEP 668)"
    Distribuições Linux recentes e o Python instalado via Homebrew no macOS bloqueiam `pip install` direto no Python do sistema (erro `error: externally-managed-environment`). Use sempre **`uv tool install neo-cmd`** ou **`pipx install neo-cmd`**: ambos criam um ambiente virtual isolado automaticamente e expõem o binário `neo` no seu `PATH`.

Se estiver contribuindo com o código-fonte do projeto:

```bash
git clone https://github.com/thalisonwilker/neo.git
cd neo
uv sync
uv run neo --version
```

Confirme a instalação:

```bash
neo --version
# Neo v0.2.0
```

---

## 2. Autentique seu Provedor Git

O comando `neo git auth login` solicita o segredo com entrada oculta no terminal e o armazena no **Keyring do sistema operacional** (ou em `~/.config/neo/credentials.toml` com permissão `0600`). O Neo nunca aceita tokens como argumento de linha de comando.

=== "GitHub"
    Gere um **Personal Access Token** (Classic com escopo `repo` ou Fine-grained) e execute:
    ```bash
    neo git auth login --provider github
    ```

=== "Bitbucket Cloud"
    Gere um **API Token** na sua conta Atlassian e execute:
    ```bash
    neo git auth login --provider bitbucket
    ```
    O terminal solicitará o e-mail da sua conta Atlassian e, em seguida, o API Token com digitação oculta.

    !!! warning "App Passwords descontinuadas no Bitbucket Cloud"
        O Bitbucket Cloud descontinuou as antigas *App Passwords*. Crie e utilize um **API Token** vinculado ao e-mail da sua conta Atlassian.

=== "Shortcut (Módulo Tasks)"
    Para usar o módulo `neo tasks`, salve o token gerado em *Settings > API Tokens*:
    ```bash
    neo tasks config set
    ```

---

## 3. Defina o Provedor e o Workspace Padrão

Configure qual provedor e qual workspace (organização/conta no GitHub ou Workspace no Bitbucket) o Neo deve usar quando você não estiver dentro de um repositório Git local:

```bash
# Definir o provedor Git padrão (github ou bitbucket)
neo git config set provider github

# Definir o workspace padrão
neo git config set workspace minha-organizacao

# Conferir as configurações ativas
neo git config list
```

---

## 4. Verifique o Contexto e Faça sua Primeira Consulta

```bash
# Verificar autenticação nos provedores Git
neo git auth status

# Inspecionar o contexto Git completo (repositório local, provedor e workspace)
neo git status

# Listar os repositórios do workspace configurado
neo git repo list --limit 10

# Exportar em JSON para usar com jq
neo git repo list --limit 5 --json | jq '.[] | {name, slug, main_branch}'
```

---

## Próximos Passos

- [Configuração & Credenciais](configuration.md): veja todas as chaves da seção `[git]` e `[agent]`, a ordem de precedência e as variáveis de ambiente para CI/CD.
- [Agente & SDD (`neo agent`)](cli/agent/index.md): configure o Google Antigravity CLI (`agy`), selecione modelos e prepare os provedores `spec-driven` e `spec-kit`.
- [Visão Geral da CLI](cli/index.md): consulte a gramática, os verbos padronizados e a tabela de códigos de saída.
- [Guia de Migração](migration.md): tabela de equivalência se você utilizava a versão `v0.1.0`/`v0.1.1`.
