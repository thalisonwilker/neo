---
name: cli-tasks-iterations
description: Manual do comando neo tasks iterations para listar sprints no Shortcut.
alwaysApply: false
---

# neo tasks iterations
> Lista as iterações (sprints) disponíveis no serviço, destacando a sprint atual.

O comando `neo tasks iterations` consulta todas as iterações cadastradas no Shortcut, ordenadas da mais recente para a mais antiga, marcando com um indicador visual qual é a sprint atualmente ativa.

---

## Sintaxe

```bash
neo tasks iterations [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Lista as iterações cadastradas ordenadas por recência | `neo tasks iterations` |

---

## Opções

As opções abaixo são específicas de `neo tasks iterations`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Atalho | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--limit` | `-l` | Não | `15` | Quantidade máxima de iterações exibidas. |
| `--service` | `-s` | Não | `shortcut` | Provedor de tarefas (`shortcut`). |

---

## Exemplos

### 1. Listando as sprints no terminal
```bash
neo tasks iterations
```

Exemplo de visualização:
```text
┏━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ ID   ┃ Nome       ┃ Status    ┃ Início     ┃ Fim        ┃
┡━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2045 │ Sprint 71  │ [● Atual] │ 2026-10-20 │ 2026-11-03 │
│ 2012 │ Sprint 70  │ Concluída │ 2026-10-06 │ 2026-10-20 │
│ 1980 │ Sprint 69  │ Concluída │ 2026-09-22 │ 2026-10-06 │
└━━━━━━┴━━━━━━━━━━━━┴━━━━━━━━━━━┴━━━━━━━━━━━━┴━━━━━━━━━━━━┘
```

### 2. Filtrando com limite e exportando em JSON
```bash
neo --json tasks iterations -l 3 | jq '.[0] | {name, status, id}'
```

---

## Erros comuns e códigos de saída

* **Código 1 (Erro genérico):** Token de acesso ausente ou sem permissões de leitura no workspace do Shortcut.

---

## Veja também
- [neo tasks resume](resume.md) — Visualizar quadro Kanban na sprint atual
- [neo tasks list](list.md) — Listar stories filtrando por iteração
- [neo tasks config](config.md) — Configurar credenciais do Shortcut
