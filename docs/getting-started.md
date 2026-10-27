---
name: getting-started
description: Guia de instalação, pré-requisitos e primeiros passos com o Neo.
alwaysApply: false
---

# Primeiros Passos

Este guia orienta a instalação do Neo, configuração das ferramentas de desenvolvimento e execução do seu primeiro comando.

---

## Pré-requisitos

- **Python >= 3.13**
- Gerenciador de pacotes [`uv`](https://docs.astral.sh/uv/) instalado:
  ```bash
  # No macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Git** configurado.
- *(Opcional)* **Docker** e **Docker Compose** para execução conteinerizada dos serviços e documentação.

---

## Instalação do Projeto

Clone o repositório e sincronize o ambiente virtual:

```bash
git clone https://github.com/thalysonwilker/neo.git
cd neo
uv sync
```

Para verificar se tudo está funcionando corretamente:

```bash
uv run neo --version
```

A saída exibirá a versão atual do Neo (`v0.1.0`).

---

## Configuração Inicial de Tokens

Antes de interagir com o GitHub, Bitbucket ou Shortcut, configure suas chaves de API:

=== "GitHub"
    Crie um **Personal Access Token** (Classic com escopo `repo` ou Fine-grained):
    ```bash
    uv run neo config auth set github --token "ghp_seu_token_aqui"
    ```

=== "Bitbucket Cloud"
    Utilize um **API Token** ou App Password com permissões de repositórios:
    ```bash
    uv run neo config auth set bitbucket --token "usuario:token"
    ```

=== "Shortcut"
    Gere um token em *User Settings > API Tokens*:
    ```bash
    uv run neo config auth set shortcut --token "seu_token_shortcut"
    ```

Verifique o status das integrações:

```bash
uv run neo config show
```

---

## Próximos Passos

- Conheça a [Configuração de Provedores](configuration.md) para alternar entre GitHub e Bitbucket.
- Explore o [Guia de Comandos da CLI](cli/index.md).
