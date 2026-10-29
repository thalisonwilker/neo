---
name: cli-tasks-resume
description: Manual do comando neo tasks resume para visualização de quadro Kanban no terminal.
alwaysApply: false
---

# neo tasks resume
> Renderiza o quadro Kanban no terminal com colunas A fazer, Fazendo e Feito.

O comando `neo tasks resume` exibe um quadro ágil completo diretamente no terminal. Por padrão, apresenta apenas as stories atribuídas ao usuário logado na **iteração (sprint) atual**, organizadas lado a lado em três colunas formatadas via **Rich**.

---

## Sintaxe

```bash
neo tasks resume [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Exibe o quadro Kanban das suas tarefas na sprint atual | `neo tasks resume` |
| `all` | Exibe o quadro com tarefas de todo o time | `neo tasks resume --all` |
| `configure` | Abre o assistente interativo de configuração de colunas | `neo tasks resume --configure` |

---

## Opções

As opções abaixo são específicas de `neo tasks resume`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Atalho | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--all` | `-a` | Não | `False` | Exibe tarefas de todos os membros (padrão: apenas as suas). |
| `--iteration` | `-i` | Não | *(atual)* | Nome, número, ID da sprint ou `'all'` para todas. |
| `--configure` | `-c` | Não | `False` | Abre a reconfiguração interativa das colunas do workflow. |
| `--limit` | `-l` | Não | `10` | Quantidade máxima de tasks exibidas por coluna. |
| `--service` | `-s` | Não | `shortcut` | Provedor de tarefas (`shortcut`). |

---

## Exemplos

### 1. Visualização diária padrão (Minhas tasks na sprint atual)
```bash
neo tasks resume
```

Exemplo de visualização:
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

### 2. Visualização de outra sprint com atalhos curtos
```bash
neo tasks resume -i "Sprint 70" -a
```

### 3. Extraindo contagem de tarefas com `--json` e `jq`
```bash
neo --json tasks resume | jq '{todo: (.todo | length), doing: (.doing | length), done: (.done | length)}'
```

---

## Erros comuns e códigos de saída

* **Código 1 (Erro genérico):** Token do Shortcut não configurado ou colunas do workflow não mapeadas. Execute `neo tasks config set` para autenticar ou use `--configure` para definir as colunas.
* **Código 2 (Uso incorreto):** Valor de sprint inválido ou não localizado.

---

## Veja também
- [neo tasks list](list.md) — Exibir stories em formato de tabela simples
- [neo tasks analyze](analyze.md) — Analisar uma história antes de codar
- [neo tasks config](config.md) — Configurar credenciais e colunas do Shortcut

