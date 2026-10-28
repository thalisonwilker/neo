---
name: cli-index
description: Visão geral da gramática neo git, verbos padronizados, opções comuns e códigos de saída.
alwaysApply: false
---

# Visão Geral da CLI

O módulo Git do Neo segue uma gramática estrita, previsível e sem abreviações ambíguas:

```text
neo git <recurso> <ação> [argumentos] [--opções]
```

- **Somente opções em forma longa:** o módulo `neo git` não utiliza atalhos de uma letra (`--provider`, `--workspace`, `--repo`, `--query`, `--limit`, `--yes`, `--json`).
- **Comandos em inglês, mensagens em português:** nomes de comandos, chaves e flags são em inglês; tabelas, painéis e mensagens de erro são em português do Brasil.
- **Saída dupla:** formato visual **Rich** por padrão para leitura humana e JSON puro no `stdout` quando `--json` é informado.

---

## Verbos Padronizados

| Verbo | Uso | Recursos |
|---|---|---|
| `list` | Lista registros de um recurso | `config`, `workspace`, `repo`, `commits` *(e planejado: `branch`, `pr`, `tag`, `release`)* |
| `show` | Exibe todos os detalhes de um item específico | `workspace`, `repo`, `commits` *(e planejado: `branch`, `pr`, `tag`, `release`)* |
| `search` | Filtra registros por palavra-chave via `--query` | `repo`, `commits` *(e planejado: `pr`)* |
| `select` | Escolhe o item ativo de forma interativa ou via flag | `workspace` |
| `set` / `get` / `unset` | Define, consulta ou remove uma chave de configuração | `config` |
| `login` / `status` / `logout` | Autentica, verifica ou remove credenciais de um provedor | `auth` |
| `create` / `remove` / `open` / `clone` / `diff` | Ações de criação, remoção, abertura e comparação | *(Planejado no backlog)* |

---

## Opções Comuns

| Opção | Argumento | Descrição |
|---|---|---|
| `--provider` | `github` \| `bitbucket` | Sobrescreve o provedor Git apenas para a execução atual. |
| `--workspace` | `<slug>` | Sobrescreve o workspace (Bitbucket) ou organização/usuário (GitHub). |
| `--repo` | `<slug>` | Informa o repositório alvo (dispensável quando executado dentro de um repositório Git local). |
| `--query` | `<termo>` | Termo de busca nos comandos `search`. |
| `--limit` | `<inteiro>` | Limita a quantidade máxima de itens retornados. |
| `--json` | *(flag booleana)* | Emite JSON puro no `stdout`, sem cores nem bordas decorativas. |
| `--yes` | *(flag booleana)* | Pula a confirmação interativa em ações destrutivas (como `auth logout`). |
| `--help` | *(flag booleana)* | Exibe a ajuda contextual do comando ou subgrupo. |

---

## Tabela de Códigos de Saída

Todo comando do Neo retorna um código de saída semântico para facilitar o uso em scripts shell e pipelines de CI/CD:

| Código | Significado | Quando ocorre |
|---|---|---|
| `0` | **Sucesso** | Comando executado até o fim sem erros. |
| `1` | **Erro genérico** | Erro inesperado de rede, erro `5xx` ou `429` da API, ou operação cancelada na confirmação interativa. |
| `2` | **Uso incorreto** | Opção desconhecida, argumento obrigatório ausente (`--query` faltando em `search`), chave proibida (`config set token`) ou comando antigo removido. |
| `3` | **Erro de autenticação** | Credencial não configurada, token inválido/expirado (`401`) ou permissão negada (`403`). |
| `4` | **Não encontrado** | Repositório, workspace ou commit inexistente (`404`), ou repositório não detectado fora de uma pasta Git. |
| `5` | **Não suportado** | Comando ou operação não suportada pelo provedor ativo (a mensagem inclui sugestão de alternativa). |

---

## Compondo Comandos com `--json` e `jq`

```bash
# Listar apenas os nomes e slugs dos repositórios do provedor ativo
neo git repo list --json | jq '.[] | {name, slug}'

# Filtrar commits de correção e extrair hash curto e autor
neo git commits search --query "fix" --limit 5 --json | jq '.[] | {hash: .hash[0:7], author: .author.display_name}'

# Verificar em um script se o provedor atual está autenticado
neo git status --json | jq -e '.authenticated'
```

---

## Mapa de Páginas da CLI

- **Módulo Git (`neo git`):**
  - [Configuração Git (`neo git config`)](config.md): `set`, `get`, `list`, `unset`.
  - [Autenticação Git (`neo git auth`)](auth.md): `login`, `status`, `logout`.
  - [Workspaces (`neo git workspace`)](workspace.md): `list`, `select`, `show`.
  - [Repositórios (`neo git repo`)](repo.md): `list`, `search`, `show` *(e itens planejados)*.
  - [Commits (`neo git commits`)](commits.md): `list`, `search`, `show` *(e itens planejados)*.
  - [Status Git (`neo git status`)](status.md): diagnóstico de contexto e recursos planejados (`branch`, `pr`, `tag`, `release`).
- **Módulo de Demandas (`neo tasks`):**
  - [Tasks & Demandas (`neo tasks`)](tasks.md): integração com o Shortcut (`resume`, `list`, `search`, `show`, `analyze`, `iterations`, `whoami`).
- **Módulo de Agente & SDD (`neo agent` / `neo config agent`):**
  - [Agente & SDD (`neo agent`)](agent.md): configuração unificada (`neo config agent set|get|list|unset`), diagnóstico (`neo agent status`), preparação SDD (`neo agent setup`) e execução do Antigravity CLI (`neo agent run`).
- **Migração:**
  - [Guia de Migração](../migration.md): equivalência entre comandos antigos e novos.
