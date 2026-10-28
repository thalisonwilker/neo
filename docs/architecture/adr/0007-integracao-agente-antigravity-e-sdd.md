---
name: adr-0007
description: Integração de agentes de codificação (Antigravity CLI) e seleção de provedores SDD via neo config agent e neo agent.
alwaysApply: false
---

# ADR 0007 — Integração de Agentes de Codificação (Antigravity CLI) e Provedores SDD

> **Status:** Aprovado  
> **Data:** 2026-10-28  
> **Decisores:** Time Neo

---

## Contexto

O Neo evolui de uma CLI de apoio operacional para um assistente de desenvolvimento integrado a agentes autônomos de codificação. O primeiro agente a ser suportado é o **Google Antigravity** via sua interface de linha de comando oficial (`agy`).

Simultaneamente, o projeto necessita de flexibilidade na adoção de esteiras de **Spec-Driven Development (SDD)**, permitindo que o desenvolvedor configure e opere de forma coesa e unificada sob o contexto de agente (`neo config agent` e `neo agent`): o executável (`command`), o modelo (`model`), a ferramenta SDD (`sdd-provider`) e o adaptador (`adapter`).

## Decisão

1. **Interface Unificada de Configuração (`neo config agent`):**
   - Centraliza todas as opções de agente sob a gramática:
     - `neo config agent set <chave> <valor>`
     - `neo config agent get <chave>`
     - `neo config agent list`
     - `neo config agent unset <chave>`
   - Chaves válidas: `command` (alias `agent-code`), `model`, `sdd-provider` (alias `sdd`, `sdd-lib`) e `adapter`.
   - A validação de `neo config agent set command <cmd>` verifica a presença no `PATH` via `shutil.which` e testa a compatibilidade executando `[cmd, "--version"]` com timeout de 3 segundos (sem `shell=True`). Caso falhe, a configuração anterior é estritamente preservada.
   - Precedência de resolução: `CLI flag > Variável de Ambiente (NEO_AGENT_CODE, NEO_AGENT_MODEL, NEO_SDD_PROVIDER) > Seção [agent] do config.toml > Padrões`.

2. **Módulo Operacional Unificado (`neo agent`):**
   - `neo agent status`: diagnóstico do ambiente, dependências e integridade das regras/skills.
   - `neo agent setup`: preparação idempotente das esteiras `spec-driven` e `spec-kit`.
   - `neo agent run`: execução interativa segura via `subprocess.Popen` com argumentos estruturados (lista de strings), `shell=False`, `cwd` explícito e encaminhamento dos sinais `SIGINT` e `SIGTERM` para garantir terminal interativo limpo e impedir processos órfãos.

3. **Integração com Antigravity:**
   - O modelo configurado é repassado via flag confirmada `--model "<model_id>"`.
   - A autenticação do agente é delegada integralmente ao Antigravity (`~/.gemini/`), sem replicação de credenciais no Neo.

4. **Preservação de Arquivos e Idempotência:**
   - A troca de provedor SDD no `config.toml` nunca apaga nem migra arquivos do projeto automaticamente.
   - O comando `neo agent setup` analisa previamente os arquivos que serão criados/modificados, solicita confirmação (suportando `--yes`) e opera de forma estritamente idempotente.

## Consequências

### Positivas
- Interface de usuário coesa, intuitiva e consistente com o restante da CLI do Neo (`neo git`, `neo tasks`, `neo agent`).
- Total liberdade para alternar modelos e ferramentas SDD sem alterar o fluxo do agente.
- Segurança reforçada: sem injeção de shell e sem manipulação desnecessária de tokens de IA pelo Neo.

### Negativas / Mitigações
- Necessidade de ter os binários `agy`, `specify` ou `npx` instalados localmente. O comando `neo agent status` diagnostica e orienta o usuário de forma prescritiva.
