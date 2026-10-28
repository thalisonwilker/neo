---
name: cli-agent
description: Manual dos comandos neo config agent e neo agent (Antigravity CLI, modelos e provedores SDD).
alwaysApply: false
---

# `neo agent` & `neo config agent`

Configura e executa o agente de codificação **Google Antigravity CLI (`agy`)** e prepara a integração com os provedores de Spec-Driven Development (**`spec-driven`** e **`spec-kit`**).

---

## Instalação e Autenticação do Antigravity CLI (`agy`)

1. **Instalação:** instale o Google Antigravity CLI conforme a documentação oficial em [antigravity.google/product/antigravity-cli](https://antigravity.google/product/antigravity-cli) e garanta que o executável **`agy`** esteja disponível no `PATH`.
2. **Autenticação:** na primeira execução de `agy` no terminal, siga o fluxo interativo oficial de login da sua conta Google.
3. **Isolamento de credenciais:** o Antigravity gerencia suas próprias credenciais e permissões localmente (`~/.gemini/`). O Neo **nunca** solicita, copia ou armazena tokens de IA em `config.toml` ou no Keyring do Neo.

---

## Configuração Unificada (`neo config agent`)

Gerencia as preferências na seção `[agent]` de `~/.config/neo/config.toml`.

```bash
neo config agent set <chave> <valor>
neo config agent get <chave> [--json]
neo config agent list [--json]
neo config agent unset <chave>
```

### Chaves Suportadas

| Chave | Aliases | Valores Aceitos | Padrão | Validação e Comportamento |
|---|---|---|---|---|
| `command` | `agent-code`, `executable` | Executável no `PATH` (ex.: `agy`) | `agy` | Verifica disponibilidade no `PATH` e executa `<cmd> --version` com timeout de 3s (sem `shell=True`). Se falhar, explica o problema e **preserva a configuração anterior**. |
| `model` | — | Identificador do modelo (ex.: `"Gemini 3.8 Flash"`) | *(padrão do agente)* | Encaminhado ao `agy` via `--model "<model>"`. Consulte `agy models` para listar os modelos disponíveis na sua conta. |
| `sdd-provider` | `sdd`, `sdd-lib` | `spec-driven` \| `spec-kit` | `spec-driven` | Provedor SDD responsável por preparar instruções e skills. Trocar esta chave não apaga nem migra arquivos existentes. |
| `adapter` | — | `antigravity` | `antigravity` | Identidade do adaptador do agente no Neo. |

### Exemplos

```bash
# Validar e salvar o executável do Antigravity CLI
neo config agent set command agy

# Definir o modelo padrão utilizado pelo agente
neo config agent set model "Gemini 3.8 Flash"

# Selecionar o provedor SDD (spec-driven ou spec-kit)
neo config agent set sdd-provider spec-driven

# Consultar e listar preferências
neo config agent get model
neo config agent list
neo config agent list --json | jq '.model.value'

# Restaurar o modelo para o padrão do agente
neo config agent unset model
```

---

## Provedores SDD: `spec-driven` vs `spec-kit`

| Característica | `spec-driven` | `spec-kit` |
|---|---|---|
| **Referência** | [`igoruehara/spec-driven`](https://github.com/igoruehara/spec-driven) | [GitHub Spec Kit (`specify-cli`)](https://github.github.com/spec-kit/integrations/agy.html) |
| **Artefatos no projeto** | `AGENTS.md` + `.agents/skills/*/SKILL.md` | `.speckit/config.toml` + `.agents/skills/speckit-*/SKILL.md` |
| **Comandos no Antigravity** | `/nova-feature`, `/clarificar`, `/validar`, `/auditar` | `/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-implement` |
| **Compatibilidade com `agy`** | Nativa (leitura automática de `AGENTS.md` e `.agents/skills/`) | Nativa (integração `agy` com skills hifenizadas) |

---

## `neo agent status`

Diagnostica a disponibilidade do executável no `PATH`, versão detectada, modelo ativo, provedor SDD e integridade dos arquivos do projeto (`AGENTS.md` e `.agents/skills/`).

### Uso

```bash
neo agent status [--dir <caminho>] [--json]
```

### Exemplo

=== "Saída Humana"
    ```bash
    neo agent status
    ```
    ```text
    ╭─────────────────── Agente & SDD ───────────────────╮
    │ Adaptador: antigravity (default)                                  │
    │ Executável: agy (config) — Disponível (/usr/local/bin/agy — v2.0) │
    │ Modelo: Gemini 3.8 Flash (config)                                 │
    │ Provedor SDD: spec-driven (config) — Pronto                       │
    │ Diretório: /Users/dev/meu-projeto                                 │
    │ AGENTS.md: presente                                               │
    │ Skills descobertas: nova-feature                                  │
    ╰───────────────────────────────────────────────────────────────────╯
    ```

=== "Saída `--json`"
    ```bash
    neo agent status --json
    ```
    ```json
    {
      "adapter": "antigravity",
      "adapter_source": "default",
      "command": "agy",
      "command_source": "config",
      "executable_available": true,
      "resolved_path": "/usr/local/bin/agy",
      "version": "Antigravity CLI v2.0.1",
      "model": "Gemini 3.8 Flash",
      "model_source": "config",
      "sdd_provider": "spec-driven",
      "sdd_source": "config",
      "project": {
        "provider": "spec-driven",
        "target_dir": "/Users/dev/meu-projeto",
        "ready": true,
        "agents_md_exists": true,
        "skills_dir_exists": true,
        "discovered_skills": ["nova-feature"]
      },
      "issues": []
    }
    ```

---

## `neo agent setup`

Prepara de forma **idempotente** as instruções e skills do provedor SDD no diretório escolhido, preservando qualquer personalização existente.

### Uso

```bash
neo agent setup [--sdd-provider <spec-driven|spec-kit>] [--agent <antigravity>] [--dir <caminho>] [--yes] [--json]
```

### Exemplo

```bash
# Preparar projeto com spec-driven
neo agent setup --sdd-provider spec-driven --yes

# Preparar skills do Spec Kit para o Antigravity
neo agent setup --sdd-provider spec-kit --dir ./meu-servico --yes
```

---

## `neo agent run`

Inicia uma sessão interativa do Antigravity CLI no diretório solicitado, encaminhando o modelo configurado (`agy --model "<model>"`) e repassando sinais (`SIGINT`/`SIGTERM`) para encerrar sem processos órfãos.

### Uso

```bash
neo agent run [--agent <antigravity>] [--command <executavel>] [--model <model-id>] [--sdd-provider <spec-driven|spec-kit>] [--dir <caminho>]
```

### Opções de Override (Não alteram `config.toml`)

| Opção | Descrição |
|---|---|
| `--agent <adaptador>` | Identidade do adaptador apenas para esta execução (padrão: `antigravity`). |
| `--command <executavel>` | Executável do agente apenas para esta execução (ex.: `agy`). |
| `--model <model-id>` | Modelo encaminhado via `--model` apenas para esta execução. |
| `--sdd-provider <provedor>` | Provedor SDD validado apenas para esta execução (`spec-driven` ou `spec-kit`). |
| `--dir <caminho>` | Diretório de trabalho (`cwd`) onde o agente será iniciado. |

### Exemplo

```bash
# Iniciar sessão no diretório atual com as preferências salvas
neo agent run

# Iniciar sessão sobrescrevendo o modelo apenas para esta execução
neo agent run --model "Gemini 3.1 Pro (High)" --dir ./backend
```

!!! note "Sessão Interativa de Terminal"
    `neo agent run` exige um terminal interativo e não aceita `--json` (retorna código `2` se invocado com `neo --json agent run`).

---

## Erros e Códigos de Saída

| Código | Significado | Cenário em `neo config agent` / `neo agent` |
|---|---|---|
| `0` | Sucesso | Configuração salva, diagnóstico concluído ou sessão encerrada normalmente. |
| `1` | Erro genérico | Falha inesperada de execução do subprocesso. |
| `2` | Uso incorreto / Validação | Executável inválido em `config agent set command`, chave proibida (`token`), timeout em `--version` ou `--json` em `agent run`. |
| `4` | Não encontrado | Executável ausente no `PATH` ou diretório `--dir` inexistente no momento de `neo agent run`. |
| `5` | Não suportado | Combinação de adaptador (`--agent`) e provedor SDD (`--sdd-provider`) não suportada. |

