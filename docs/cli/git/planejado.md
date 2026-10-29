---
name: cli-git-planejado
description: Backlog e especificações de recursos planejados no módulo Git do Neo (branch, pr, tag, release).
alwaysApply: false
---

# neo git planejado (🚧)
> Visão geral dos recursos e verbos em desenvolvimento no roadmap da CLI Neo.

!!! warning "Recursos em desenvolvimento"
    Os comandos descritos nesta página fazem parte do backlog planejado e ainda **não estão disponíveis** para execução na versão atual do Neo (`v0.2.0`).

---

## Recursos Planejados

### 1. Branches (`neo git branch`)
Gerenciamento de ramificações remotas e locais integradas ao contexto do workspace:

* `neo git branch list`: Lista branches ativas do repositório remoto com autor do último commit.
* `neo git branch create <nome>`: Cria branch remota a partir da branch principal configurada.
* `neo git branch diff <branch>`: Exibe comparação sintética entre branches.

### 2. Pull Requests (`neo git pr`)
Fluxo completo de code review e abertura de PRs unificado para GitHub e Bitbucket:

* `neo git pr list`: Lista PRs abertos no repositório com status de CI e revisores.
* `neo git pr create`: Abre um novo Pull Request a partir da branch atual, preenchendo template baseado nos commits.
* `neo git pr show <id>`: Detalha descrição, comentários e checks de automação.
* `neo git pr merge <id>`: Realiza o merge do PR via linha de comando após aprovações mínimas.

### 3. Tags e Releases (`neo git tag` & `neo git release`)
Versionamento e publicação de artefatos:

* `neo git tag list`: Lista tags semânticas publicadas.
* `neo git tag create <versão>`: Cria e envia uma nova tag assinada.
* `neo git release list`: Lista releases publicadas com changelog e notas de versão.
* `neo git release create <versão>`: Gera notas automáticas de release e publica no provedor.

### 4. Ações Complementares de Repositório (`clone` e `create`)
* `neo git repo clone <slug>`: Clona repositório remoto via SSH/HTTPS no diretório local. *(Hoje, utilize `neo git repo show` para consultar as URLs de clone).*
* `neo git repo create <nome>`: Cria um novo repositório diretamente no workspace ativo.

---

## Rastreabilidade e Roadmap
- Especificação em planejamento: `specs/0010-branches-prs-e-detalhes-repo/`
- Para sugestões e acompanhamento, consulte o [Repositório Oficial do Neo](https://github.com/thalisonwilker/neo).

