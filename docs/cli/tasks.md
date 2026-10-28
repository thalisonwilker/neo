---
name: cli-tasks
description: Manual do comando neo tasks para consulta e análise contextual de chamados no Shortcut.
alwaysApply: false
---

# `neo tasks`

Gerencia suas tarefas e sprints sem sair do terminal. Hoje conecta-se à **REST API v3 do Shortcut** (selecionável via `--service / -s`, padrão `shortcut`).

---

## Comandos

### `neo tasks resume`
Renderiza o seu **quadro Kanban no terminal** com três colunas lado a lado: **A fazer**, **Fazendo** e **Feito**. Por padrão, mostra apenas as stories atribuídas a você na **iteração (sprint) atual**.

=== "Minhas Tasks na Sprint Atual (Padrão)"
    ```bash
    neo tasks resume
    ```

=== "Outra Iteração (`-i / --iteration`)"
    ```bash
    # Aceita nome da sprint, número, ID ou 'all' para ignorar filtro de sprint
    neo tasks resume --iteration "Sprint 70"
    neo tasks resume -i 70
    neo tasks resume -i all
    ```

=== "Board Completo do Time (`--all`)"
    ```bash
    # Inclui tasks de todos os membros na iteração selecionada
    neo tasks resume --all
    ```

=== "Reconfigurar Colunas (`--configure`)"
    ```bash
    # Reabre o seletor interativo de colunas do workflow
    neo tasks resume --configure
    ```

=== "Exportar Quadro em JSON (`--json`)"
    ```bash
    neo --json tasks resume | jq '{todo: (.todo | length), doing: (.doing | length), done: (.done | length)}'
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

!!! info "Configuração de colunas no primeiro uso"
    Se as colunas **A fazer**, **Fazendo** e **Feito** ainda não estiverem salvas em `~/.config/neo/config.toml`, `neo tasks resume` busca os estados do seu workflow na API do Shortcut e pergunta quais colunas mapear antes de exibir o quadro.

---

### `neo tasks analyze <id>`
Lê os detalhes de uma story e entrega o contexto pronto para você começar a codar:

- extrai critérios de aceite explícitos ou implícitos na descrição,
- destaca alertas de risco, dependências ou bloqueios,
- sugere o nome padronizado da branch Git (ex.: `feature/sc-1234-descricao`),
- sugere a mensagem de commit inicial.

```bash
neo tasks analyze 1234

# Em JSON para integrar com hooks ou scripts de criação de branch
neo --json tasks analyze 1234 | jq -r '.suggested_branch'
```

---

### `neo tasks list`
Lista stories em tabela (por padrão, filtra pela **iteração atual**):

=== "Minhas Stories na Sprint Atual"
    ```bash
    neo tasks list --mine
    ```

=== "Todas as Stories da Sprint Atual"
    ```bash
    neo tasks list
    ```

=== "Filtrar por Sprint (`-i / --iteration`)"
    ```bash
    neo tasks list --iteration "Sprint 70"
    neo tasks list -i 70 --mine
    neo tasks list -i all --mine
    ```

---

### `neo tasks show <id>`
Exibe descrição completa, estado, tipo (`feature`, `bug`, `chore`), proprietários, labels e URL direta do card:

```bash
neo tasks show 1234
```

---

### `neo tasks search <query>`
Busca stories no Shortcut por título ou termo na descrição:

```bash
neo tasks search "login"
```

---

### `neo tasks iterations`
Lista todas as sprints cadastradas da mais recente para a mais antiga e marca a ativa com `[● Atual]`:

```bash
neo tasks iterations
```

---

### `neo tasks whoami`
Valida o token configurado e mostra o nome e login do membro autenticado no Shortcut:

```bash
neo tasks whoami
```

---

### `neo tasks config`
Gerencia o token de autenticação e o mapeamento de colunas do workflow:

```bash
neo tasks config set                         # solicita token em prompt oculto
neo tasks config set --token "seu_token"     # salva token via flag
neo tasks config get                         # exibe token mascarado
neo tasks config delete                      # remove token salvo
neo tasks config columns                     # assistente interativo de colunas
neo tasks config columns \
  --todo "📝 - Backlog de Sprint, 🚨 - Bug" \
  --doing "🚧 - Em Progresso" \
  --done "✅ - Finalizado"
```
