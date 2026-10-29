---
name: cli-tasks-list
description: Manual do comando neo tasks list para listagem de stories em tabela.
alwaysApply: false
---

# neo tasks list
> Lista stories ativas no workspace do Shortcut em formato tabular.

O comando `neo tasks list` exibe as histórias do Shortcut cadastradas na iteração alvo (por padrão, a **última sprint ativa**), com opções para restringir o retorno exclusivamente às stories atribuídas a você.

---

## Sintaxe

```bash
neo tasks list [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Lista as stories da sprint atual em formato de tabela | `neo tasks list` |
| `mine` | Filtra apenas stories atribuídas ao seu usuário | `neo tasks list --mine` |

---

## Opções

As opções abaixo são específicas de `neo tasks list`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Atalho | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--mine` | `-m` | Não | `False` | Exibe apenas as stories atribuídas ao seu perfil. |
| `--iteration` | `-i` | Não | *(atual)* | Filtra pela iteração informada (nome, número, ID ou `'all'`). |
| `--service` | `-s` | Não | `shortcut` | Provedor de tarefas (`shortcut`). |

---

## Exemplos

### 1. Listando minhas stories na sprint atual
```bash
neo tasks list --mine
# ou com atalhos: neo tasks list -m
```

### 2. Listando todas as stories de outra sprint
```bash
neo tasks list -i "Sprint 70"
```

### 3. Extraindo IDs e títulos em JSON
```bash
neo --json tasks list -m | jq '.[] | {id, name, state: .workflow_state_id}'
```

---

## Erros comuns e códigos de saída

* **Código 1 (Erro genérico):** Falha na comunicação com a API do Shortcut ou sprint inexistente.
* **Código 2 (Uso incorreto):** Valor inválido para a flag `--iteration`.

---

## Veja também
- [neo tasks show](show.md) — Exibir os detalhes completos de uma história
- [neo tasks search](search.md) — Buscar histórias por texto livre
- [neo tasks resume](resume.md) — Quadro Kanban visual da sprint

