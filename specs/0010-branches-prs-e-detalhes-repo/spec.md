---
name: spec
description: Contrato da feature 0010 — consulta de branches, pull requests, detalhes de repositório e paginação no Bitbucket e GitHub.
alwaysApply: true
---

# Spec — Branches, Pull Requests e Detalhes de Repositório (`neo git`)

> **Fonte da verdade.** Status: em review
> Tier: **Pequeno** (`spec.md` + `tasks.md` — evolução do contexto Git multi-provedor existente).

## Resumo
Completa o módulo de repositórios e operações Git da Onda 1 (`neo git`), adicionando consulta de **branches** (`neo git branches list`), consulta e inspeção de **pull requests** (`neo git pr list`, `neo git pr show <id>`), exibição de **detalhes de repositório** (`neo git repo show <slug>`) e **paginação** na listagem e busca de repositórios para Bitbucket Cloud e GitHub.

---

## Critérios de aceite

### AC-1: Detalhes de um repositório (`neo git repo show <slug>`)
- **Dado** um usuário autenticado no provedor Git resolvido (`bitbucket` ou `github`);
- **Quando** executa `neo git repo show <slug>` (com `--workspace/-w` e `--provider/-p` opcionais);
- **Então** o sistema consulta `get_repository(repo_slug=slug, workspace=workspace)` e exibe um painel Rich (ou objeto JSON com `--json`) contendo: nome, slug, workspace/owner, visibilidade (`Privado`/`Público`), branch principal (`main_branch`), descrição, URLs de clone (`ssh_clone_url` e `https_clone_url`) e data de atualização (`updated_on`);
- **E** caso o repositório não exista (404), encerra com código `1` e mensagem clara de não encontrado.

### AC-2: Listagem e filtro de branches (`neo git branches list`)
- **Dado** um repositório alvo informado via `--repo/-r <slug>` ou auto-detectado do remote `origin` do diretório Git local;
- **Quando** o usuário executa `neo git branches list [--repo <slug>] [--workspace <ws>] [--provider <prov>] [--query/-q <termo>] [--limit/-l <n>]`;
- **Então** o sistema consulta as branches do repositório no Bitbucket (`/repositories/{ws}/{slug}/refs/branches`) ou no GitHub (`/repos/{owner}/{repo}/branches`), filtra opcionalmente por substring case-insensitive no nome da branch (`--query`) e exibe tabela Rich (ou lista JSON com `--json`) com: **Nome da Branch** e **Último Commit (short hash)**;
- **E** se `--repo` for omitido fora de um repositório Git local, encerra com código `1` orientando o uso de `--repo <slug>`.

### AC-3: Listagem de Pull Requests (`neo git pr list`)
- **Dado** um repositório alvo informado via `--repo/-r <slug>` ou auto-detectado do diretório Git local;
- **Quando** o usuário executa `neo git pr list [--repo <slug>] [--workspace <ws>] [--provider <prov>] [--state/-s <open|merged|declined|all>] [--limit/-l <n>]` (padrão `--state open`);
- **Então** o sistema consulta os pull requests no Bitbucket (`/repositories/{ws}/{slug}/pullrequests`) ou no GitHub (`/repos/{owner}/{repo}/pulls`) mapeando os estados de forma unificada (`open`, `merged`, `declined`/`closed`, `all`) e exibe tabela Rich (ou lista JSON com `--json`) contendo: **ID/Número**, **Título**, **Estado**, **Branches (`source → destination`)** e **Autor**;
- **E** se um valor inválido for passado em `--state`, encerra com código `1` informando os estados válidos (`open`, `merged`, `declined`, `all`).

### AC-4: Detalhes de um Pull Request (`neo git pr show <id>`)
- **Dado** um repositório alvo (`--repo/-r <slug>` ou inferido do Git local) e o número/ID de um Pull Request;
- **Quando** o usuário executa `neo git pr show <id> [--repo <slug>] [--workspace <ws>] [--provider <prov>]`;
- **Então** o sistema consulta os detalhes do PR no provedor correspondente e exibe um painel Rich (ou JSON com `--json`) contendo: ID, título, estado, autor, branches (`source_branch → target_branch`), data de criação/atualização, link web (`web_url`) e descrição;
- **E** caso o PR não exista (404), encerra com código `1` e mensagem amigável.

### AC-5: Paginação na listagem e pesquisa de repositórios
- **Dado** um workspace no Bitbucket ou conta/organização no GitHub com múltiplas páginas de repositórios;
- **Quando** o usuário executa `neo git repo list` ou `neo git repo search <query>`;
- **Então** o cliente segue a paginação da API (campo `next` no Bitbucket e `per_page=100` / links de próxima página no GitHub, até o limite seguro de páginas) garantindo que repositórios além da primeira página sejam listados e encontrados na busca.

---

## Matriz de decisão — Mapeamento de Estados de Pull Request (`--state`)

| Flag `--state` na CLI | Filtro na API Bitbucket (`state=`) | Filtro na API GitHub (`state=` + pós-filtro) | Estado normalizado no modelo | AC |
|---|---|---|---|---|
| `open` (default) | `OPEN` | `state=open` | `OPEN` | AC-3 |
| `merged` | `MERGED` | `state=closed` + `merged_at != null` | `MERGED` | AC-3 |
| `declined` | `DECLINED` | `state=closed` + `merged_at == null` | `DECLINED` | AC-3 |
| `all` | `OPEN`, `MERGED`, `DECLINED` | `state=all` | `OPEN` \| `MERGED` \| `DECLINED` | AC-3 |

---

## Casos de borda e erros
- Executar `neo git branches list`, `neo git pr list` ou `neo git pr show <id>` fora de um repositório Git e sem `--repo` → erro com código `1` orientando informar `--repo <slug>` (AC-2, AC-3, AC-4).
- Repositório sem branches ou sem PRs para o filtro informado → exibe painel informativo (ou `[]` em modo `--json`) com código `0`.
- Erros HTTP `401/403`, `404` e `429` traduzidos para as exceções de domínio (`BitbucketAuthError`/`GitHubAuthError`, `NotFoundError`, `RateLimitError`) sem expor stack trace bruto.

## Fora de escopo
- Criação, aprovação, merge ou fechamento de Pull Requests via CLI (escopo do MVP é consulta e investigação).
- Criação ou deleção de branches remotas via CLI.
- Análise cruzada com o Shortcut (`neo bug investigate <id>`) — será tratada na spec seguinte que consumirá os métodos de branches e PRs criados aqui.

## Rastreabilidade
- Arquitetura: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md)
- Qualidade e Testes: [ADR-0005](../../docs/architecture/adr/0005-padroes-de-qualidade-e-testes.md)
- UX e JSON: [ADR-0006](../../docs/architecture/adr/0006-observabilidade-e-ux-cli.md)
- Specs relacionadas: [0003-modulo-bitbucket](../0003-modulo-bitbucket/spec.md), [0006-modulo-github-e-multi-provedor-git](../0006-modulo-github-e-multi-provedor-git/spec.md), [0009-refactor-cli-git-e-tasks](../0009-refactor-cli-git-e-tasks/spec.md)

