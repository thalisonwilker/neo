---
name: cli-agent-setup
description: Manual do comando neo agent setup para preparação idempotente da esteira SDD e skills do agente.
alwaysApply: false
---

# neo agent setup
> Prepara de forma idempotente as instruções e skills do provedor SDD no diretório alvo.

O comando `neo agent setup` inicializa ou sincroniza a estrutura de Spec-Driven Development no diretório do projeto. Ele garante a presença das regras de contexto (`CLAUDE.md`, `.claude/settings.json`), cria diretórios de especificações (`specs/`) e disponibiliza as skills agênticas oficiais sem sobrescrever arquivos modificados sem consentimento.

---

## Sintaxe

```bash
neo agent setup [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Prepara os arquivos de governança e skills do provedor SDD | `neo agent setup` |

---

## Opções

As opções abaixo são específicas de `neo agent setup`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Obrigatório | Padrão | Descrição |
|---|---|---|---|
| `--sdd-provider` | Não | `spec-driven` | Provedor SDD para preparação (`spec-driven` ou `spec-kit`). |
| `--agent` | Não | `antigravity` | Identidade do adaptador do agente (padrão: `antigravity`). |
| `--dir` | Não | `.` | Diretório alvo onde as instruções e skills serão preparadas. |
| `--yes` | Não | `False` | Confirma a criação dos arquivos ausentes sem prompt interativo. |
| `--json` | Não | `False` | Emite o resultado da preparação em JSON puro no `stdout`. |

---

## Exemplos

### 1. Inicializando um projeto com o provedor padrão
```bash
neo agent setup
```

### 2. Configurando com provedor alternativo sem prompt interativo
```bash
neo agent setup --sdd-provider spec-kit --yes
```

### 3. Execução em scripts com saída JSON
```bash
neo agent setup --dir ./meu-projeto --yes --json | jq .
```

---

## Erros comuns e códigos de saída

* **Código 2 (Uso incorreto):** Valor inválido para `--sdd-provider` ou diretório inexistente.
* **Código 1 (Erro genérico):** Falha de permissão de escrita no sistema de arquivos.

---

## Veja também
- [neo agent status](status.md) — Verificar se os arquivos foram criados com sucesso
- [neo agent run](run.md) — Iniciar sessão do agente no projeto preparado
- [Engenharia & SDD — Visão Geral](../../architecture.md)

