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

## 📚 Documentação (MkDocs Material)

O Neo conta com documentação técnica completa estilizada com **Material for MkDocs** (paleta claro/escuro, busca instantânea e navegação em abas inspirada no [HTTPX](https://www.python-httpx.org/)):

### Executar via Docker Compose (Conteinerizado)
```bash
# Iniciar o servidor de documentação com live-reload na porta 8000
docker compose -f docker-compose.docs.yml up

# Acessar no navegador: http://localhost:8000
```

### Executar Localmente via `uv`
```bash
# Iniciar servidor local
uv run --group docs mkdocs serve

# Compilar build estático (validação estrita)
uv run --group docs mkdocs build --strict
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
| `neo config show` | Exibe o status geral de autenticação de todos os serviços suportados (`bitbucket`, `github`, `shortcut`), o provedor Git padrão e os tokens mascarados. |
| `neo config auth set <service> [--token <token>]` | Configura o token de API de um serviço (`bitbucket`, `github` ou `shortcut`). Oculta a digitação se `--token` for omitido. |
| `neo config auth get <service>` | Consulta o status e exibe o token mascarado de um serviço específico. |
| `neo config auth delete <service>` | Remove a credencial armazenada com segurança. |
| `neo config set-provider <provider>` | Define o provedor Git padrão global (`github` ou `bitbucket`) persistido em `config.toml`. |
| `neo config get-provider` | Exibe o provedor Git atualmente configurado como padrão. |

#### Exemplos:

```bash
# Configurar token do GitHub (Personal Access Token ou Classic Token com escopo repo)
neo config auth set github --token "ghp_..."

# Configurar token do Shortcut de forma interativa (prompt seguro mascarado)
neo config auth set shortcut

# Configurar token do Bitbucket diretamente via flag
neo config auth set bitbucket --token "meu-app-password"

# Definir GitHub como provedor Git padrão
neo config set-provider github

# Consultar provedor Git padrão
neo config get-provider

# Verificar status de todas as integrações
neo config show

# Consultar credencial específica em formato JSON
neo --json config auth get shortcut

# Remover credencial de um serviço
neo config auth delete bitbucket
```

---

### 2. 🏢 Workspaces / Organizações Git (`neo workspace`)

Permite listar todos os workspaces/organizações acessíveis na conta (Bitbucket Cloud ou GitHub) e definir interativamente ou via flag qual deles é o workspace ativo/padrão, persistindo a escolha em `config.toml`.

#### Comandos Disponíveis:

| Comando | Opções | Descrição |
|---|---|---|
| `neo workspace list` | `[-p, --provider <github\|bitbucket>]` | Lista todos os workspaces ou organizações aos quais a conta tem acesso, indicando com `[● Ativo]` o workspace padrão. |
| `neo workspace current` | `[-p, --provider <github\|bitbucket>]` | Exibe o workspace/organização atualmente selecionado e sua origem (configuração local ou detecção automática via API). |
| `neo workspace select` | `[-p, --provider <github\|bitbucket>]`, `[-s, --slug <slug>]` | Seleciona o workspace ativo. Sem flag, abre um menu interativo no terminal; com `--slug`, define diretamente. |
| `neo workspace set <slug>` | `[-p, --provider <github\|bitbucket>]` | Atalho direto para definir o workspace padrão por slug. |

#### Exemplos:

```bash
# Listar workspaces do Bitbucket ou GitHub (auto-detecta pelo repositório ou provedor padrão)
neo workspace list

# Listar organizações do GitHub explicitamente
neo workspace list --provider github

# Selecionar workspace de forma interativa
neo workspace select

# Definir workspace do Bitbucket
neo workspace set ebi_informatica --provider bitbucket

# Definir organização ativa no GitHub
neo workspace set minha-organizacao --provider github

# Verificar qual workspace está ativo
neo workspace current

# Em formato JSON para scripts
neo --json workspace list
```

---

### 3. 🗄️ Repositórios Git (`neo repo`)

Gerencia e localiza repositórios no Bitbucket Cloud ou GitHub com arquitetura unificada de provedores.

#### Resolução do Provedor Git:
1. Flag explícita: `--provider github` ou `-p bitbucket`.
2. Auto-detecção: se executado dentro de um repositório git local, inspeciona a URL do remote `origin`.
3. Preferência persistida: consulta `default_provider` definido via `neo config set-provider`.
4. Fallback automático: seleciona o provedor que possui credenciais configuradas.

#### Comandos Disponíveis:

| Comando | Opções | Descrição |
|---|---|---|
| `neo repo list` | `[-p, --provider <prov>]`, `[-w, --workspace <ws>]` | Lista os repositórios disponíveis no workspace com visibilidade, branch padrão e data de atualização. |
| `neo repo search <query>` | `[-p, --provider <prov>]`, `[-w, --workspace <ws>]` | Pesquisa repositórios por nome, slug ou texto da descrição. |
| `neo repo clone <slug>` | `[-p, --provider <prov>]`, `[-w, --workspace <ws>]`, `[--ssh \| --https]` | Clona o repositório resolvendo a URL via API e disparando `git clone`. |
| `neo repo create <name>` | `[-p, --provider <prov>]`, `[-w, --workspace <ws>]`, `[--private \| --public]`, `[-d, --description <desc>]`, `[-y, --yes]` | Cria um novo repositório com confirmação de segurança prévia. |

#### Exemplos:

```bash
# Listar repositórios do provedor padrão ou auto-detectado
neo repo list

# Listar repositórios do GitHub explicitamente
neo repo list --provider github

# Pesquisar repositórios contendo "api" no Bitbucket
neo repo search api -p bitbucket

# Clonar repositório forçando SSH
neo repo clone backend-core --ssh

# Criar repositório privado no GitHub sem prompt interativo
neo repo create novo-microservico --provider github --private -d "Microsserviço de pagamentos" -y

# Exportar lista de repositórios em JSON para automações
neo --json repo list > repos.json
```

---

### 4. 📜 Histórico & Commits (`neo commits`)

Consulta histórico de commits no Bitbucket ou GitHub com suporte a auto-detecção do repositório a partir do diretório Git local.

#### Comandos Disponíveis:

| Comando | Opções | Descrição |
|---|---|---|
| `neo commits search` | `[-p, --provider <prov>]`, `[-r, --repo <slug>]`, `[-w, --workspace <ws>]`, `[-a, --author <autor>]`, `[-q, --query <termo>]`, `[-l, --limit <n>]` | Pesquisa commits filtrando por autor, termo na mensagem ou limite. Caso `--repo` seja omitido, detecta o repositório via remote do git local. |

#### Exemplos:

```bash
# Buscar commits no repositório do diretório atual (auto-detecta GitHub ou Bitbucket)
neo commits search

# Filtrar commits por autor em um repositório específico no GitHub
neo commits search --provider github --repo neo --author "Thalyson"

# Buscar alterações relacionadas a uma palavra-chave ou ID de ticket
neo commits search --query "sc-2108" --limit 10

# Obter histórico em JSON
neo --json commits search --limit 5
```

---

### 5. 🎯 Demandas & Stories do Shortcut (`neo story`)

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
4. [x] **Seleção e Gestão de Workspace do Bitbucket** (`specs/0005-selecao-de-workspace-bitbucket`)
5. [ ] **Investigação Cruzada de Bugs** (`specs/0006-analise-cruzada-investigacao-bugs`): correlacionar dados do Shortcut com commits e repositórios do Bitbucket via `neo bug investigate <id>`.

---

**Neo não deve tomar o controle da vida do usuário: deve devolver tempo, clareza e autonomia a ele.**
