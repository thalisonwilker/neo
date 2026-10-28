---
name: getting-started
description: Guia de instalação, pré-requisitos e primeiros passos com o Neo.
alwaysApply: false
---

# Primeiros Passos

Instale o Neo, conecte suas contas do GitHub, Bitbucket ou Shortcut e execute sua primeira consulta no terminal em menos de dois minutos.

---

## Pré-requisitos

- **Python >= 3.13**
- **Git** instalado e configurado no `PATH`
- Recomendado: gerenciador [`uv`](https://docs.astral.sh/uv/) para instalar ferramentas CLI em ambientes isolados:
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## 1. Instale o Neo

=== "Via PyPI (`uv` ou `pip`)"
    Instale o pacote **`neo-cmd`** para liberar o binário `neo` globalmente:
    ```bash
    # Recomendado: ambiente isolado gerenciado pelo uv
    uv tool install neo-cmd

    # Alternativa com pip
    pip install neo-cmd
    ```

=== "A partir do Código-Fonte"
    Clone o repositório e sincronize as dependências locais:
    ```bash
    git clone https://github.com/thalisonwilker/neo.git
    cd neo
    uv sync
    ```

Confirme que o binário está acessível:

```bash
neo --version
# Neo v0.1.1
```

---

## 2. Conecte seus Tokens

Seus tokens são salvos no **Keyring nativo do sistema operacional** (ou em `~/.config/neo/credentials.toml` com permissão `0600` quando o Keyring não estiver disponível).

 Dica: omita a flag `--token` se preferir digitar o segredo de forma oculta no terminal, sem deixar rastro no histórico do shell (`~/.zsh_history` ou `~/.bash_history`).

=== "GitHub"
    Gere um **Personal Access Token** (Classic com escopo `repo` ou Fine-grained):
    ```bash
    # Prompt oculto (recomendado)
    neo git config auth set github

    # Ou via flag direta
    neo git config auth set github --token "ghp_seu_token_aqui"
    ```

=== "Bitbucket Cloud"
    Use um **API Token** ou **App Password** no formato `usuario:token` (ou apenas o token Workspace):
    ```bash
    # Prompt oculto (recomendado)
    neo git config auth set bitbucket

    # Ou via flag direta
    neo git config auth set bitbucket --token "usuario:token"
    ```

=== "Shortcut"
    Gere um token em *Settings > API Tokens* no Shortcut:
    ```bash
    # Prompt oculto (recomendado)
    neo tasks config set

    # Ou via flag direta
    neo tasks config set --token "seu_token_shortcut"
    ```

---

## 3. Execute seu Primeiro Comando

Verifique o status geral das integrações e faça sua primeira consulta:

```bash
# Painel consolidado de credenciais e provedor Git ativo
neo config show

# Quadro Kanban da sua sprint atual no Shortcut
neo tasks resume

# Repositórios do seu workspace ativo no GitHub ou Bitbucket
neo git repo list
```

Precisa processar a saída em um script? Adicione `--json` antes do subcomando:

```bash
neo --json config show | jq .
```

---

## Próximos Passos

- [Configuração & Credenciais](configuration.md): entenda a precedência de tokens, variáveis de ambiente para CI e mapeamento de colunas do Kanban.
- [Guia de Comandos da CLI](cli/index.md): veja todos os subcomandos e filtros de `neo git` e `neo tasks`.
