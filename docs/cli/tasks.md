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
neo tasks list --service shortcut
```

---

## Comandos

### `neo tasks config`
Configura as credenciais e o mapeamento de colunas do board do serviço de tasks:

```bash
neo tasks config set [--token "seu_token"]   # prompt oculto se omitido
neo tasks config get                         # token mascarado
neo tasks config delete
neo tasks config columns                     # assistente interativo para mapear A fazer, Fazendo e Feito
neo tasks config columns --todo "📝 - Backlog de Sprint, 🚨 - Bug" --doing "🚧 - Em Progresso" --done "✅ - Finalizado"
```

---

### `neo tasks whoami`
Valida o token do Shortcut e exibe os dados do usuário autenticado:

```bash
neo tasks whoami
```

---

### `neo tasks iterations`
Lista todas as **iterações (sprints)** cadastradas no Shortcut ordenadas da mais recente para a mais antiga, marcando a última com `[● Atual]`:

```bash
neo tasks iterations
```

---

### `neo tasks resume`
Exibe um **quadro estilo Kanban** no terminal com 3 colunas lado a lado (**A fazer**, **Fazendo** e **Feito**).
Por padrão, filtra automaticamente pela **última iteração (atual)** do Shortcut e pelas tasks atribuídas ao usuário autenticado.

!!! info "Auto-configuração Inteligente por Serviço"
    Ao rodar `neo tasks resume`, o Neo verifica se o serviço atual (`shortcut`) já possui as colunas **A fazer**, **Fazendo** e **Feito** configuradas em `~/.config/neo/config.toml`.
    Caso ainda não estejam configuradas, ele busca todas as colunas reais do seu board na API (`GET /api/v3/workflows`), exibe a lista numerada e permite selecionar **1 ou mais colunas** (ex.: `1, 2`) para cada etapa antes de renderizar o quadro.

=== "Minhas Tasks na Iteração Atual (Padrão)"
    ```bash
    neo tasks resume
    ```

=== "Filtrar Outra Iteração (`-i`)"
    ```bash
    # Por nome completo, número da sprint ou ID (ou 'all' para todas)
    neo tasks resume --iteration "Sprint 70"
    neo tasks resume -i 70
    neo tasks resume -i all
    ```

=== "Todo o Board (`--all`)"
    ```bash
    neo tasks resume --all
    ```

=== "Reconfigurar Colunas (`--configure`)"
    ```bash
    neo tasks resume --configure
    ```

=== "Saída JSON (`--json`)"
    ```bash
    neo --json tasks resume
    ```

Exemplo de saída no terminal:

```text
                Quadro Resumo (Shortcut — Minhas Tasks — Sprint 71)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 📝 A fazer (2)                     ┃ 🚧 Fazendo (1)                     ┃ ✅ Feito (1)                       ┃
┃ 📝 - Backlog de Sprint, 🚨 - Bug   ┃ 🚧 - Em Progresso                  ┃ ✅ - Finalizado                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ #2157 ● Feature                    │ #2089 ● Feature                    │ #2163 ● Feature                    │
│ Adicionar o FCP ST no CSOSN 900    │ [New Desktop] Adições importantes  │ Emissao automatica de NFSe         │
│ 🔄 Sprint 71  🏷 fiscal             │ pós mvp                            │ (Interno)                          │
│                                    │ 🔄 Sprint 71  🏷 desktop            │ 🔄 Sprint 71  🏷 nfse               │
│ #1914 ● Bug                        │                                    │                                    │
│ Sistema não está baixando arquivos │                                    │                                    │
│ em aparelhos com iOS               │                                    │                                    │
│ 🔄 Sprint 71  🏷 mobile             │                                    │                                    │
└────────────────────────────────────┴────────────────────────────────────┴────────────────────────────────────┘
```

---

### `neo tasks list`
Lista stories ativas no espaço de trabalho (filtrando automaticamente pela **última iteração** por padrão):

=== "Iteração Atual (Padrão)"
    ```bash
    neo tasks list
    ```

=== "Apenas Minhas Stories (`--mine`)"
    ```bash
    neo tasks list --mine
    ```

=== "Filtrar Iteração Específica (`--iteration / -i`)"
    ```bash
    neo tasks list --iteration "Sprint 70"
    neo tasks list -i 70
    neo tasks list -i all
    ```

---

### `neo tasks search <query>`
Pesquisa stories por título ou palavras-chave:

```bash
neo tasks search "login"
```

---

### `neo tasks show <id>`
Exibe a visualização detalhada do ticket com descrição formatada, labels e link direto no navegador:

```bash
neo tasks show 1234
```

---

### `neo tasks analyze <id>`
Realiza uma **análise contextual completa** da demanda:
- Extrai critérios de aceite implícitos ou explícitos.
- Identifica alertas de risco, impedimentos ou bloqueios.
- Sugere o nome ideal da branch Git (ex: `feature/sc-1234-descricao`).
- Sugere a mensagem padronizada para o commit.

```bash
neo tasks analyze 1234
```
