---
name: cli-tasks-show
description: Manual do comando neo tasks show para visualização completa de uma história do Shortcut.
alwaysApply: false
---

# neo tasks show
> Exibe detalhes completos de uma story pelo ID numérico no Shortcut.

O comando `neo tasks show` busca todas as informações de um card: título, descrição em markdown formatada no terminal, status de workflow, tipo (`feature`, `bug`, `chore`), estimativa de pontos, proprietários atribuídos, labels e URL web direta.

---

## Sintaxe

```bash
neo tasks show <story_id> [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Exibe todos os campos e metadados da história especificada | `neo tasks show 12345` |

---

## Opções

As opções abaixo são específicas de `neo tasks show`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Atalho | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--service` | `-s` | Não | `shortcut` | Provedor de tarefas (`shortcut`). |

---

## Exemplos

### 1. Inspecionando uma história no terminal
```bash
neo tasks show 2157
```

### 2. Exportando os dados completos do card em JSON
```bash
neo --json tasks show 2157 | jq '{id, name, estimate, labels: [.labels[].name]}'
```

---

## Erros comuns e códigos de saída

* **Código 2 (Uso incorreto):** Omitir o ID da história ou fornecer um valor não numérico.
* **Código 1 (Erro genérico):** Story não encontrada (`404`) ou token sem permissão de acesso.

---

## Veja também
- [neo tasks analyze](analyze.md) — Analisar a story e extrair sugestões de branch e commits
- [neo tasks list](list.md) — Listar histórias da sprint
- [neo tasks search](search.md) — Localizar o ID de uma história por palavra-chave

