---
name: cli-tasks-search
description: Manual do comando neo tasks search para busca de cards no Shortcut por palavra-chave.
alwaysApply: false
---

# neo tasks search
> Pesquisa stories no Shortcut por palavra-chave ou texto livre.

O comando `neo tasks search` realiza uma consulta em todo o workspace do Shortcut por termos contidos no título, descrição ou comentários dos cards.

---

## Sintaxe

```bash
neo tasks search <query> [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Pesquisa histórias contendo o termo informado | `neo tasks search "login"` |

---

## Opções

As opções abaixo são específicas de `neo tasks search`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Atalho | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--service` | `-s` | Não | `shortcut` | Provedor de tarefas (`shortcut`). |

---

## Exemplos

### 1. Pesquisa rápida por palavra-chave
```bash
neo tasks search "webhook"
```

### 2. Extraindo links diretos e IDs via `jq`
```bash
neo --json tasks search "webhook" | jq '.[] | {id, name, url: .app_url}'
```

---

## Erros comuns e códigos de saída

* **Código 2 (Uso incorreto):** Omitir o termo posicional obrigatório `query`.
* **Código 1 (Erro genérico):** Falha de conexão ou token inválido.

---

## Veja também
- [neo tasks show](show.md) — Exibir todos os detalhes de um card encontrado
- [neo tasks list](list.md) — Listar stories da sprint atual
- [neo tasks analyze](analyze.md) — Analisar o contexto do card para desenvolvimento

