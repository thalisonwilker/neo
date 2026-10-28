---
name: spec
description: Contrato da feature 0015 — integração com Antigravity CLI, configuração unificada via `neo config agent` e seleção de provedor SDD.
alwaysApply: true
---

# Spec — Integração Antigravity CLI, Configuração Unificada de Agente e Provedores SDD

> **Fonte da verdade.** Status: implementado  
> **Tier:** Arquitetural (`product.md` + `design.md` + `domain.md` + `spec.md` + `tasks.md`)

## Resumo
Unifica a configuração do ecossistema de agentes em `neo config agent`, permitindo gerenciar executável (`command`), modelo (`model`), provedor SDD (`sdd-provider`) e adaptador (`adapter`), além de orquestrar a execução do Google Antigravity CLI (`agy`) e esteiras SDD (`spec-driven` e `spec-kit`) através do módulo operacional `neo agent`.

---

## Interface e Comandos

### 1. Configuração Unificada (`neo config agent`)

```bash
neo config agent set <chave> <valor>
neo config agent get <chave> [--json]
neo config agent list [--json]
neo config agent unset <chave>
```

#### Tabela de Chaves de Configuração de Agente (`[agent]`)

| Chave | Aliases Aceitos | Valores Suportados | Valor Padrão | Descrição e Validação |
|---|---|---|---|---|
| `command` | `agent-code`, `executable` | Executável no PATH (ex.: `agy`) | `agy` | Comando que inicia o agente. **Validação estrita antes de persistir:** checa `PATH` e resposta a `--version` com timeout de 3s. |
| `model` | — | Identificador textual de modelo (ex.: `"Gemini 3.8 Flash"`) | *(nenhum / padrão do agente)* | Modelo de linguagem e raciocínio repassado ao agente na execução. |
| `sdd-provider` | `sdd`, `sdd-lib` | `spec-driven` \| `spec-kit` | `spec-driven` | Ferramenta SDD para preparação de instruções, templates e skills. |
| `adapter` | — | `antigravity` | `antigravity` | Identidade do adaptador do agente no Neo. |

### 2. Operação do Agente (`neo agent`)

```bash
# Diagnóstico de executável, versão, modelo, provedor SDD e integridade do projeto
neo agent status [--json]

# Preparação da esteira SDD no projeto (idempotente, exibe alterações e pede confirmação)
neo agent setup [--sdd-provider <spec-driven|spec-kit>] [--dir <caminho>] [--yes] [--json]

# Execução da sessão interativa (argumentos estruturados, cwd explícito, repassa SIGINT/SIGTERM)
neo agent run [--agent <antigravity>] [--command <executavel>] [--model <model-id>] [--sdd-provider <spec-driven|spec-kit>] [--dir <caminho>]
```

---

## Critérios de Aceite

### AC-1: Configuração do executável do agente via `neo config agent set command`
- **Dado** que o usuário deseja definir o comando executável do agente
- **Quando** executa `neo config agent set command <comando>` (ou alias `agent-code`) com um executável válido e disponível no PATH (ex.: `agy`)
- **Então** o Neo valida a disponibilidade e compatibilidade com o adaptador Antigravity e persiste o comando na seção `[agent]` do arquivo `~/.config/neo/config.toml`, exibindo mensagem de sucesso e retornando código `0`.

### AC-2: Validação prévia de disponibilidade e compatibilidade antes de persistir
- **Dado** que o comando `neo config agent set command <comando>` é invocado
- **Quando** o executável informado não é encontrado no `PATH` ou falha ao responder à checagem de versão/executabilidade dentro de um timeout de 3 segundos
- **Então** o Neo emite mensagem de erro explicativa indicando a causa e como corrigir, sem invocar shell arbitrário e sem iniciar sessões do agente, retornando código `2` (erro de uso/parâmetro).

### AC-3: Preservação da configuração anterior em caso de falha de validação
- **Dado** que já existe uma configuração válida de `command` em `~/.config/neo/config.toml` (ex.: `agy`)
- **Quando** o usuário tenta configurar um novo executável inexistente ou incompatível com `neo config agent set command binario-invalido`
- **Então** a validação falha e o Neo preserva inalterada a configuração anterior no arquivo `~/.config/neo/config.toml`.

### AC-4: Persistência e recuperação unificada de executável, modelo e provedor SDD
- **Dado** o subgrupo unificado `neo config agent`
- **Quando** o usuário executa:
  - `neo config agent set model <model-id>`, `neo config agent get model` ou `neo config agent unset model`
  - `neo config agent set sdd-provider <spec-driven|spec-kit>`, `neo config agent get sdd-provider` ou `neo config agent unset sdd-provider`
  - `neo config agent list`
- **Então** cada preferência é gravada, consultada, listada e removida na seção `[agent]` de `config.toml`, aceitando `--json` e rejeitando chaves inválidas ou valores de provedor SDD não suportados com código `2`.

### AC-5: Aplicação de overrides pontuais sem alterar preferências persistidas
- **Dado** que o executável, modelo e provedor SDD estão configurados no `config.toml`
- **Quando** o usuário executa `neo agent run --command <outro-executavel> --model <outro-modelo> --sdd-provider <outro-sdd>`
- **Então** o Neo utiliza os valores das flags exclusivamente para aquela sessão de execução, mantendo o arquivo `~/.config/neo/config.toml` inalterado.

### AC-6: Encaminhamento oficial do modelo selecionado ao Antigravity CLI
- **Dado** que um identificador de modelo foi configurado (ex.: `"Gemini 3.8 Flash"`) ou informado via flag `--model`
- **Quando** o Neo inicia o agente Antigravity via `neo agent run`
- **Então** ele constrói a linha de comando repassando a opção oficial confirmada `--model "<model_id>"` (ex.: `agy --model "Gemini 3.8 Flash"`), sem fallback silencioso para modelos não homologados.

### AC-7: Seleção e preparação de provedores SDD (`neo agent setup`)
- **Dado** um projeto e o provedor SDD configurado ou informado via `--sdd-provider`
- **Quando** o usuário executa `neo agent setup`
- **Então**:
  - Para `spec-driven`: prepara as instruções `AGENTS.md` e a pasta `.agents/skills/` (descobertas nativamente pelo Antigravity);
  - Para `spec-kit`: prepara a integração do Antigravity com a CLI `specify` (`specify init --integration agy` ou `specify integration install agy`), respeitando diretórios e convenções oficiais do Spec Kit.

### AC-8: Inicialização do agente no diretório com descoberta de instruções e skills
- **Dado** que o agente e a esteira SDD estão configurados
- **Quando** o usuário executa `neo agent run [--dir <caminho>]`
- **Então** o Neo executa o processo do agente com diretório de trabalho explícito (`cwd`), garantindo que o agente carregue o arquivo de regras `AGENTS.md` e as skills locais do projeto selecionado.

### AC-9: Bloqueio informativo de combinações incompatíveis antes da execução
- **Dado** uma solicitação de execução ou setup
- **Quando** uma combinação de adaptador e provedor for incompatível ou não suportada
- **Então** o Neo interrompe a operação antes de alterar qualquer arquivo ou iniciar qualquer processo, emitindo mensagem clara com código de saída `5` (`UNSUPPORTED`).

### AC-10: Diagnóstico de dependências e ambiente (`neo agent status`)
- **Dado** o ambiente do usuário
- **Quando** o usuário executa `neo agent status` (suportando `--json`)
- **Então** o Neo inspeciona o executável configurado, a disponibilidade no PATH, versão detectada, modelo ativo, provedor SDD e a integridade das instruções do projeto, fornecendo instruções acionáveis de resolução para qualquer item pendente.

### AC-11: Idempotência e preservação de personalizações no setup
- **Dado** que um projeto já possui `AGENTS.md` ou skills customizadas em `.agents/skills/`
- **Quando** o comando `neo agent setup` é executado repetidas vezes
- **Então** o Neo não duplica diretórios nem sobrescreve regras e personalizações customizadas sem aviso e consentimento explícito (suportando `--yes` para automações).

### AC-12: Troca de provedor SDD sem exclusão ou migração destrutiva de artefatos
- **Dado** um projeto com artefatos SDD gerados anteriormente
- **Quando** o usuário altera a preferência com `neo config agent set sdd-provider spec-kit` (ou `spec-driven`)
- **Então** nenhuma especificação (`specs/`), template ou arquivo existente é apagado ou migrado automaticamente.

### AC-13: Preservação estrita dos comportamentos existentes de Git e Tasks
- **Dado** a introdução das configurações de agente e provedores SDD
- **Quando** qualquer comando sob `neo git ...`, `neo tasks ...` ou `neo config show` for executado
- **Então** todos os contratos e comportamentos existentes permanecem intactos, e `neo config show` passa a refletir também o estado do agente, comando, modelo e provedor SDD.

### AC-14: Isolamento absoluto de credenciais e segredos
- **Dado** a execução, diagnóstico e configuração do agente de codificação
- **Quando** qualquer comando `neo config` ou `neo agent` for acionado
- **Então** o Neo não armazena, não solicita e não imprime tokens de API ou segredos do Antigravity em logs, `--verbose`, telas de erro ou saídas `--json`.

### AC-15: Cancelamento gracioso e prevenção de processos órfãos
- **Dado** uma sessão interativa do agente em andamento iniciada por `neo agent run`
- **Quando** o usuário envia uma interrupção (`Ctrl+C` / `SIGINT` ou `SIGTERM`)
- **Então** o Neo repassa imediatamente o sinal ao subprocesso do agente, aguarda o encerramento ordenado e finaliza a sessão sem deixar processos zumbis ou órfãos no sistema.

### AC-16: Documentação completa e consistente com a implementação
- **Dado** os novos comandos e opções implementados
- **Quando** a documentação MkDocs for compilada com `mkdocs build --strict`
- **Então** todos os comandos (`neo config agent set|get|list|unset`, `neo agent status|setup|run`), guia de instalação do Antigravity, tabela de migração e glossário encontram-se documentados e passam na validação sem erros de links.

---

## Matriz de Decisão: Resolução de Parâmetros de Execução

| Flag CLI | Variável de Ambiente | Seção [agent] config.toml | Resultado Utilizado | AC |
|---|---|---|---|---|
| `--command agy-custom` | `NEO_AGENT_CODE=agy-env` | `command = "agy-cfg"` | `agy-custom` (CLI vence) | AC-5 |
| `—` | `NEO_AGENT_CODE=agy-env` | `command = "agy-cfg"` | `agy-env` (ENV vence config) | AC-4 |
| `—` | `—` | `command = "agy-cfg"` | `agy-cfg` (Config persistida) | AC-4 |
| `—` | `—` | `—` | `agy` (Padrão do adaptador) | AC-1, AC-10 |
| `--model "Gemini 3.8 Flash"` | `NEO_AGENT_MODEL=m-env` | `model = "m-cfg"` | `"Gemini 3.8 Flash"` | AC-5, AC-6 |
| `—` | `NEO_AGENT_MODEL=m-env` | `model = "m-cfg"` | `m-env` | AC-4, AC-6 |
| `—` | `—` | `model = "m-cfg"` | `m-cfg` | AC-4, AC-6 |
| `--sdd-provider spec-kit` | `NEO_SDD_PROVIDER=spec-driven` | `sdd-provider = "spec-driven"` | `spec-kit` | AC-5, AC-7 |
| `—` | `NEO_SDD_PROVIDER=spec-kit` | `sdd-provider = "spec-driven"` | `spec-kit` | AC-4, AC-7 |
| `—` | `—` | `sdd-provider = "spec-kit"` | `spec-kit` | AC-4, AC-7 |
| `—` | `—` | `—` | `spec-driven` (Padrão) | AC-7 |

---

## Casos de Borda e Erros
- **Executável não encontrado no PATH:** `neo config agent set command <cmd>` falha com código `2`, sem alterar `config.toml`. `neo agent run` falha com código `4` (`NOT_FOUND`).
- **Timeout na verificação:** executável que trava ou demora mais de 3 segundos no teste é rejeitado com mensagem explicativa e código `2`.
- **Interrupção pelo usuário (`SIGINT`):** repassada ao processo filho sem travamento do terminal do Neo.
- **Provedor SDD inválido:** valores diferentes de `spec-driven` e `spec-kit` são rejeitados na validação com código `2`.

---

## Fora de Escopo
- Orquestração autônoma do ciclo completo de SDD.
- Adaptação de outros agentes (Claude Code, Cursor CLI, Aider) neste incremento.
- Chamadas diretas a APIs REST de modelos.
- Modificação das esteiras e especificações já consolidadas em `specs/` no Neo.

---

## Rastreabilidade
- Product: `./product.md`
- Design: `./design.md`
- Domínio: `./domain.md`
- ADR Relacionado: `docs/architecture/adr/0007-integracao-agente-antigravity-e-sdd.md`
