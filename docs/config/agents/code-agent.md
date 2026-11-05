---
name: config-code-agent
description: Guia de configuração do agente de código Google Antigravity e provedores SDD.
alwaysApply: false
---

# Configuração do Code Agent & SDD

O Neo integra-se com agentes de codificação por IA (**Google Antigravity CLI**) e ferramentas de **Spec-Driven Development (SDD)**.

---

## Seção `[agent]` do `config.toml`

As preferências do agente de codificação ficam armazenadas na seção `[agent]` do arquivo `~/.config/neo/config.toml`:

```toml
[agent]
adapter = "antigravity"
command = "agy"
model = "Gemini 3.8 Flash"
sdd-provider = "spec-driven"
```

### Chaves de Configuração

| Chave | Valores Aceitos | Valor Padrão | Descrição |
|---|---|---|---|
| `adapter` | `antigravity` | `antigravity` | Adaptador do agente de IA utilizado pelo Neo. |
| `command` | Ex.: `agy`, `gemini` | `agy` | Executável CLI do agente de código no seu sistema. |
| `model` | Ex.: `Gemini 3.8 Flash`, `pro` | `Gemini 3.8 Flash` | Identificador do modelo repassado ao agente. |
| `sdd-provider` | `spec-driven` \| `spec-kit` | `spec-driven` | Provedor de Spec-Driven Development configurado. |

---

## Comandos de Configuração (`neo config agent`)

Você pode gerenciar as configurações do agente via CLI:

```bash
# Definir executável, modelo e provedor SDD
neo config agent set command agy
neo config agent set model "Gemini 3.8 Flash"
neo config agent set sdd-provider spec-driven

# Consultar valores atuais
neo config agent get command
neo config agent get model

# Listar todas as configurações da seção [agent]
neo config agent list

# Restaurar uma chave para o valor padrão
neo config agent unset model
```

---

## Variáveis de Ambiente

Para ambientes de CI/CD ou sessões temporárias, você pode sobrescrever as configurações via variáveis de ambiente:

| Variável | Descrição |
|---|---|
| `NEO_AGENT_CODE` | Força o executável do agente (ex.: `agy`). |
| `NEO_AGENT_MODEL` | Força o identificador do modelo (ex.: `"Gemini 3.8 Flash"`). |
| `NEO_SDD_PROVIDER` | Força a ferramenta SDD (`spec-driven` ou `spec-kit`). |

Consulte a referência completa de comandos em [`neo agent` & `neo config agent`](../../cli/agent/index.md).
