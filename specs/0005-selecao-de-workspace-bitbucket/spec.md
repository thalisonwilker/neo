---
name: spec
description: Contrato da feature de seleção e gestão de workspace do Bitbucket na CLI Neo.
alwaysApply: true
---

# Spec — Seleção e Gestão de Workspace do Bitbucket

> **Fonte da verdade.** Status: em review
> Permite listar, inspecionar e selecionar o workspace ativo do Bitbucket de forma interativa ou via flag, persistindo a escolha em configuração e integrando-a com os comandos `neo repo` e `neo commits`.

## Resumo
A CLI Neo permitirá ao usuário listar seus workspaces acessíveis no Bitbucket Cloud, selecionar um workspace ativo (interativamente ou diretamente por slug) para ser salvo nas configurações locais (`config.toml`), e usar essa preferência como workspace padrão em todas as operações de repositório e commit sem a necessidade de passar `--workspace` a cada comando.

---

## Critérios de Aceite

### AC-1: Listar workspaces da conta (`neo workspace list`)
- **Dado** o usuário autenticado no Bitbucket Cloud;
- **Quando** executa `neo workspace list`;
- **Então** exibe uma tabela formatada com Rich contendo todos os workspaces disponíveis (Nome, Slug, Tipo/Permissão), destacando com um badge `[Ativo]` o workspace atualmente configurado;
- **E** em modo global `--json`, retorna uma lista estruturada de objetos `[{"name": "...", "slug": "...", "is_admin": bool, "is_active": bool}]`.

### AC-2: Exibir workspace ativo (`neo workspace current`)
- **Dado** o usuário com ou sem workspace configurado em arquivo local;
- **Quando** executa `neo workspace current`;
- **Então** exibe um painel indicando o workspace ativo e a sua origem (`configuração local` ou `detectado automaticamente via API`);
- **E** em modo `--json`, emite `{"workspace": "<slug>", "source": "config" | "api_auto"}`.

### AC-3: Seleção direta de workspace (`neo workspace select --slug <slug>` ou `neo workspace set <slug>`)
- **Dado** um slug de workspace válido pertencente à conta autenticada;
- **Quando** o usuário executa `neo workspace select --slug <slug>` (ou `neo workspace set <slug>`);
- **Então** valida a existência do workspace na API do Bitbucket, persiste a chave `default_workspace = "<slug>"` em `~/.config/neo/config.toml` e exibe mensagem de sucesso com Rich;
- **E** caso o slug informado não pertença à conta, emite mensagem de erro e código de saída 1 sem alterar a configuração.

### AC-4: Seleção interativa no terminal (`neo workspace select`)
- **Dado** o terminal em modo interativo e sem a flag `--slug`;
- **Quando** o usuário executa `neo workspace select`;
- **Então** o Neo busca os workspaces disponíveis, exibe um menu numerado com os slugs e solicita a escolha via prompt interativo, persistindo a opção selecionada;
- **E** se o modo `--json` estiver ativo sem `--slug`, emite erro orientando o uso obrigatório da flag `--slug`.

### AC-5: Precedência de workspace nos comandos de repositórios e commits
- **Dado** um workspace salvo em `config.toml` (ex: `acme_corp`);
- **Quando** o usuário executa comandos como `neo repo list`, `neo repo search`, `neo repo clone`, `neo repo create` ou `neo commits search`:
  - Se a flag `--workspace <ws>` for fornecida explicitamente, ela tem precedência máxima;
  - Se `--workspace` for omitida, utiliza automaticamente o workspace salvo em `config.toml`;
  - Se nenhum workspace estiver salvo em `config.toml`, mantém o fallback automático de consultar o primeiro workspace retornado pela API.

### AC-6: Tratamento de ausência de credenciais
- **Dado** o Neo sem credenciais configuradas para o Bitbucket;
- **Quando** o usuário executa qualquer subcomando de `neo workspace`;
- **Então** encerra com código de saída 1 e emite mensagem clara instruindo a configuração prévia via `neo config auth set bitbucket`.

---

## Matriz de Decisão: Resolução de Workspace

| Flag `--workspace` | Configurado em `config.toml` | API Bitbucket | Workspace Utilizado | AC |
|---|---|---|---|---|
| Informada (`custom-ws`) | Qualquer | Qualquer | `custom-ws` (prioridade máxima) | AC-5 |
| Omitida | Configurado (`meu-ws`) | Não precisa chamar `/user/workspaces` | `meu-ws` (preferência persistida) | AC-5 |
| Omitida | Não configurado (`None`) | Retorna lista (`auto-ws`) | `auto-ws` (fallback automático) | AC-2, AC-5 |
| Omitida | Não configurado (`None`) | Lista vazia ou erro | Exceção `BitbucketNotFoundError` amigável | AC-6 |

---

## Casos de Borda e Erros
- **Workspace não encontrado:** Usuário tenta selecionar um slug que não existe ou ao qual não tem acesso $\rightarrow$ emite erro explicativo com status 404 e código 1.
- **Falha de I/O ao salvar `config.toml`:** Diretório sem permissão $\rightarrow$ captura amigável e saída informativa em `stderr`.
- **Modo headless/JSON sem `--slug`:** Interatividade bloqueada $\rightarrow$ mensagem orientando `--slug <nome>`.

---

## Fora de Escopo
- Criar ou excluir workspaces no Bitbucket Cloud via CLI (administração restrita ao console web).
- Gerenciar convites ou membros de workspaces.

---

## Rastreabilidade
- Arquitetura: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md) (Monolito Modular e ACL).
- Configuração: `src/neo/config.py`.
- Integração: `src/neo/integrations/bitbucket.py`.
- Testes: `tests/unit/test_workspace.py` e `tests/e2e/test_workspace_commands.py`.
