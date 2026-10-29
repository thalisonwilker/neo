---
name: cli-agent-index
description: Visão geral do módulo neo agent e integração com Google Antigravity CLI e Spec-Driven Development.
alwaysApply: false
---

# neo agent
> Diagnóstico, preparação SDD e execução do agente de codificação Google Antigravity CLI (agy).

O módulo `neo agent` conecta o fluxo de desenvolvimento do Neo à esteira de **Spec-Driven Development (SDD)**, orquestrando o agente de codificação oficial **Google Antigravity CLI (`agy`)**, gerenciando templates de especificação e garantindo governança das regras de projeto.

---

## Sintaxe

```bash
neo agent <ação> [--opções]
# ou para configuração:
neo config agent <ação> [chave] [valor]
```

---

## Organização dos Comandos

O módulo do agente está organizado nos seguintes submenus funcionais:

### 1. Configuração do Agente
- [**Configurações do Agente (`neo config agent`)**](config.md): Define preferências de execução em `~/.config/neo/config.toml` (`set`, `get`, `list`, `unset`).

### 2. Diagnóstico e Status
- [**Diagnóstico do Agente (`neo agent status`)**](status.md): Inspeciona disponibilidade do executável `agy`, versão, modelo configurado, provedor SDD e arquivos do projeto.

### 3. Preparação SDD
- [**Preparação SDD (`neo agent setup`)**](setup.md): Inicializa e sincroniza instruções de projeto (`CLAUDE.md`), templates e skills SDD de forma idempotente.

### 4. Execução Interativa
- [**Execução Interativa (`neo agent run`)**](run.md): Inicia uma sessão de trabalho interativa com o Antigravity CLI no diretório escolhido.

---

## Provedores SDD Suportados

O Neo suporta dois provedores para estruturar a esteira orientada a especificações:

1. **`spec-driven` (Padrão):**
   Esteira completa baseada em gates: `product.md` → `design.md` → `domain.md` → `spec.md` → `tasks.md`.
2. **`spec-kit`:**
   Estrutura enxuta focada em especificações ágeis e decomposição direta de tarefas.

---

## Veja também
- [Conceitos Gerais da CLI](../index.md)
- [Engenharia & SDD — Visão Geral](../../architecture.md)
- [Glossário de Termos](../../glossary.md)
