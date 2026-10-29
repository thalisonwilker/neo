---
name: cli-git-index
description: Visão geral do módulo neo git, arquitetura unificada para GitHub e Bitbucket Cloud.
alwaysApply: false
---

# neo git
> Comandos Git unificados para GitHub e Bitbucket Cloud com resolução automática de contexto.

O módulo `neo git` oferece uma interface coesa para gerenciar repositórios, workspaces, histórico de commits, credenciais e configurações sem trocar de sintaxe entre **GitHub** e **Bitbucket Cloud**.

---

## Sintaxe

```bash
neo git <recurso> <ação> [argumentos] [--opções]
```

O módulo não aceita abreviações de uma letra para opções (use `--provider`, `--workspace`, `--repo`, `--query`, `--limit`, `--author`, `--yes`).

---

## Organização dos Comandos

Os comandos do módulo `neo git` estão distribuídos em submenus funcionais:

### 1. Contexto e Acesso
Gerenciamento de credenciais, resolução de diretório local e configurações:

- [**Configurar Token / Autenticação (`neo git auth`)**](auth.md): Login seguro com token no Keyring (`login`), verificação de estado (`status`) e encerramento de sessão (`logout`).
- [**Configurações Gerais (`neo git config`)**](config.md): Definição de provedor padrão, branch principal e formatos sugeridos (`set`, `get`, `list`, `unset`).
- [**Diagnóstico de Contexto (`neo git status`)**](status.md): Inspeciona o repositório local, branch atual, remote, provedor e workspace resolvidos.
- [**Configurar Workspaces (`neo git workspace`)**](workspace.md): Listagem (`list`), seleção interativa (`select`) e inspeção de workspaces ou organizações (`show`).

### 2. Recursos Remotos
Consulta e investigação de repositórios e commits:

- [**Repositórios (`neo git repo`)**](repo.md): Listagem (`list`), busca por texto (`search`) e detalhes completos (`show`).
- [**Commits (`neo git commits`)**](commits.md): Histórico recente (`list`), busca por mensagem (`search`) e detalhes de commit (`show`).

### 3. Backlog e Recursos Planejados
- [**Recursos Planejados (🚧)**](planejado.md): Visão do roadmap para gerenciamento de branches, pull requests, tags e releases.

---

## Opções Comuns do Módulo Git

| Opção | Tipo | Descrição |
|---|---|---|
| `--provider` | `github` \| `bitbucket` | Sobrescreve o provedor Git para o comando atual. |
| `--workspace` | `<slug>` | Sobrescreve a organização/conta (GitHub) ou Workspace (Bitbucket). |
| `--repo` | `<slug>` | Informa o repositório alvo (inferido do Git local se omitido). |
| `--json` | Flag | Emite saída estruturada em JSON no `stdout`. Consulte as [opções globais](../index.md#opcoes-globais-vs-opcoes-de-recurso). |

---

## Veja também
- [Conceitos Gerais da CLI](../index.md)
- [Guia: Trocar de Provedor (GitHub ↔ Bitbucket)](../../guias/trocar-provedor.md)
- [Guia: Uso em CI com `--json`](../../guias/ci-json.md)
