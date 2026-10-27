---
name: README
description: Visão geral, manual de comandos e guia do Neo (Personal Command Assistant).
alwaysApply: false
---

# Neo — Personal Command Assistant

> **Compreenda seus sistemas. Seja dono das suas escolhas.**

**Neo** é um assistente pessoal extensível, executado via linha de comando (CLI), desenvolvido em **Python 3.13 com Typer e Rich**. Seu objetivo é eliminar tarefas manuais repetitivas, organizar fluxos de trabalho (Bitbucket, Shortcut), investigar dados com autonomia e apoiar a tomada de decisões com clareza.

Inspirado filosoficamente no personagem Neo, de *Matrix*, o projeto apoia-se em três princípios fundamentais: **compreender antes de executar**, **preservar as escolhas do usuário** e **evoluir por meio de módulos independentes**.

---

## 🧭 Esteira Spec-Driven Development (SDD)

O desenvolvimento do Neo segue rigorosamente **Spec-Driven Development (SDD)**, combinando **Lean Inception**, **Domain-Driven Design (DDD)** tático e **Design Docs**:

- **Mapa Geral do Projeto:** [docs/README.md](docs/README.md)
- **Estado de Trabalho Vivo:** [docs/STATE.md](docs/STATE.md)
- **Roadmap (Now / Next / Later):** [docs/product/roadmap.md](docs/product/roadmap.md)
- **Diretrizes e Regras para Agentes:** [AGENTS.md](AGENTS.md)
- **Quality Gates e Definition of Done:** [docs/engineering/TESTING.md](docs/engineering/TESTING.md)

---

## 🚀 Instalação e Execução

O Neo é gerenciado com [`uv`](https://docs.astral.sh/uv/):

```bash
# Clonar o repositório
git clone git@bitbucket.org:seu-workspace/neo.git
cd neo

# Sincronizar dependências e ambiente virtual
uv sync

# Executar a CLI localmente
uv run neo --help
```

---

## 📖 Manual de Comandos da CLI

Todas as saídas do Neo são renderizadas com **Rich** por padrão (tabelas formatadas, cores e painéis contextuais). Adicionalmente, qualquer comando suporta a flag global `--json` para emitir dados estruturados em JSON puro no `stdout`, facilitando integrações com `jq`, scripts bash e automações de CI/CD.

```bash
# Flags Globais
neo --help              # Ajuda geral e lista de comandos
neo --version, -V       # Exibe versão instalada (v0.1.0)
neo --json <comando>    # Emite a resposta em JSON puro
neo -v, --verbose       # Habilita mensagens de debug e traces
```

---

### 1. ⚙️ Configuração & Credenciais (`neo config`)

O Neo utiliza o **Keyring nativo do sistema operacional** (macOS Keychain, Linux Secret Service / Keyring, Windows Credential Manager) para proteger tokens de API. Caso o Keyring esteja indisponível em ambientes headless/containers, há fallback automático para arquivo local protegido (`~/.config/neo/credentials.toml` com permissão restrita `0600`) ou variáveis de ambiente.

#### Comandos Disponíveis:

| Comando | Descrição |
|---|---|
| `neo config show` | Exibe o status geral de autenticação de todos os serviços suportados, a origem da credencial e os tokens mascarados. |
| `neo config auth set <service> [--token <token>]` | Configura o token de API de um serviço (`bitbucket` ou `shortcut`). Oculta a digitação se `--token` for omitido. |
| `neo config auth get <service>` | Consulta o status e exibe o token mascarado de um serviço específico. |
| `neo config auth delete <service>` | Remove a credencial armazenada com segurança. |

#### Exemplos:

```bash
# Configurar token do Shortcut de forma interativa (prompt seguro mascarado)
neo config auth set shortcut

# Configurar token do Bitbucket diretamente via flag
neo config auth set bitbucket --token "meu-app-password"

# Verificar status de todas as integrações
neo config show

# Consultar credencial específica em formato JSON
neo --json config auth get shortcut

# Remover credencial de um serviço
neo config auth delete bitbucket
```

---

### 2. 🗄️ Repositórios Bitbucket (`neo repo`)

Gerencia e localiza repositórios no Bitbucket Cloud via API REST 2.0.

#### Comandos Disponíveis:

| Comando | Opções | Descrição |
|---|---|---|
| `neo repo list` | `[-w, --workspace <ws>]` | Lista os repositórios disponíveis no workspace com visibilidade, branch padrão e data de atualização. |
| `neo repo search <query>` | `[-w, --workspace <ws>]` | Pesquisa repositórios por nome, slug ou texto da descrição. |
| `neo repo clone <slug>` | `[-w, --workspace <ws>]`, `[--ssh \| --https]` | Clona o repositório resolvendo a URL via API e disparando `git clone`. |
| `neo repo create <name>` | `[-w, --workspace <ws>]`, `[--private \| --public]`, `[-d, --description <desc>]`, `[-y, --yes]` | Cria um novo repositório no Bitbucket Cloud com confirmação de segurança prévia. |

#### Exemplos:

```bash
# Listar repositórios do workspace padrão ou configurado
neo repo list

# Pesquisar repositórios contendo "api"
neo repo search api

# Clonar repositório forçando SSH
neo repo clone backend-core --ssh

# Criar repositório privado sem prompt interativo
neo repo create novo-microservico --private -d "Microsserviço de pagamentos" -y

# Exportar lista de repositórios em JSON para automações
neo --json repo list > repos.json
```

---

### 3. 📜 Histórico & Commits (`neo commits`)

Consulta histórico de commits no Bitbucket com suporte a auto-detecção do repositório a partir do diretório Git local.

#### Comandos Disponíveis:

| Comando | Opções | Descrição |
|---|---|---|
| `neo commits search` | `[-r, --repo <slug>]`, `[-w, --workspace <ws>]`, `[-a, --author <autor>]`, `[-q, --query <termo>]`, `[-l, --limit <n>]` | Pesquisa commits filtrando por autor, termo na mensagem ou limite. Caso `--repo` seja omitido, detecta o repositório via remote do git local. |

#### Exemplos:

```bash
# Buscar commits no repositório do diretório atual
neo commits search

# Filtrar commits por autor em um repositório específico
neo commits search --repo api-service --author "Thalyson"

# Buscar alterações relacionadas a uma palavra-chave ou ID de ticket
neo commits search --query "sc-2108" --limit 10

# Obter histórico em JSON
neo --json commits search --limit 5
```

---

### 4. 🎯 Demandas & Stories do Shortcut (`neo story`)

Integração direta com a **REST API v3 do Shortcut** (`app.shortcut.com`) para acompanhamento de tarefas, chamados e análise contextual de tickets.

#### Comandos Disponíveis:

| Comando | Opções | Descrição |
|---|---|---|
| `neo story whoami` | — | Valida o token e exibe dados do usuário logado (nome, username `@mention`, e-mail e ID). |
| `neo story list` | `[-m, --mine]` | Lista stories ativas no workspace. A flag `--mine` filtra apenas as demandas atribuídas ao usuário logado. |
| `neo story search <query>` | — | Pesquisa stories ativas por termo, palavra-chave ou título. |
| `neo story show <id>` | — | Exibe detalhes completos de uma story (tipo, labels, link web direto e descrição formatada). |
| `neo story analyze <id>` | — | Analisa o contexto da story, extraindo critérios de aceite, detectando alertas de impedimento/bloqueios, palavras-chave e sugerindo a branch git e o prefixo de commit ideal. |

#### Exemplos:

```bash
# Verificar credencial e usuário autenticado
neo story whoami

# Listar todas as minhas stories ativas
neo story list --mine

# Pesquisar stories sobre login ou autenticação
neo story search "autenticacao"

# Consultar detalhes da story #2108
neo story show 2108

# Analisar contexto da story e obter sugestão de branch e commit
neo story analyze 2108
```

Exemplo de saída de `neo story analyze`:
```text
╭────────────────────────────── Análise de Contexto: Story #2108 ──────────────────────────────╮
│ Título: Ajustar timeout da conexão com gateway de pagamentos                                  │
│ Branch Recomendada: bugfix/sc-2108-ajustar-timeout-da-conexao                                │
│ Prefixo de Commit: [sc-2108]                                                                 │
│ Possui Bloqueios?: Não                                                                       │
│ Palavras-chave de Busca: gateway, timeout, conexao, pagamentos                               │
│                                                                                              │
│ Critérios de Aceite Detectados:                                                              │
│ • Respeitar limite de 5 segundos antes de abortar                                            │
│ • Emitir log de timeout no Datadog                                                           │
╰──────────────────────────────────────────────────────────────────────────────────────────────╯
```

---

## 🛠️ Stack Tecnológico & Arquitetura

- **Linguagem & Runtime:** Python >= 3.13 gerenciado com `uv`
- **Framework de CLI:** Typer + Rich
- **Modelagem de Dados:** Pydantic v2
- **Camada de Segurança:** Keyring (com fallback `0600`)
- **Arquitetura:** DDD Tático em camadas (`interfaces` / `commands` → `services` → `integrations` / `infrastructure` → `domain`)
- **Qualidade & Testes:** Pytest (Unitários e E2E CLI), Ruff (Linter/Formatter), Mypy (Tipagem estrita)

```bash
# Rodar todos os testes automatizados
uv run pytest -v

# Cobertura de código (mínimo 80%)
uv run pytest --cov=neo

# Verificação de lint e formatação
uv run ruff check .
uv run ruff format --check .

# Verificação estática de tipos
uv run mypy src
```

---

## 🗺️ Próximos Passos (Roadmap da Onda 1)

1. [x] **Fundação da CLI e Autenticação Segura** (`specs/0002-fundacao-cli-e-configuracao`)
2. [x] **Módulo Bitbucket** (`specs/0003-modulo-bitbucket`)
3. [x] **Módulo Shortcut API v3** (`specs/0004-modulo-shortcut`)
4. [ ] **Investigação Cruzada de Bugs** (`specs/0005-analise-cruzada-investigacao-bugs`): correlacionar dados do Shortcut com commits e repositórios do Bitbucket via `neo bug investigate <id>`.

---

**Neo não deve tomar o controle da vida do usuário: deve devolver tempo, clareza e autonomia a ele.**
