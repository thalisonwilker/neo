---
name: cli-commits
description: Manual do comando neo git commits para histórico e busca de commits.
alwaysApply: false
---

# `neo git commits`

O módulo `commits` investiga o histórico de versões nos repositórios remotos.

---

## Auto-Detecção Inteligente

Quando executado dentro de uma pasta de projeto Git local, o Neo inspeciona automaticamente a URL do remote `origin` para determinar o provedor (**GitHub** ou **Bitbucket**), o workspace/organização e o slug do repositório, dispensando o preenchimento manual das flags.

---

## Comandos

### `neo git commits search`
Pesquisa commits com filtros opcionais de autor, termo de mensagem e quantidade máxima:

=== "No Diretório Atual"
    ```bash
    # Detecta automaticamente o repositório atual
    neo git commits search
    ```

=== "Filtrando por Autor"
    ```bash
    neo git commits search --author "Thalyson"
    ```

=== "Filtrando por Palavra-chave ou Ticket"
    ```bash
    neo git commits search --query "sc-2108" --limit 10
    ```

=== "Em Repositório Específico"
    ```bash
    neo git commits search --provider github --repo neo --limit 5
    ```
