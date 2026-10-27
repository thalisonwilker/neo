---
name: spec
description: Contrato da feature do módulo GitHub e suporte a múltiplos provedores Git na CLI Neo.
alwaysApply: true
---

# Spec — Módulo GitHub e Multi-provedor Git

> **Fonte da verdade.** Status: em review
> Permite autenticar no GitHub, configurar o provedor padrão, auto-detectar o provedor pelo remote git local ou forçar via flag, e executar comandos de repositórios, commits e workspaces de forma unificada.

## Resumo
A CLI Neo passará a suportar o **GitHub** como provedor Git completo ao lado do **Bitbucket**, compartilhando os mesmos comandos de interface (`neo repo`, `neo commits`, `neo workspace`) com seleção inteligente por repositório local, configuração persistida de preferência e flag explícita.

---

## Critérios de Aceite

### AC-1: Autenticação do GitHub (`neo config auth set github`)
- **Dado** o usuário com um Personal Access Token do GitHub (`ghp_...`);
- **Quando** executa `neo config auth set github` (interativo ou via `--token`);
- **Então** o token é validado e armazenado com segurança no Keyring do SO (com fallback 0600 em `config.toml`);
- **E** a variável de ambiente `GITHUB_TOKEN` é reconhecida com maior precedência sobre o Keyring;
- **E** `neo config show` passa a listar o status e token mascarado do serviço `github`.

### AC-2: Gestão do Provedor Padrão (`neo config set-provider`)
- **Dado** os serviços suportados (`bitbucket` e `github`);
- **Quando** o usuário executa `neo config set-provider <bitbucket|github>`;
- **Então** persiste `default_provider = "<provedor>"` no arquivo `~/.config/neo/config.toml` e exibe mensagem de confirmação;
- **E** `neo config get-provider` exibe o provedor ativo atualmente;
- **E** se fornecido provedor inválido, emite erro com código de saída 1.

### AC-3: Auto-detecção inteligente de provedor via Git local
- **Dado** o usuário executando comandos no diretório de um repositório git local;
- **Quando** executa qualquer comando de `repo` ou `commits` sem a flag `--provider`:
  - Se a URL do remote `origin` apontar para `github.com`, resolve automaticamente para o provedor `github`;
  - Se a URL do remote `origin` apontar para `bitbucket.org`, resolve automaticamente para o provedor `bitbucket`;
  - Se o diretório não tiver remote reconhecido, utiliza o `default_provider` configurado (ou fallback para `bitbucket`).

### AC-4: Forçar provedor via flag explícita (`--provider` / `-p`)
- **Dado** qualquer comando de `neo repo`, `neo commits` ou `neo workspace`;
- **Quando** o usuário passa a opção `--provider github` (ou `-p github`) ou `--provider bitbucket` (ou `-p bitbucket`);
- **Então** o comando executa exclusivamente contra a API do provedor indicado, ignorando a auto-detecção local e a configuração padrão.

### AC-5: Operações de Repositórios e Commits no GitHub
- **Dado** o provedor GitHub ativo ou selecionado;
- **Quando** o usuário executa:
  - `neo repo list [--workspace <org_ou_user>]`: lista repositórios da conta autenticada ou da organização especificada;
  - `neo repo search <query>`: pesquisa repositórios acessíveis no GitHub;
  - `neo repo clone <slug> [--ssh|--https]`: resolve URL do GitHub e clona via git;
  - `neo repo create <name> [--private|--public]`: cria repositório no GitHub sob a conta ou organização ativa;
  - `neo commits search [--repo <slug>]`: busca histórico de commits no repositório do GitHub.

### AC-6: Gestão de Organizações/Workspaces no GitHub (`neo workspace`)
- **Dado** o provedor GitHub ativo;
- **Quando** executa `neo workspace list`:
  - Retorna o usuário pessoal autenticado e todas as organizações às quais o usuário pertence;
  - `neo workspace set <org>` persiste a organização padrão do GitHub em `config.toml`.

### AC-7: Tratamento de ausência de credenciais e erros
- **Dado** o provedor GitHub selecionado sem credencial configurada;
- **Quando** o usuário executa um comando dependente da API do GitHub;
- **Então** encerra com código 1 e mensagem amigável instruindo: `Credenciais do GitHub não configuradas. Execute neo config auth set github`.

---

## Matriz de Decisão: Resolução de Provedor Git

| Flag `--provider` | Remote Git Local | Config `default_provider` | Provedor Escolhido | AC |
|---|---|---|---|---|
| Informada (`github`) | Qualquer | Qualquer | `github` (prioridade máxima) | AC-4 |
| Informada (`bitbucket`) | Qualquer | Qualquer | `bitbucket` (prioridade máxima) | AC-4 |
| Omitida | `origin` aponta para `github.com` | Qualquer | `github` (auto-detecção) | AC-3 |
| Omitida | `origin` aponta para `bitbucket.org` | Qualquer | `bitbucket` (auto-detecção) | AC-3 |
| Omitida | Sem remote / outro host | Configurado (`github`) | `github` (preferência salva) | AC-2 |
| Omitida | Sem remote / outro host | Configurado (`bitbucket`) | `bitbucket` (preferência salva) | AC-2 |
| Omitida | Sem remote / outro host | Não configurado | `bitbucket` (fallback padrão) | AC-3 |

---

## Casos de Borda e Erros
- **Token sem escopo `repo`:** GitHub retorna 404 ao tentar acessar ou listar repositórios privados $\rightarrow$ emitir erro claro orientando permissões do token.
- **Rate Limit da API do GitHub (403):** Capturado e traduzido para mensagem amigável de limite atingido.
- **Organização inexistente no GitHub:** Retorno 404 traduzido para mensagem amigável sem stack trace.

---

## Fora de Escopo
- Autenticação via GitHub OAuth App com servidor de callback local.
- Gerenciamento de pull requests, releases e GitHub Actions (foco em repositórios, commits e workspaces).

---

## Rastreabilidade
- Arquitetura: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md).
- Product: `./product.md`
- Design: `./design.md`
- Domínio: `./domain.md`
