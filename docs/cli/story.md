---
name: cli-story
description: Manual do comando neo story para consulta e análise contextual de chamados no Shortcut.
alwaysApply: false
---

# `neo story`

O módulo `story` integra-se à **REST API v3 do Shortcut** para visualização, pesquisa e análise inteligente de tickets de desenvolvimento.

---

## Comandos

### `neo story whoami`
Valida o token do Shortcut e exibe os dados do usuário autenticado:

```bash
uv run neo story whoami
```

---

### `neo story list`
Lista stories ativas no espaço de trabalho:

=== "Todas as Stories Ativas"
    ```bash
    uv run neo story list
    ```

=== "Apenas Minhas Stories"
    ```bash
    uv run neo story list --mine
    ```

---

### `neo story search <query>`
Pesquisa stories por título ou palavras-chave:

```bash
uv run neo story search "login"
```

---

### `neo story show <id>`
Exibe a visualização detalhada do ticket com descrição formatada, labels e link direto no navegador:

```bash
uv run neo story show 1234
```

---

### `neo story analyze <id>`
Realiza uma **análise contextual completa** da demanda:
- Extrai critérios de aceite implícitos ou explícitos.
- Identifica alertas de risco, impedimentos ou bloqueios.
- Sugere o nome ideal da branch Git (ex: `feature/sc-1234-descricao`).
- Sugere a mensagem padronizada para o commit.

```bash
uv run neo story analyze 1234
```
