---
name: cli-index
description: Conceitos gerais da CLI Neo, gramática padronizada, matriz de comandos, códigos de saída e guia de homônimos.
alwaysApply: false
---

# Conceitos Gerais da CLI

O Neo é um assistente unificado via linha de comando para desenvolvedores, conectando Git (GitHub e Bitbucket Cloud), demandas (Shortcut) e orquestração de agentes de IA (Antigravity CLI e esteiras SDD).

---

## Gramática Padronizada

A invocação de comandos no Neo segue uma estrutura previsível:

```text
neo <módulo> [recurso] <ação> [argumentos] [--opções]
```

- **Módulos disponíveis:** `neo git`, `neo tasks`, `neo agent`, `neo fin` e o utilitário `neo config`.
- **Comandos em inglês, interface em português:** Nomes de módulos, recursos, ações e flags são em inglês; tabelas, painéis, confirmações e mensagens de erro são em português do Brasil.
- **Ausência de atalhos em `neo git`:** Para evitar ambiguidades entre provedores, o módulo `neo git` **não utiliza atalhos de uma letra** (use `--provider`, `--workspace`, `--repo`, `--query`, `--limit`, `--author`, `--yes`). No módulo `neo tasks`, atalhos curtos ergonômicos são suportados (`-s`, `-i`, `-m`, `-a`, `-c`, `-l`, `-t`).
- **Saída visual e estruturada:** Saída formatada com tabelas e caixas **Rich** por padrão para leitura humana no terminal; JSON puro emitido no `stdout` quando `--json` é utilizado.

---

## Qual comando usar? (Homônimos)

O Neo possui comandos com nomes semelhantes que atuam em contextos e fronteiras distintos:

### Comparativo dos comandos `status`

| Comando | O que inspeciona | Quando usar |
|---|---|---|
| **`neo git status`** | O repositório Git local onde o comando é executado. | Para checar branch atual, alterações locais, detecção automática do provedor e workspace pelo `remote origin`, e se há autenticação válida para o repositório. |
| **`neo git auth status`** | O cofre de credenciais dos provedores Git. | Para verificar se o GitHub e o Bitbucket Cloud estão autenticados (no Keyring ou variáveis de ambiente), sem depender de estar dentro de uma pasta Git. |
| **`neo agent status`** | A prontidão do ambiente de IA e Spec-Driven Development. | Para validar se o executável do Antigravity CLI (`agy`) está instalado no `PATH`, checar a versão, o modelo configurado e a presença dos arquivos de governança SDD (`spec.md`, `CLAUDE.md`, etc.). |

### Comparativo dos comandos de configuração (`config`)

| Comando | Escopo de atuação | Onde salva |
|---|---|---|
| **`neo config show`** | Visão agregada de todo o sistema Neo. | Somente leitura de `[git]`, `[agent]`, `[tasks]` e status de credenciais. |
| **`neo git config`** | Preferências específicas de versionamento (`provider`, `workspace`, `default-branch`, etc.). | Seção `[git]` em `~/.config/neo/config.toml`. |
| **`neo config agent`** | Preferências do agente de IA (`command`, `model`, `sdd-provider`, `adapter`). | Seção `[agent]` em `~/.config/neo/config.toml`. |
| **`neo tasks config`** | Credenciais da API do Shortcut e mapeamento de colunas Kanban. | Keyring do SO e seção `[tasks]` em `~/.config/neo/config.toml`. |

---

## Verbos Padronizados

Para garantir previsibilidade, o Neo organiza suas ações em verbos consistentes:

### Verbos Disponíveis

| Verbo | Propósito | Recursos que utilizam |
|---|---|---|
| `list` | Lista registros tabulares de um recurso | `git config`, `git workspace`, `git repo`, `git commits`, `config agent`, `tasks list`, `tasks iterations`, `fin bank`, `fin category`, `fin tx` |
| `show` | Exibe todos os detalhes e metadados de um registro específico | `git workspace`, `git repo`, `git commits`, `tasks show`, `config show` |
| `get` | Consulta o registro detalhado ou chave de configuração de um recurso | `git config`, `config agent`, `tasks config`, `fin bank`, `fin category`, `fin tx` |
| `create` | Criação de novos recursos locais ou remotos | `fin bank`, `fin category`, `fin tx` |
| `update` | Atualização de metadados ou propriedades de um recurso existente | `fin bank`, `fin tx` |
| `delete` | Remove um recurso existente ou credencial salva | `fin bank`, `fin category`, `fin tx`, `tasks config` |
| `search` | Pesquisa registros por termo ou palavra-chave | `git repo`, `git commits`, `tasks search` |
| `select` | Escolhe o registro ativo de forma interativa ou via flag | `git workspace` |
| `set` | Grava ou atualiza uma chave de configuração | `git config`, `config agent`, `tasks config` |
| `unset` | Remove uma chave de configuração personalizada | `git config`, `config agent` |
| `login` | Autentica um provedor solicitando segredo com digitação oculta | `git auth` |
| `logout` | Remove credenciais armazenadas de um provedor | `git auth` |
| `status` | Diagnostica o estado do repositório, credenciais ou agente | `git status`, `git auth status`, `agent status` |
| `resume` | Renderiza visão consolidada em quadro Kanban no terminal | `tasks resume` |
| `whoami` | Identifica a conta ou membro autenticado no serviço | `tasks whoami` |
| `analyze` | Realiza análise contextual e gera sugestões de branch/commits | `tasks analyze` |
| `setup` | Prepara de forma idempotente arquivos de governança e skills | `agent setup` |
| `run` | Inicia sessão interativa do agente de codificação | `agent run` |

### Verbos Planejados no Backlog (🚧)

!!! warning "Recursos em desenvolvimento"
    Os verbos abaixo fazem parte do roadmap das próximas versões do Neo e ainda não estão disponíveis para execução:

| Verbo | Propósito planejado | Recursos pretendidos |
|---|---|---|
| `clone` 🚧 | Clonagem assistida de repositórios | `git repo` |
| `open` 🚧 | Abertura do recurso na interface web do provedor | `git repo`, `git pr`, `tasks` |
| `diff` 🚧 | Comparação entre branches ou commits | `git repo`, `git branch` |
| `close` / `merge` 🚧 | Finalização e merge de pull requests | `git pr` |

---

## Matriz Recurso × Ação

Esta matriz resume todas as operações mapeadas no Neo, indicando disponibilidade imediata, planejamento ou não aplicabilidade:

| Módulo | Recurso | `list` | `show` | `search` | `select` | `set`/`get` | `auth` | `status` | Outras ações |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **`neo config`** | Geral (`show`) | ➖ | ✅ | ➖ | ➖ | ➖ | ➖ | ➖ | — |
| | Agente (`agent`) | ✅ | ➖ | ➖ | ➖ | ✅ | ➖ | ➖ | `unset` (✅) |
| **`neo git`** | Configuração (`config`) | ✅ | ➖ | ➖ | ➖ | ✅ | ➖ | ➖ | `unset` (✅) |
| | Autenticação (`auth`) | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ | ✅ | `login` (✅), `logout` (✅) |
| | Contexto (`status`) | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ | — |
| | Workspaces (`workspace`) | ✅ | ✅ | ➖ | ✅ | ➖ | ➖ | ➖ | — |
| | Repositórios (`repo`) | ✅ | ✅ | ✅ | ➖ | ➖ | ➖ | ➖ | `clone` (🚧), `create` (🚧) |
| | Commits (`commits`) | ✅ | ✅ | ✅ | ➖ | ➖ | ➖ | ➖ | — |
| | Branches (`branch`) 🚧 | 🚧 | 🚧 | ➖ | 🚧 | ➖ | ➖ | ➖ | `create` (🚧), `diff` (🚧) |
| | Pull Requests (`pr`) 🚧 | 🚧 | 🚧 | 🚧 | ➖ | ➖ | ➖ | ➖ | `create` (🚧), `merge` (🚧) |
| | Tags & Releases 🚧 | 🚧 | 🚧 | ➖ | ➖ | ➖ | ➖ | ➖ | `create` (🚧) |
| **`neo tasks`** | Demandas (`tasks`) | ✅ | ✅ | ✅ | ➖ | ➖ | ➖ | ➖ | `resume` (✅), `whoami` (✅), `iterations` (✅), `analyze` (✅) |
| | Configuração (`config`) | ➖ | ➖ | ➖ | ➖ | ✅ | ➖ | ➖ | `delete` (✅), `columns` (✅) |
| **`neo agent`** | Agente (`agent`) | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ | ✅ | `setup` (✅), `run` (✅) |

**Legenda:**
* ✅ **Disponível:** Funcionalidade implementada e testada no código atual.
* 🚧 **Planejado:** Especificado na visão de produto e presente no backlog de implementação.
* ➖ **Não se aplica:** Ação não compatível com a natureza do recurso.

---

## Opções Globais vs. Opções de Recurso

### Opções Globais (válidas em qualquer nível da CLI)
As opções globais configuram o comportamento fundamental da aplicação:

* `--json`: Suprime qualquer formatação visual e imprime o payload de resposta em JSON puro no `stdout`.
* `--verbose`, `-v`: Ativa logs detalhados de diagnóstico e depuração de requisições HTTP.
* `--version`, `-V`: Exibe a versão instalada do Neo (`v0.2.0`) e finaliza a execução.
* `--help`: Exibe o texto de ajuda contextual do comando ou grupo.

### Opções de Recurso (escopo específico de comando)
Configuram filtros, alvos e paginação nos comandos que as suportam:

* `--provider`: Sobrescreve o provedor Git (`github` ou `bitbucket`) para a chamada atual.
* `--workspace`: Define ou sobrescreve o slug do workspace ou organização alvo.
* `--repo`: Slug do repositório a ser consultado (inferido automaticamente quando executado dentro de uma pasta Git).
* `--query`: Termo obrigatório de busca textual em comandos `search`.
* `--limit`: Limita a quantidade máxima de registros retornados (suporta `-l` em `neo tasks`).
* `--service`, `-s`: Seleciona o provedor de tarefas no módulo `tasks` (padrão: `shortcut`).
* `--yes`: Confirma operações destrutivas sem exibir prompts interativos no terminal.

---

## Tabela de Códigos de Saída

Todo comando do Neo encerra sua execução com um código de saída semântico padronizado, permitindo integração confiável em scripts shell e pipelines de CI/CD:

| Código | Significado | Situação típica |
|---|---|---|
| `0` | **Sucesso** | Operação concluída com êxito. |
| `1` | **Erro genérico** | Erro imprevisto de rede, indisponibilidade de serviço (`5xx`/`429`), ou cancelamento de ação pelo usuário no terminal. |
| `2` | **Uso incorreto** | Argumento obrigatório ausente, flag desconhecida, formato de chave inválido ou invocação de comando legado descontinuado. |
| `3` | **Erro de autenticação** | Token ausente, inválido ou expirado (`401`), credencial sem permissões suficientes (`403`) ou provedor não autenticado. |
| `4` | **Não encontrado** | Repositório, workspace, commit ou card inexistente (`404`), ou comando Git executado fora de um repositório sem `--repo`. |
| `5` | **Não suportado** | Ação ou filtro não suportado pelo provedor Git ativo (com mensagem explicativa de alternativa). |

---

## Compondo Automações com `--json` e `jq`

A flag `--json` permite extrair dados pontuais diretamente no terminal combinando o Neo com `jq`:

```bash
# 1. Listar nome e slug de todos os repositórios do workspace ativo
neo git repo list --json | jq '.[] | {name, slug}'

# 2. Extrair o hash e a mensagem dos 5 últimos commits
neo git commits list --limit 5 --json | jq '.[] | {hash: .hash[0:7], message: .message | split("\n")[0]}'

# 3. Validar se a autenticação do provedor atual está ativa em um script
if neo git status --json | jq -e '.authenticated' > /dev/null; then
  echo "Provedor autenticado com sucesso!"
fi

# 4. Extrair o branch sugerido para uma história do Shortcut
BRANCH=$(neo --json tasks analyze 12345 | jq -r '.suggested_branch')
git checkout -b "$BRANCH"
```
