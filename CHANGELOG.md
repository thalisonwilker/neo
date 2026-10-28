# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.

## [0.2.0] — 2026-10-28

### Added
- **Integração com Google Antigravity CLI (`agy`) e Provedores SDD (`0015`):**
  - `neo config agent set | get | list | unset` para configurar `command`, `model`, `sdd-provider` (`spec-driven` e `spec-kit`) e `adapter` na seção `[agent]` de `~/.config/neo/config.toml`, validando disponibilidade no `PATH` e `--version` com timeout de 3s.
  - `neo agent status` para diagnóstico completo de binários, versão, modelo e integridade de `AGENTS.md` e `.agents/skills/`.
  - `neo agent setup` para preparação idempotente das esteiras `spec-driven` e `spec-kit` sem sobrescrever personalizações.
  - `neo agent run` para iniciar sessões interativas com repasse de `--model`, overrides locais e encaminhamento de sinais `SIGINT`/`SIGTERM`.
- **Nova gramática `neo git <recurso> <ação> [--opções]`:**
  - `neo git config set | get | list | unset` para gerenciar as chaves `provider`, `workspace`, `default-branch`, `branch-pattern` e `commit-format` na seção `[git]` de `~/.config/neo/config.toml`.
  - `neo git auth login | status | logout` para autenticação com entrada oculta, armazenamento no Keyring do SO e fallback em `~/.config/neo/credentials.toml` (`0600`).
  - `neo git status` para diagnóstico consolidado do repositório Git local, provedor, workspace e autenticação.
  - `neo git workspace show` para inspecionar detalhes e origem do workspace ativo.
  - `neo git repo show` e paginação automática em `neo git repo list` e `neo git repo search`.
  - `neo git commits list` e `neo git commits show <sha>` para listagem e inspeção individual de commits.
- **Variáveis de ambiente padronizadas:** `NEO_GIT_PROVIDER`, `NEO_GIT_WORKSPACE`, `NEO_GITHUB_TOKEN` (com `GITHUB_TOKEN` e `GH_TOKEN` como alternativas) e `NEO_BITBUCKET_EMAIL` + `NEO_BITBUCKET_TOKEN`.
- **Códigos de saída padronizados:** `0` (sucesso), `1` (erro genérico), `2` (uso incorreto), `3` (erro de autenticação), `4` (não encontrado) e `5` (não suportado pelo provedor).
- **Documentação:** Novas páginas `docs/cli/config.md`, `docs/cli/auth.md`, `docs/cli/status.md` e `docs/migration.md`.

### Changed (Breaking Changes)
- Removidos todos os atalhos de uma letra (`-p`, `-w`, `-r`, `-a`, `-q`, `-l`, `-s`, `-d`, `-y`, `-t`) do módulo `neo git`.
- Removido o suporte a passagem de token por flag (`--token`) no módulo `neo git`; `neo git config set token` é bloqueado com código `2`.
- Tabela de substituição de comandos (`v0.1.x` → novo):
  - `neo git config auth set <provider>` → `neo git auth login --provider <provider>`
  - `neo git config auth get <provider>` → `neo git auth status --provider <provider>`
  - `neo git config auth delete <provider>` → `neo git auth logout --provider <provider> [--yes]`
  - `neo git config set-provider <provider>` → `neo git config set provider <provider>`
  - `neo git config get-provider` → `neo git config get provider`
  - `neo git workspace current` → `neo git workspace show`
  - `neo git workspace set <slug>` → `neo git config set workspace <slug>` ou `neo git workspace select --workspace <slug>`
  - `neo git workspace select --slug <slug>` → `neo git workspace select --workspace <slug>`
  - `neo git repo search <termo>` → `neo git repo search --query <termo>`
  - `neo git commits search` (sem filtro) → `neo git commits list`
  - `neo git repo clone` e `neo git repo create` movidos para o backlog planejado.

## [0.1.1] — 2026-10-28

### Changed
- Revisão da documentação MkDocs e `README.md` com foco em terminal, simplicidade e automação com `--json`.

## [0.1.0] — 2026-10-27

### Added
- Lançamento inicial do pacote `neo-cmd` com módulos `neo git`, `neo tasks` e `neo config`.

