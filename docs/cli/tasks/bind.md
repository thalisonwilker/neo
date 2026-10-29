---
name: cli-tasks-bind
description: Manual dos comandos neo tasks bind e neo tasks unbind para vinculação da demanda ativa ao repositório local.
alwaysApply: false
---

# neo tasks bind / unbind
> Vincula ou remove o vínculo manual de uma tarefa/história do Shortcut ao repositório Git local.

Os comandos `neo tasks bind` e `neo tasks unbind` permitem associar explicitamente o repositório local a uma demanda de trabalho, persistindo o identificador em `.git/neo-context.json`. Essa vinculação tem precedência sobre a inferência automática por nome de branch e é consumida diretamente pelo diagnóstico de [neo config show](../index.md) e [neo git status](../git/status.md).

---

## Sintaxe

```bash
neo tasks bind <id> [--json]
neo tasks unbind [--json]
```

---

## Ações

| Ação / Comando | Descrição | Exemplo de comando |
|---|---|---|
| `bind <id>` | Vincula manualmente uma task ao repositório em `.git/neo-context.json` | `neo tasks bind 2157` |
| `unbind` | Remove a vinculação manual, restaurando a inferência por branch | `neo tasks unbind` |

---

## Opções

| Opção | Atalho | Ações suportadas | Padrão | Descrição |
|---|---|---|---|---|
| `--json` | — | `bind`, `unbind` | `false` | Emite a resposta em JSON estruturado no `stdout`. |
| `--help` | — | `bind`, `unbind` | — | Exibe o manual de ajuda do comando. |

---

## Exemplos

### 1. Vinculando uma demanda ao repositório local
```bash
neo tasks bind 2157
```

**Saída humana:**
```text
✓ Task #2157 vinculada com sucesso ao repositório local (neo-context.json).
```

### 2. Vinculando com saída em JSON
```bash
neo tasks bind 2157 --json
```

**Saída estruturada:**
```json
{
  "status": "success",
  "story_id": 2157,
  "story_title": null,
  "bound": true,
  "path": "/Users/thalysonwilker/Projects/neo/.git/neo-context.json"
}
```

### 3. Removendo a vinculação manual
```bash
neo tasks unbind
```

**Saída humana:**
```text
✓ Vínculo de task manual removido com sucesso do repositório local.
```

---

## Erros comuns e códigos de saída

| Código | Causa | Resolução |
|---|---|---|
| `2` | Executado fora de um repositório Git | Navegue até o diretório raiz de um repositório Git antes de executar `neo tasks bind`. |
| `2` | ID da task não informado ou não numérico | Informe um número inteiro correspondente ao identificador da história no Shortcut. |

---

## Veja também

- [Quadro Kanban (`neo tasks resume`)](resume.md) — Visão ágil das histórias da sprint
- [Status Git (`neo git status`)](../git/status.md) — Diagnóstico de branch e contexto do repositório
- [Visão Geral da CLI](../index.md) — Conceitos de opções globais e códigos de saída

