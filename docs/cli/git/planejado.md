---
name: cli-git-planejado
description: Backlog de recursos planejados no módulo Git do Neo (branch, tag, release, repo e ações adicionais de PR).
alwaysApply: false
---

# neo git planejado (🚧)
> Visão geral dos recursos e verbos em desenvolvimento no roadmap da CLI Neo.

!!! warning "Recursos em desenvolvimento"
    Os comandos descritos nesta página fazem parte do backlog planejado e ainda **não estão disponíveis** para execução na versão atual do Neo (`v0.2.0`).

---

## Recursos Planejados

### 1. Branches remotas

Operações em branches remotas e comparação entre branches continuam planejadas. Para operações locais já disponíveis, consulte [branches](branch/index.md).

### 2. Ações adicionais de Pull Request
Inspeção detalhada e merge pela CLI continuam planejados. Para listar PRs abertas, abrir, aprovar, recusar ou pesquisar, consulte [pull requests](pr/index.md).

### 3. Tags e Releases (`neo git tag` & `neo git release`)
Versionamento e publicação de artefatos:

* `neo git tag list`: Lista tags semânticas publicadas.
* `neo git tag create <versão>`: Cria e envia uma nova tag assinada.
* `neo git release list`: Lista releases publicadas com changelog e notas de versão.
* `neo git release create <versão>`: Gera notas automáticas de release e publica no provedor.

### 4. Clonagem de Repositório (`clone`)
* `neo git repo clone <slug>`: Clona repositório remoto via SSH/HTTPS no diretório local. *(Hoje, utilize `neo git repo show` para consultar as URLs de clone).*

---

## Rastreabilidade e Roadmap
- Especificação em planejamento: `specs/0010-branches-prs-e-detalhes-repo/`
- Para sugestões e acompanhamento, consulte o [Repositório Oficial do Neo](https://github.com/thalisonwilker/neo).

