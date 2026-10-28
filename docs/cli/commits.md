---
name: cli-commits
description: Manual do comando neo git commits para histórico e busca de commits.
alwaysApply: false
---

# `neo git commits`

Investiga o histórico de commits direto na API do **GitHub** ou do **Bitbucket Cloud**, útil para rastrear quando uma alteração entrou ou cruzar commits com IDs de tarefas.

---

## Detecção Automática pelo Repositório Local

Se você rodar `neo git commits search` dentro de uma pasta com Git inicializado, o Neo lê a URL do remote `origin` e descobre sozinho:

- o provedor (`github` ou `bitbucket`),
- o workspace/organização,
- o slug do repositório.

Fora de um repositório Git (ou para consultar outro projeto), basta informar `--repo` e, se necessário, `--provider` e `--workspace`.

---

## Comandos

### `neo git commits search`
Lista e filtra commits por termo na mensagem, autor e limite de resultados:

=== "No Repositório Atual"
    ```bash
    # Detecta provedor, workspace e repo via git remote origin
    neo git commits search
    ```

=== "Por Mensagem ou ID de Card (`--query`)"
    ```bash
    # Encontra commits que mencionam um ticket específico
    neo git commits search --query "sc-2108" --limit 10
    ```

=== "Por Autor (`--author`)"
    ```bash
    neo git commits search --author "Thalyson"
    ```

=== "Em Outro Repositório (`--repo`)"
    ```bash
    neo git commits search --provider github --repo neo --limit 5
    ```

=== "Em JSON para Auditoria (`--json`)"
    ```bash
    neo --json git commits search --query "fix" --limit 5 | jq '.[] | {hash, author, message}'
    ```
