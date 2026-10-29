---
name: cli-tasks-analyze
description: Manual do comando neo tasks analyze para análise contextual de stories e geração de sugestões de Git.
alwaysApply: false
---

# neo tasks analyze
> Analisa o contexto da story sugerindo nome de branch Git, prefixos e critérios de aceite.

O comando `neo tasks analyze` inspeciona a descrição, título, labels e tipo de uma história no Shortcut, sintetizando o contexto técnico necessário para que o desenvolvedor inicie o trabalho sem atrito:
* Sugestão de nome padronizado de branch (ex.: `feature/sc-2157-descricao`).
* Sugestão de mensagem inicial de commit semântico.
* Extração estruturada de critérios de aceite (explícitos ou implícitos).
* Alertas de riscos e dependências mapeadas.

---

## Sintaxe

```bash
neo tasks analyze <story_id> [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Processa a história e emite análise contextual e sugestões de Git | `neo tasks analyze 2157` |

---

## Opções

As opções abaixo são específicas de `neo tasks analyze`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Atalho | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--service` | `-s` | Não | `shortcut` | Provedor de tarefas (`shortcut`). |

---

## Exemplos

### 1. Análise visual antes de começar a codar
```bash
neo tasks analyze 2157
```

Exemplo de painel no terminal:
```text
╭─ Análise da Story #2157 ──────────────────────────────────────────╮
│ Título:           Adicionar o FCP ST no CSOSN 900                 │
│ Tipo:             feature                                         │
│ Branch Sugerida:  feature/sc-2157-fcp-st-csosn-900                │
│ Commit Sugerido:  feat(fiscal): adiciona calculo de FCP ST        │
│                                                                   │
│ Critérios de Aceite Identificados:                                │
│   • Validar percentual de FCP retido em operações interestaduais   │
│   • Aplicar apenas quando CSOSN for 900                           │
╰───────────────────────────────────────────────────────────────────╯
```

### 2. Criando a branch diretamente com `--json` e `jq`
```bash
BRANCH=$(neo --json tasks analyze 2157 | jq -r '.suggested_branch')
git checkout -b "$BRANCH"
```

---

## Erros comuns e códigos de saída

* **Código 2 (Uso incorreto):** Não informar o `story_id` ou passar valor não numérico.
* **Código 1 (Erro genérico):** História não localizada no Shortcut.

---

## Veja também
- [neo tasks show](show.md) — Exibir os dados brutos da história
- [neo tasks resume](resume.md) — Quadro Kanban da sprint
- [Guia: Fluxo Diário (Tasks → Branch → Commit)](../../guias/fluxo-diario.md)
