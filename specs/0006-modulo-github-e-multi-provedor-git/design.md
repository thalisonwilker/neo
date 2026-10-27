---
name: design
description: Technical Design Doc para módulo GitHub e abstração de múltiplos provedores Git na CLI Neo.
alwaysApply: false
---

# Technical Design Doc — Módulo GitHub e Multi-provedor Git

> **Tier:** arquitetural · **Status:** aprovado
> **Autor:** Thalyson Wilker · **Data:** 2026-10-27

## Links e artefatos
- Spec: `./spec.md`
- Product: `./product.md`
- Domínio: `./domain.md`
- ADR relacionado: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md)

---

## Contexto da funcionalidade
Hoje, a CLI Neo implementa comandos como `neo repo`, `neo commits` e `neo workspace` acoplados diretamente ao `BitbucketClient`. Para permitir o trabalho com GitHub e futuros provedores (como GitLab), introduzimos uma interface comum de provedor Git (`GitProviderProtocol` ou `GitProvider`), mantendo a camada de comandos (`commands/`) isolada de detalhes de protocolo de cada API.

---

## Design Proposto: Arquitetura Ports & Adapters

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Camada de Comandos CLI                          │
│         neo repo  ·  neo commits  ·  neo workspace  ·  neo config      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                         resolve_git_provider()
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    Porta / Protocolo (Domain)                          │
│                       GitProviderProtocol                              │
│  - list_repositories(owner)        - list_commits(repo, owner, ...)   │
│  - search_repositories(query)      - list_workspaces()                │
│  - get_repository(repo, owner)     - get_default_workspace()         │
│  - create_repository(name, ...)                                       │
└───────────────────▲────────────────────────────────▲───────────────────┘
                    │                                │
            implementa porta                 implementa porta
                    │                                │
┌───────────────────┴───────────────┐┌───────────────┴───────────────────┐
│     Adaptador: BitbucketClient    ││      Adaptador: GitHubClient      │
│  REST API 2.0 (api.bitbucket.org) ││    REST API v3 (api.github.com)   │
│  Auth: Basic / Bearer             ││    Auth: Bearer / Token           │
└───────────────────────────────────┘└───────────────────────────────────┘
```

### Resolução de Provedor (Hierarquia de Precedência):
1. **Flag explícita na CLI:** `--provider / -p <bitbucket|github>` (sobrescreve tudo).
2. **Auto-detecção via Git Local:** Se o diretório atual tiver um repositório git local cujo remote `origin` seja `github.com` ou `bitbucket.org`.
3. **Configuração Persistida:** Chave `default_provider` em `config.toml` (configurável via `neo config set-provider <provider>`).
4. **Fallback:** `bitbucket` (ou o único provedor que possuir credenciais ativas).

---

## Cobertura dos 5 Eixos

### 1. Tech Stack
- HTTP Client: `httpx` (já existente no projeto).
- API GitHub: REST API v3 oficial (`https://api.github.com`), com header `Accept: application/vnd.github+json` e `X-GitHub-Api-Version: 2022-11-28`.
- Modelagem: `Pydantic v2` para DTOs.

### 2. Arquitetura Base
- Camada `integrations/`: Novo módulo `src/neo/integrations/github.py` e `src/neo/integrations/github_models.py`.
- Camada `integrations/common.py`: Protocolo `GitProviderProtocol` e fábrica `resolve_git_provider()`.
- Adaptadores: `BitbucketClient` e `GitHubClient` satisfazem `GitProviderProtocol`.

### 3. Infra & Segurança
- Armazenamento de token do GitHub via Keyring do SO (`KEYRING_SERVICE_NAME = "neo-cli"`, chave `github`), com fallback para `config.toml` (0600) e variável `GITHUB_TOKEN`.

### 4. Qualidade
- 100% dos cenários cobertos por testes unitários com mocks `respx` e testes E2E com `CliRunner`.
- Cobertura $\ge 80\%$.
- Tipagem estrita com `mypy` e lint limpo com `ruff`.

### 5. Observabilidade & UX
- Terminal com Rich por padrão; mensagens de erro explicativas (ex: token inválido, workspace/org inexistente).
- Suporte total a `--json` em todos os fluxos.

---

## Alternativas Consideradas

| Alternativa | Prós | Contras | Decisão |
|---|---|---|---|
| Subcomandos separados (`neo github repo` e `neo bitbucket repo`) | Simples de rotear | Duplica comandos, pior ergonomia, não auto-detecta pelo repositório | Descartada |
| Comandos unificados (`neo repo`) com `GitProviderProtocol` | Ergonomia consistente, auto-detecção transparente | Exige abstração de porta comum | **Escolhida (Recomendada)** |

---

## Riscos e Mitigações
- **Diferença conceitual Workspace vs Org/User:** No GitHub, repositórios pertencem a uma Organização ou Usuário (Owner). No Bitbucket, pertencem a um Workspace.
  - *Mitigação:* `neo workspace` tratará Organizações + Usuário autenticado como os "workspaces" do GitHub, com nome e slug equivalentes.
