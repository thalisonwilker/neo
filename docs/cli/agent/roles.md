---
name: cli-agent-roles
description: Catálogo de papéis especializados de agentes de IA suportados pelo Neo (code, refine, review-pr, review-task).
alwaysApply: false
---

# neo agent roles
> Lista todos os papéis especializados de agentes disponíveis e seus contextos de atuação.

O comando `neo agent roles` exibe os perfis suportados pelo Neo para atuação de agentes de inteligência artificial. Cada papel possui diretrizes bem definidas de escopo, permissão de edição de código de produção e injeção de contexto específico.

---

## Sintaxe

```bash
neo agent roles [--json]
```

---

## Papéis Disponíveis

| Papel (`id`) | Título | Modifica Código? | Contexto Principal | Descrição |
|---|---|:---:|---|---|
| `code` | Codificador | Sim | Spec ativa e código do projeto | Implementação técnica de especificações, refatoração e resolução de bugs. |
| `refine` | Refinador de Demandas | Não | Demanda ativa do Shortcut | Decomposição de histórias, critérios de aceite Given/When/Then e preparação de specs SDD. |
| `review-pr` | Revisor de PR | Não | Commits da branch e `git diff` | Revisão técnica de diffs, conformidade com a spec, qualidade de código e segurança. |
| `review-task` | Auditor de DoD | Não | Suíte de testes e checklist | Validação de critérios de aceite (AC-N), status de testes e Definition of Done. |

---

## Opções

| Opção | Atalho | Padrão | Descrição |
|---|---|---|---|
| `--json` | — | `false` | Emite o catálogo estruturado em formato JSON puro no `stdout`. |
| `--help` | — | — | Exibe o manual de ajuda do comando. |

---

## Exemplos

### 1. Visualização em tabela humana
```bash
neo agent roles
```

**Saída esperada:**
```text
                     Papéis de Agentes Especializados do Neo                      
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Papel       ┃ Título                ┃ Modifica Código? ┃ Contexto Principal       ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ code        │ Codificador           │ Sim              │ Spec ativa e código      │
│ refine      │ Refinador de Demandas │ Não              │ Demanda ativa (Shortcut) │
│ review-pr   │ Revisor de PR         │ Não              │ Commits e git diff       │
│ review-task │ Auditor de DoD        │ Não              │ DoD e suíte de testes    │
└━━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━┴━━━━━━━━━━━━━━━━━━━━━━━━━━┘
```

### 2. Emissão em JSON para automações
```bash
neo agent roles --json
```

**Saída estruturada:**
```json
[
  {
    "id": "code",
    "title": "Codificador",
    "description": "Implementação técnica de especificações...",
    "allows_code_edits": true,
    "context_type": "Spec ativa e código-fonte do repositório",
    "model": null
  },
  {
    "id": "refine",
    "title": "Refinador de Demandas",
    "description": "Análise e refinamento de histórias...",
    "allows_code_edits": false,
    "context_type": "Demanda ativa (Shortcut) e requisitos de negócio",
    "model": null
  }
]
```

---

## Veja também
- [Executar Sessão do Agente (`neo agent run`)](run.md)
- [Configuração de Modelos por Papel (`neo config agent`)](config.md)
- [Visão Geral de Agente & SDD](index.md)

