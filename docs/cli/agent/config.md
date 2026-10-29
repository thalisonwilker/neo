---
name: cli-agent-config
description: Manual do comando neo config agent para gerenciamento de preferências na seção [agent] de config.toml.
alwaysApply: false
---

# neo config agent
> Gerencia preferências do agente de codificação na seção [agent] de config.toml.

O comando `neo config agent` permite configurar os padrões de execução do agente de IA e da esteira SDD gravados em `~/.config/neo/config.toml` sob a seção `[agent]`.

---

## Sintaxe

```bash
neo config agent <ação> [argumentos] [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| `set` | Define uma preferência na seção `[agent]` do `config.toml` | `neo config agent set model "Gemini 3.8 Pro"` |
| `get` | Exibe o valor efetivo de uma chave e sua camada de origem | `neo config agent get command` |
| `list` | Lista todas as chaves da seção `[agent]` com valores e origens | `neo config agent list` |
| `unset` | Remove uma chave personalizada, restaurando o valor padrão | `neo config agent unset model` |

---

## Opções

As opções abaixo são específicas de `neo config agent`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Ações suportadas | Obrigatório | Descrição |
|---|---|---|---|
| `--json` | `get`, `list` | Não | Emite o resultado em formato JSON no `stdout`. |

---

## Chaves Suportadas

| Chave | Padrão | Descrição |
|---|---|---|
| `command` | `agy` | Nome ou caminho absoluto do executável do Antigravity CLI. |
| `model` | `Gemini 3.8 Flash` | Modelo padrão encaminhado para as sessões do agente. |
| `sdd-provider` | `spec-driven` | Provedor de esteira SDD padrão (`spec-driven` ou `spec-kit`). |
| `adapter` | `antigravity` | Adaptador do agente utilizado pelo Neo (atualmente: `antigravity`). |

---

## Exemplos

### 1. Definindo o modelo preferido
```bash
neo config agent set model "Gemini 3.8 Flash"
```

### 2. Consultando o executável configurado
=== "Saída Humana"
    ```bash
    neo config agent get command
    ```
    ```text
    command: agy (origem: default)
    ```

=== "Saída em JSON"
    ```bash
    neo config agent get command --json | jq .
    ```
    ```json
    {
      "key": "command",
      "value": "agy",
      "source": "default"
    }
    ```

### 3. Listando todas as preferências do agente
```bash
neo config agent list
```

---

## Erros comuns e códigos de saída

* **Código 2 (Uso incorreto):** Tentar definir chave inválida ou omitir chave/valor obrigatório.
* **Código 4 (Não encontrado):** Tentar obter via `get` uma chave não existente e sem valor padrão.

---

## Veja também
- [neo agent status](status.md) — Diagnóstico de prontidão do executável e modelo
- [neo agent run](run.md) — Executar sessão interativa com overrides locais
- [neo config show](../index.md#qual-comando-usar-homonimos) — Visão geral de todas as configurações

