---
name: cli-git-config
description: Manual do comando neo git config para gerenciamento de preferências na seção [git] de config.toml.
alwaysApply: false
---

# neo git config
> Gerencia preferências do módulo Git na seção [git] do arquivo de configuração do usuário.

O recurso `neo git config` define preferências de trabalho persistidas em `~/.config/neo/config.toml` sob a seção `[git]`. Chaves permitidas: `provider`, `workspace`, `default-branch`, `branch-pattern` e `commit-format`.

!!! info "Segurança: `token` não é chave de configuração"
    A chave `token` não existe em `neo git config` e é rejeitada com código `2`. Credenciais são tratadas com segurança via [`neo git auth`](auth.md).

---

## Sintaxe

```bash
neo git config <ação> [chave] [valor] [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| `set` | Define o valor de uma chave na seção `[git]` do `config.toml` | `neo git config set provider github` |
| `get` | Exibe o valor efetivo e a camada de origem de uma chave de configuração | `neo git config get workspace` |
| `list` | Lista todas as chaves da seção `[git]` com seus valores e origens | `neo git config list` |
| `unset` | Remove uma chave personalizada, restaurando o valor padrão | `neo git config unset default-branch` |

---

## Opções

As opções abaixo são específicas do recurso `neo git config`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Ações suportadas | Obrigatório | Descrição |
|---|---|---|---|
| `--json` | `get`, `list`, `set`, `unset` | Não | Emite o resultado em JSON estruturado no `stdout`. |

---

## Chaves Suportadas

| Chave | Valores aceitos | Padrão | Descrição |
|---|---|---|---|
| `provider` | `github` \| `bitbucket` | *(automático)* | Provedor Git padrão fora de repositórios locais. |
| `workspace` | `<slug>` | *(automático)* | Workspace ou organização padrão. |
| `default-branch` | Texto (ex.: `main`, `master`) | `main` | Nome da branch principal padrão para operações. |
| `branch-pattern` | Ex.: `{type}/{id}-{slug}` | `{type}/{id}-{slug}` | Padrão sugerido para nomenclatura de branches. |
| `commit-format` | Ex.: `{type}: {message}` | `{type}: {message}` | Formato sugerido para mensagens de commit. |

---

## Exemplos

### 1. Definindo o provedor e workspace padrão
```bash
neo git config set provider github
neo git config set workspace acme-inc
```

### 2. Consultando uma chave com origem da resolução
=== "Saída Humana"
    ```bash
    neo git config get provider
    ```
    ```text
    provider: github (origem: config)
    ```

=== "Saída em JSON (`--json`)"
    ```bash
    neo git config get provider --json | jq .
    ```
    ```json
    {
      "key": "provider",
      "value": "github",
      "source": "config"
    }
    ```

### 3. Listando todas as configurações ativas
```bash
neo git config list
```

### 4. Removendo uma chave personalizada
```bash
neo git config unset default-branch
```

---

## Erros comuns e códigos de saída

* **Código 2 (Uso incorreto):**
  * Tentar definir uma chave inexistente ou proibida (ex.: `neo git config set chave_invalida xyz`).
  * Fornecer um valor inválido para `provider` (diferente de `github` ou `bitbucket`).
  * Omitir a chave ou o valor obrigatório no comando `set`.
* **Código 4 (Não encontrado):**
  * Consultar via `get` uma chave não definida e sem valor padrão.

---

## Veja também
- [neo git auth](auth.md) — Autenticação segura de provedores Git
- [neo git status](status.md) — Diagnóstico de resolução de contexto
- [neo config show](../index.md#qual-comando-usar-homonimos) — Visão agregada de configurações do Neo
