---
name: spec
description: Contrato da feature 0014 — refatoração da gramática de `neo git`, separação entre `config` e `auth`, novos comandos de leitura (`status`, `commits list/show`, `repo show`, `workspace show`), códigos de saída padronizados e atualização completa da documentação.
alwaysApply: true
---

# Spec — Refatoração da Gramática `neo git` e Padronização da CLI

> **Fonte da verdade.** Status: implementado
> Tier: **Pequeno** (`spec.md` + `tasks.md` — redesenho da gramática da borda CLI do módulo `git`, precedência de configuração/autenticação, códigos de saída e documentação MkDocs).

## Resumo
Refatora o módulo `neo git` para a gramática estrita `neo git <recurso> <ação> [argumentos] [--opções]`, removendo todos os atalhos de uma letra, separando configuração (`neo git config`) de autenticação (`neo git auth`), adicionando comandos de inspeção (`neo git status`, `neo git workspace show`, `neo git repo show`, `neo git commits list`, `neo git commits show <sha>`), padronizando códigos de saída (`0` a `5`) e atualizando toda a documentação MkDocs e guia de migração.

---

## Gramática e Regras Globais do Módulo `neo git`

```text
neo git <recurso> <ação> [argumentos] [--opções]
```

1. **Somente opções em forma longa:** nenhum comando de `neo git` aceita flags curtas de uma letra (`-p`, `-w`, `-r`, `-a`, `-q`, `-l`, `-s`, `-d`, `-y`, `-t` são removidas).
2. **Verbos padronizados:**
   - Configuração: `set`, `get`, `list`, `unset`
   - Autenticação: `login`, `status`, `logout`
   - Recursos (`workspace`, `repo`, `commits`): `list`, `show`, `search`, `select` (e no backlog: `create`, `remove`, `open`, `clone`, `diff`)
   - Diagnóstico de contexto: `neo git status`
3. **Idioma:** comandos, subcomandos, chaves e opções em inglês; mensagens de saída, prompts e erros em português do Brasil.
4. **Suporte a `--json`:** todo comando de leitura aceita `--json` (tanto na raiz `neo --json git ...` quanto no comando `neo git ... --json`), emitindo JSON puro no `stdout`, sem cores ANSI nem texto decorativo.
5. **Confirmação em ações destrutivas:** exigem confirmação interativa (`typer.confirm`), com opção longa `--yes` para pular.
6. **Opções comuns padronizadas:** `--provider <github|bitbucket>`, `--workspace <slug>`, `--repo <slug>`, `--json`, `--limit <n>`.

---

## Escopo: Implementar Agora vs. Backlog (Planejado)

### Implementar agora
```bash
# Configuração (chaves: provider, workspace, default-branch, branch-pattern, commit-format)
neo git config set <chave> <valor>
neo git config get <chave>
neo git config list
neo git config unset <chave>

# Autenticação
neo git auth login --provider <github|bitbucket>
neo git auth status
neo git auth logout --provider <github|bitbucket>

# Leitura e Seleção
neo git workspace list
neo git workspace select [--workspace <slug>]
neo git workspace show [--workspace <slug>]

neo git repo list
neo git repo search --query <termo>
neo git repo show [<slug>] [--repo <slug>]

neo git commits list
neo git commits search --query <termo>
neo git commits show <sha>

neo git status
```

### Backlog ("Planejado" — documentar com `!!! note "Planejado"`, não implementar agora)
- **Branches (`neo git branch`):** `neo git branch list`, `neo git branch show <nome>`, `neo git branch create <nome>`, `neo git branch remove <nome> [--yes]`
- **Pull Requests (`neo git pr`):** `neo git pr list`, `neo git pr show <id>`, `neo git pr create`, `neo git pr search --query <termo>`
- **Tags (`neo git tag`):** `neo git tag list`, `neo git tag show <nome>`, `neo git tag create <nome>`, `neo git tag remove <nome> [--yes]`
- **Releases (`neo git release`):** `neo git release list`, `neo git release show <tag>`, `neo git release create <tag>`
- **Repositórios (ações adicionais):** `neo git repo open`, `neo git repo clone <slug>`, `neo git repo create <nome> [--yes]`
- **Commits (ações adicionais):** `neo git commits diff <sha>`

---

## Tabela de Migração (Comando Antigo → Comando Novo)

| Comando Antigo (`v0.1.0` / `v0.1.1`) | Comando Novo (`v0.2.0`) | Observação |
|---|---|---|
| `neo git config auth set <provider> [--token ...]` | `neo git auth login --provider <provider>` | Entrada somente via prompt oculto (sem `--token`) |
| `neo git config auth get <provider>` | `neo git auth status [--provider <provider>]` | Nunca exibe partes sensíveis ou token |
| `neo git config auth delete <provider>` | `neo git auth logout --provider <provider> [--yes]` | Pede confirmação (ou `--yes`) |
| `neo git config set-provider <provider>` | `neo git config set provider <provider>` | Unificado em `config set <chave> <valor>` |
| `neo git config get-provider` | `neo git config get provider` | Unificado em `config get <chave>` |
| `neo git workspace current` | `neo git workspace show` | Verbo padronizado `show` |
| `neo git workspace set <slug>` | `neo git config set workspace <slug>` ou `neo git workspace select --workspace <slug>` | Padronizado entre `config set` e `workspace select` |
| `neo git workspace select --slug <slug> -p <prov>` | `neo git workspace select --workspace <slug> --provider <prov>` | Sem atalhos curtos; `--slug` vira `--workspace` |
| `neo git repo search <termo> -w <ws> -p <prov>` | `neo git repo search --query <termo> --workspace <ws> --provider <prov>` | `--query` explícito; sem `-w` ou `-p` |
| `neo git repo clone <slug>` | *(Planejado no backlog)* | Removido da superfície ativa até implementação |
| `neo git repo create <nome> -d ... -y` | *(Planejado no backlog)* | Removido da superfície ativa até implementação |
| `neo git commits search` (sem filtro) | `neo git commits list` | Listagem separada de busca (`search --query`) |
| `neo git commits search -q <termo> -r <repo> -l <n>` | `neo git commits search --query <termo> --repo <repo> --limit <n>` | Sem atalhos de uma letra |

---

## Códigos de Saída Padronizados

| Código | Significado | Quando ocorre |
|---|---|---|
| `0` | Sucesso | Operação concluída sem erros |
| `1` | Erro genérico | Falha de rede, erro inesperado da API (`5xx`, rate limit `429`) ou operação cancelada pelo usuário |
| `2` | Uso incorreto | Flag desconhecida, atalho de uma letra removido, argumento obrigatório ausente, chave de `config` inválida (ex.: `token`), comando antigo removido |
| `3` | Erro de autenticação | Credencial não configurada, token inválido/expirado (`401`) ou permissão insuficiente (`403`) |
| `4` | Não encontrado | Repositório, workspace ou commit inexistente (`404`), ou repositório não informado fora de diretório Git |
| `5` | Não suportado | Operação ou recurso não suportado pelo provedor ativo (inclui sugestão de alternativa na mensagem) |

---

## Critérios de Aceite

### AC-1: Gramática estrita e remoção de atalhos de uma letra
- **Dado** qualquer comando ou subcomando sob `neo git`;
- **Quando** o usuário passa um atalho de uma letra (como `-p`, `-w`, `-r`, `-a`, `-q`, `-l`, `-s`, `-d`, `-y`, `-t`);
- **Então** a CLI rejeita a opção com código de saída `2` (uso incorreto);
- **E** todos os comandos de leitura (`config get`, `config list`, `auth status`, `workspace list`, `workspace show`, `repo list`, `repo search`, `repo show`, `commits list`, `commits search`, `commits show`, `status`) aceitam `--json` tanto antes quanto depois do subcomando.

### AC-2: Gerenciamento de configuração (`neo git config set|get|list|unset`) e precedência
- **Dado** as chaves válidas da seção `[git]` em `~/.config/neo/config.toml`: `provider`, `workspace`, `default-branch`, `branch-pattern` e `commit-format`;
- **Quando** o usuário executa `neo git config set <chave> <valor>`, `get <chave>`, `list` ou `unset <chave>`;
- **Então** o sistema valida a chave, grava/lê/lista/remove o valor na seção `[git]` de `config.toml` com permissão `0600`;
- **E** se `<chave>` for `token`, falha com código `2` e mensagem orientando a usar `neo git auth login --provider <github|bitbucket>`;
- **E** a resolução de `provider` e `workspace` em qualquer comando `neo git` respeita estritamente a precedência:
  1. Opção de linha de comando (`--provider`, `--workspace`)
  2. Variável de ambiente (`NEO_GIT_PROVIDER`, `NEO_GIT_WORKSPACE`)
  3. Seção `[git]` do `config.toml` (`provider`, `workspace`)
  4. Auto-detecção pelo `remote origin` do repositório Git local
  5. Padrão (`github` se autenticado apenas no GitHub, ou `bitbucket`).

### AC-3: Autenticação segura (`neo git auth login|status|logout`) e variáveis de ambiente
- **Dado** o subgrupo `neo git auth`;
- **Quando** o usuário executa:
  - `neo git auth login --provider github`: solicita o Personal Access Token com entrada oculta;
  - `neo git auth login --provider bitbucket`: exibe aviso de que App Passwords foram descontinuadas em favor de API Tokens, solicita o e-mail da conta e, em seguida, o API Token com entrada oculta;
  - `neo git auth status [--provider <github|bitbucket>] [--json]`: exibe se cada provedor está autenticado e a fonte (`env`, `keyring`, `file`, `none`), sem nunca expor o token nem partes dele em logs, erros, `--verbose` ou `--json`;
  - `neo git auth logout --provider <github|bitbucket> [--yes]`: pede confirmação interativa (ou pula com `--yes`) e remove a credencial do Keyring e do arquivo local `0600`;
- **Então** nenhum comando aceita token via argumento ou flag (`--token` não existe);
- **E** a resolução de credenciais para automação aceita `NEO_GITHUB_TOKEN` (com `GITHUB_TOKEN` e `GH_TOKEN` como alternativas) para GitHub, e `NEO_BITBUCKET_EMAIL` + `NEO_BITBUCKET_TOKEN` (com `BITBUCKET_TOKEN` como alternativa) para Bitbucket Cloud, seguindo a ordem: variáveis de ambiente > Keyring do SO > arquivo `~/.config/neo/credentials.toml` (`0600`).

### AC-4: Comandos de Workspace (`neo git workspace list|select|show`)
- **Dado** um usuário autenticado no provedor resolvido (`github` ou `bitbucket`);
- **Quando** executa:
  - `neo git workspace list [--provider <p>] [--limit <n>] [--json]`: lista os workspaces (Bitbucket) ou organizações/conta pessoal (GitHub) marcando o ativo;
  - `neo git workspace select [--provider <p>] [--workspace <slug>]`: seleciona interativamente pelo teclado (ou diretamente se `--workspace <slug>` for passado) e salva em `[git].workspace` no `config.toml`;
  - `neo git workspace show [--provider <p>] [--workspace <slug>] [--json]`: exibe os detalhes do workspace ativo ou informado (nome, slug, provedor, permissão de admin e fonte da resolução: `cli`, `env`, `config`, `remote` ou `default`);
- **Então** retorna código `0` em caso de sucesso, `3` se não autenticado e `4` se o workspace informado não for encontrado.

### AC-5: Comandos de Repositório (`neo git repo list|search|show`)
- **Dado** um usuário autenticado no provedor resolvido;
- **Quando** executa:
  - `neo git repo list [--provider <p>] [--workspace <ws>] [--limit <n>] [--json]`: lista repositórios paginados do workspace resolvido;
  - `neo git repo search --query <termo> [--provider <p>] [--workspace <ws>] [--limit <n>] [--json]`: filtra repositórios por nome, slug ou descrição exigindo a opção `--query`;
  - `neo git repo show [<slug>] [--repo <slug>] [--provider <p>] [--workspace <ws>] [--json]`: exibe detalhes completos do repositório (informado por argumento/opção `--repo` ou auto-detectado do diretório Git local);
- **Então** retorna código `0` em caso de sucesso, `2` se `--query` for omitido em `search`, `3` em falha de autenticação e `4` se o repositório não existir ou não puder ser detectado.

### AC-6: Comandos de Commits (`neo git commits list|search|show`)
- **Dado** um repositório alvo informado via `--repo <slug>` ou auto-detectado do diretório Git local;
- **Quando** o usuário executa:
  - `neo git commits list [--repo <slug>] [--workspace <ws>] [--provider <p>] [--author <autor>] [--limit <n>] [--json]`: lista os commits recentes do repositório;
  - `neo git commits search --query <termo> [--repo <slug>] [--workspace <ws>] [--provider <p>] [--author <autor>] [--limit <n>] [--json]`: busca commits cuja mensagem contenha `<termo>` (opção `--query` obrigatória);
  - `neo git commits show <sha> [--repo <slug>] [--workspace <ws>] [--provider <p>] [--json]`: exibe detalhes completos do commit `<sha>` (hash completo, hash curto, autor, data ISO, mensagem completa e URL);
- **Então** retorna código `0` em sucesso, `2` se `--query` ou `<sha>` faltar, `3` em erro de autenticação e `4` se o repositório ou commit `<sha>` não for encontrado.

### AC-7: Diagnóstico de contexto (`neo git status`)
- **Dado** qualquer diretório local (dentro ou fora de um repositório Git);
- **Quando** o usuário executa `neo git status [--json]`;
- **Então** exibe um painel (ou objeto JSON) consolidando:
  - Contexto Git local: se é um repositório Git (`is_git_repo`), branch atual (`current_branch`), estado da working tree (`clean: true|false`) e URL do `remote origin`;
  - Contexto Neo resolvido: `provider` ativo + fonte (`env`, `config`, `remote`, `default`), `workspace` ativo + fonte, `repo` detectado e status de autenticação do provedor ativo (`authenticated: true|false`, `auth_source`).

### AC-8: Códigos de saída, interface de provedor e bloqueio orientativo de comandos antigos
- **Dado** a execução de qualquer comando `neo git`;
- **Quando** ocorre erro de autenticação (`3`), recurso não encontrado (`4`), operação não suportada pelo provedor (`5`) ou tentativa de executar comando removido da versão anterior (`neo git config auth ...`, `neo git config set-provider`, `neo git config get-provider`, `neo git workspace current`, `neo git workspace set`, `neo git repo clone`, `neo git repo create`);
- **Então** a CLI encerra com o código de saída correspondente (`2` para comando antigo/uso incorreto, `3`, `4` ou `5`) e imprime mensagem em português dizendo exatamente o que aconteceu e qual o novo comando ou ação recomendada.

### AC-9: Documentação MkDocs, Glossário, Migração e CHANGELOG
- **Dado** a documentação do projeto em `docs/`, `mkdocs.yml`, `README.md` e `CHANGELOG.md`;
- **Quando** compilada com `uv run --group docs mkdocs build --strict`;
- **Então** o build passa sem erros ou links quebrados, contendo:
  - `docs/index.md`, `docs/getting-started.md` (com admonition PEP 668 `externally-managed-environment` e fluxo `auth login` + `config set`), `docs/configuration.md` (seção `[git]`, precedência e variáveis `NEO_*`);
  - `docs/cli/index.md` (gramática, verbos, opções comuns e tabela de códigos de saída `0`–`5`);
  - `docs/cli/config.md`, `docs/cli/auth.md`, `docs/cli/workspace.md`, `docs/cli/repo.md`, `docs/cli/commits.md` e `docs/cli/status.md` seguindo o modelo de 7 seções por comando e marcando comandos de backlog com `!!! note "Planejado"`;
  - `docs/glossary.md` atualizado com `Provider / Provedor`, `Workspace` (equivalência Bitbucket Workspace vs GitHub Organization/User), `API Token / Personal Access Token` e `Keyring`;
  - `docs/migration.md` e `CHANGELOG.md` com a tabela completa `comando antigo → comando novo` e lista de breaking changes.

---

## Matriz de Decisão — Precedência e Códigos de Saída

| Cenário | Entrada / Estado | Resultado Observável | Exit Code | AC |
|---|---|---|---|---|
| Uso de flag curta removida | `neo git repo list -p github` | Erro de opção inexistente | `2` | AC-1 |
| Tentativa de salvar token via config | `neo git config set token abc` | Erro orientando `neo git auth login --provider <p>` | `2` | AC-2 |
| Comando antigo removido | `neo git workspace current` | Erro apontando o novo comando `neo git workspace show` | `2` | AC-8 |
| Sem credencial ou token inválido (401/403) | `neo git repo list` sem token | Erro orientando `neo git auth login --provider <p>` | `3` | AC-3, AC-8 |
| Repositório ou commit não encontrado (404) | `neo git commits show deadbeef` | Erro informando que o commit não foi encontrado | `4` | AC-6, AC-8 |
| Fora de repo Git sem `--repo` | `neo git commits list` em `/tmp` | Erro orientando passar `--repo <slug>` | `4` | AC-6, AC-8 |
| Operação não suportada pelo provedor | Método lança `UnsupportedProviderOperationError` | Erro claro + sugestão de alternativa | `5` | AC-8 |

---

## Ponto de Decisão para Aprovação: Comandos Antigos (Aliases Depreciados vs. Remoção com Erro Orientativo)

### Opção A (Recomendada): Remover os comandos antigos e falhar com mensagem orientativa (Exit Code `2`)
- **Como funciona:** Comandos antigos (`neo git config auth ...`, `neo git config set-provider`, `neo git workspace current`, `neo git workspace set`, `neo git repo clone/create`) não executam a ação antiga; eles interceptam a chamada, exibem exatamente qual é o comando novo equivalente (ou informam que foi movido para o backlog planejado) e encerram com código `2`.
- **Prós:**
  - Cumpre literalmente o requisito de teste: *"Teste garantindo que o comando antigo falha com mensagem apontando o novo"*.
  - Mantém `--help` limpo e alinhado à nova gramática sem duplicar subcomandos.
  - Como o projeto está na fase `v0.1.x` (pré-`1.0`), evita carregar dívida técnica e código morto de flags curtas e fluxos inseguros (como `--token` em linha de comando).
- **Contras:**
  - Scripts existentes precisam atualizar os comandos imediatamente ao atualizar o pacote.

### Opção B: Manter os antigos funcionando como aliases ocultos depreciados por uma versão
- **Como funciona:** Imprime um warning no `stderr` e redireciona para o comando novo (exceto onde a semântica mudou, como `auth set --token` que viola a regra de segurança de nunca aceitar token por argumento).
- **Prós:**
  - Transição gradual para alguns comandos de leitura (`workspace current`).
- **Contras:**
  - Conflita com a exigência de que o comando antigo **falhe** no teste automatizado e com a proibição de aceitar `--token` por argumento em `config auth set`.

---

## Casos de Borda e Erros
- **Bitbucket Cloud (App Passwords descontinuadas):** O Bitbucket Cloud exige o e-mail da conta Atlassian + API Token para autenticação Basic HTTP (`email:api_token`). O comando `neo git auth login --provider bitbucket` solicita o e-mail e o API Token separadamente (ou aceita `NEO_BITBUCKET_EMAIL` + `NEO_BITBUCKET_TOKEN` via ambiente) e nunca expõe o segredo.
- **Execução de `auth login` em modo não-interativo / `--json`:** Falha imediatamente com código `2` orientando o uso das variáveis `NEO_GITHUB_TOKEN` ou `NEO_BITBUCKET_EMAIL` + `NEO_BITBUCKET_TOKEN`.
- **Vazamento de segredos:** Qualquer log HTTP em `--verbose` ou serialização `--json` mascara cabeçalhos `Authorization` e nunca inclui o valor do token.

## Fora de Escopo
- Alterar o funcionamento ou gramática do módulo `neo tasks`.
- Implementar os comandos listados como backlog (`branch`, `pr`, `tag`, `release`, `repo open/clone/create`, `commits diff`) — devem apenas constar na documentação como `!!! note "Planejado"`.
- Adicionar novas dependências externas no `pyproject.toml`.

## Rastreabilidade
- Arquitetura: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md)
- Segurança e Credenciais: [ADR-0004](../../docs/architecture/adr/0004-gestao-de-credenciais-e-seguranca.md)
- Qualidade e Testes: [ADR-0005](../../docs/architecture/adr/0005-padroes-de-qualidade-e-testes.md)
- UX e JSON: [ADR-0006](../../docs/architecture/adr/0006-observabilidade-e-ux-cli.md)
- Supersede parcialmente nos caminhos Git: [0009-refactor-cli-git-e-tasks](../0009-refactor-cli-git-e-tasks/spec.md) e [0010-branches-prs-e-detalhes-repo](../0010-branches-prs-e-detalhes-repo/spec.md)
