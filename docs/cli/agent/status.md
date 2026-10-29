---
name: cli-agent-status
description: Manual do comando neo agent status para diagnóstico do executável Antigravity e arquivos SDD.
alwaysApply: false
---

# neo agent status
> Diagnostica disponibilidade do executável agy, versão, modelo, provedor SDD e arquivos do projeto.

O comando `neo agent status` inspeciona a prontidão da infraestrutura de IA e governança no diretório alvo: valida se o executável do Google Antigravity CLI (`agy`) está instalado no `PATH`, consulta sua versão, exibe o modelo e provedor SDD ativos e avalia a presença dos arquivos fundamentais de governança (`CLAUDE.md`, `.claude/`, `specs/`, `docs/STATE.md`).

---

## Sintaxe

```bash
neo agent status [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Inspeciona e reporta a integridade do agente e da esteira SDD | `neo agent status` |

---

## Opções

As opções abaixo são específicas de `neo agent status`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Obrigatório | Padrão | Descrição |
|---|---|---|---|
| `--dir` | Não | `.` | Diretório raiz do projeto a inspecionar. |
| `--json` | Não | `False` | Emite o diagnóstico estruturado em formato JSON puro no `stdout`. |

---

## Exemplos

### 1. Diagnóstico no terminal (leitura humana)
```bash
neo agent status
```

Exemplo de visualização:
```text
╭─ Diagnóstico do Agente & SDD ─────────────────────────────╮
│ Adaptador:         antigravity                            │
│ Executável (agy):  ✓ Instalado (/usr/local/bin/agy)       │
│ Versão do agy:     v1.4.2                                 │
│ Modelo Padrão:     Gemini 3.8 Flash                       │
│ Provedor SDD:      spec-driven                            │
│                                                           │
│ Governança do Projeto:                                    │
│   • CLAUDE.md:     ✓ Presente                             │
│   • docs/STATE.md: ✓ Presente                             │
│   • specs/:        ✓ Presente (15 especificações)         │
╰───────────────────────────────────────────────────────────╯
```

### 2. Validação automatizada em script de CI com `--json`
```bash
if neo agent status --json | jq -e '.binary_available' > /dev/null; then
  echo "Ambiente pronto para sessões com agentes."
fi
```

---

## Erros comuns e códigos de saída

* **Código 0 (Sucesso):** Diagnóstico concluído e reportado com êxito.
* **Código 1 (Erro genérico):** O executável `agy` não foi encontrado no `PATH` do sistema.

---

## Veja também
- [neo agent setup](setup.md) — Preparar e sincronizar arquivos de governança SDD
- [neo agent run](run.md) — Iniciar sessão interativa do agente
- [neo git status](../git/status.md) — Diagnóstico de contexto Git

