---
name: cli-git-auth
description: Manual do comando neo git auth para autenticação segura com GitHub e Bitbucket Cloud.
alwaysApply: false
---

# neo git auth
> Gerencia a autenticação e credenciais dos provedores Git armazenadas no Keyring seguro do sistema operacional.

O recurso `neo git auth` gerencia os tokens de acesso para **GitHub** e **Bitbucket Cloud**. O Neo armazena as credenciais de forma segura no cofre do sistema (Keyring nativo: Keychain no macOS, Secret Service no Linux e Credential Manager no Windows) com fallback automático para `~/.config/neo/credentials.toml` com permissões restritas `0600`.

---

## Sintaxe

```bash
neo git auth <ação> [opções]
```

O token de acesso **nunca** é passado por linha de comando ou flag, sendo solicitado com entrada oculta no terminal.

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| `login` | Solicita o token de autenticação em prompt oculto e salva no Keyring | `neo git auth login --provider github` |
| `status` | Exibe o estado de autenticação dos provedores Git sem expor segredos | `neo git auth status` |
| `logout` | Remove as credenciais salvas de um provedor | `neo git auth logout --provider bitbucket --yes` |

---

## Opções

As opções abaixo são específicas do recurso `neo git auth`. Para opções de saída e depuração, consulte as [opções globais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Ações suportadas | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--provider` | `login`, `status`, `logout` | Sim em `login`/`logout` | Nenhum | Provedor Git alvo (`github` ou `bitbucket`). |
| `--yes` | `logout` | Não | `False` | Pula a confirmação interativa ao remover credenciais. |
| `--json` | `status`, `logout` | Não | `False` | Emite a saída estruturada em JSON no `stdout`. |

---

## Exemplos

### 1. Autenticando no GitHub
```bash
neo git auth login --provider github
# Solicita: Personal Access Token (PAT): [entrada oculta]
```

### 2. Autenticando no Bitbucket Cloud (API Token + E-mail)
!!! warning "App Passwords descontinuadas no Bitbucket Cloud"
    O Bitbucket Cloud descontinuou as antigas *App Passwords*. Crie e utilize um **API Token** vinculado ao e-mail da sua conta Atlassian.

```bash
neo git auth login --provider bitbucket
# Solicita: E-mail da conta Atlassian: dev@empresa.com
# Solicita: Bitbucket API Token: [entrada oculta]
```

### 3. Consultando o estado de autenticação
=== "Saída Humana"
    ```bash
    neo git auth status
    ```
    ```text
    ╭─ Provedores Git ──────────────────────────────────────╮
    │ GitHub:    ✓ Autenticado (keyring: gh_pat_***)         │
    │ Bitbucket: ✓ Autenticado (keyring: dev@empresa.com)   │
    ╰───────────────────────────────────────────────────────╯
    ```

=== "Saída Estruturada (`--json`)"
    ```bash
    neo git auth status --json | jq .
    ```
    ```json
    {
      "github": {
        "authenticated": true,
        "source": "keyring"
      },
      "bitbucket": {
        "authenticated": true,
        "source": "keyring",
        "email": "dev@empresa.com"
      }
    }
    ```

### 4. Removendo credenciais em automação
```bash
neo git auth logout --provider github --yes --json
```

---

## Erros comuns e códigos de saída

* **Código 2 (Uso incorreto):**
  * Omitir a flag obrigatória `--provider` em `login` ou `logout`.
  * Informar um provedor inválido (ex.: `--provider gitlab`).
* **Código 3 (Erro de autenticação):**
  * Token fornecido inválido ou revogado na checagem remota da API.
* **Código 1 (Erro genérico):**
  * Usuário respondeu "não" no prompt interativo de confirmação do `logout`.

---

## Veja também
- [neo git status](status.md) — Diagnóstico completo do repositório local e resolução de autenticação
- [neo git config](config.md) — Configurações de preferências gerais do Git
- [Guia: Trocar de Provedor (GitHub ↔ Bitbucket)](../../guias/trocar-provedor.md)
