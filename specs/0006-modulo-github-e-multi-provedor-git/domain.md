---
name: domain
description: Modelo de domínio e linguagem ubíqua para múltiplos provedores Git na CLI Neo.
alwaysApply: false
---

# Domain Model (DDD) — Multi-provedor Git

> Subdomínio: **Supporting** (gestão de código-fonte e repositórios).

## Bounded Context
`GitIntegrationContext`: Responsável por consultar, criar, listar e clonar repositórios, consultar commits e gerenciar workspaces/organizações entre diferentes provedores remotos de código (Bitbucket e GitHub).

## Linguagem Ubíqua

| Termo | Definição | NÃO confundir com |
|---|---|---|
| `GitProvider` | Nome do provedor Git suportado (`bitbucket` ou `github`). | `ServiceType` de autenticação (que inclui `shortcut`). |
| `Workspace` | Unidade agregadora de repositórios (Workspace no Bitbucket; Organização ou Conta de Usuário no GitHub). | Diretório de trabalho local do SO. |
| `Repository` | Repositório Git remoto com nome, slug, visibilidade e links de clone. | Repositório local `.git`. |
| `Commit` | Registro de alteração no histórico do Git com hash, autor, data e mensagem. | PR ou branch. |

## Agregados e Value Objects
- **Value Object `GitProviderType`**: Literal `"bitbucket" | "github"`.
- **Value Object `GitRepo` / `BitbucketRepo`**: Modelo unificado com `name`, `slug`, `is_private`, `main_branch`, `updated_on`, `clone_links`.
- **Value Object `GitWorkspace` / `BitbucketWorkspace`**: Modelo com `name`, `slug`, `is_admin`.
- **Value Object `GitCommit` / `BitbucketCommit`**: Modelo com `hash`, `short_hash`, `author`, `date`, `summary`, `message`.

## Relações com Outros Contextos
- Utiliza **Anti-Corruption Layer (ACL)** em `src/neo/integrations/bitbucket.py` e `src/neo/integrations/github.py` para traduzir formatos específicos de cada API externa em DTOs neutros consumidos pela aplicação.
