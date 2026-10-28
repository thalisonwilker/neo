---
name: cli-tasks
description: Manual do comando neo tasks para consulta e análise contextual de chamados no Shortcut.
alwaysApply: false
---

# `neo tasks`

O comando `tasks` reúne os serviços de gestão de tarefas. Hoje integra-se à **REST API v3 do Shortcut** para visualização, pesquisa e análise inteligente de tickets de desenvolvimento.

## Seletor de Serviço

Todos os subcomandos aceitam `--service` / `-s` (padrão: `shortcut`, único serviço suportado atualmente). Um serviço inválido encerra com código 1 listando os suportados.

```bash
uv run neo tasks list --service shortcut
```

---

## Comandos

### `neo tasks config`
Configura as credenciais do serviço de tasks:

```bash
uv run neo tasks config set [--token "seu_token"]   # prompt oculto se omitido
uv run neo tasks config get                         # token mascarado
uv run neo tasks config delete
```

---

### `neo tasks whoami`
Valida o token do Shortcut e exibe os dados do usuário autenticado:

```bash
uv run neo tasks whoami
```

---

### `neo tasks list`
Lista stories ativas no espaço de trabalho:

=== "Todas as Stories Ativas"
    ```bash
    uv run neo tasks list
    ```

=== "Apenas Minhas Stories"
    ```bash
    uv run neo tasks list --mine
    ```

---

### `neo tasks search <query>`
Pesquisa stories por título ou palavras-chave:

```bash
uv run neo tasks search "login"
```

---

### `neo tasks show <id>`
Exibe a visualização detalhada do ticket com descrição formatada, labels e link direto no navegador:

```bash
uv run neo tasks show 1234
```

---

### `neo tasks analyze <id>`
Realiza uma **análise contextual completa** da demanda:
- Extrai critérios de aceite implícitos ou explícitos.
- Identifica alertas de risco, impedimentos ou bloqueios.
- Sugere o nome ideal da branch Git (ex: `feature/sc-1234-descricao`).
- Sugere a mensagem padronizada para o commit.

```bash
uv run neo tasks analyze 1234
```
