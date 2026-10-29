---
name: cli-git-workspace
description: Manual do comando neo git workspace para listar, selecionar e inspecionar workspaces no GitHub e Bitbucket Cloud.
alwaysApply: false
---

# neo git workspace
> Lista, seleciona e exibe detalhes do workspace ativo no GitHub ou Bitbucket Cloud.

No Neo, o conceito de **Workspace** unifica o escopo organizacional dos provedores:
* No **Bitbucket Cloud**: corresponde a um *Workspace*.
* No **GitHub**: corresponde a uma *Organização* ou à *conta pessoal do usuário*.

---

## Sintaxe

```bash
neo git workspace <ação> [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| `list` | Lista todos os workspaces disponíveis para a conta autenticada | `neo git workspace list --provider github` |
| `select` | Seleciona o workspace ativo de forma interativa ou via flag | `neo git workspace select --workspace acme-inc` |
| `show` | Exibe os detalhes e metadados do workspace ativo ou especificado | `neo git workspace show` |

---

## Opções

As opções abaixo são específicas do recurso `neo git workspace`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Ações suportadas | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--workspace` | `select`, `show` | Não | Atual | Slug do workspace a selecionar ou inspecionar. |
| `--provider` | `list`, `select`, `show` | Não | *(resolvido)* | Provedor Git: `github` ou `bitbucket`. |
| `--limit` | `list` | Não | Nenhum | Quantidade máxima de workspaces exibidos na listagem. |
| `--json` | `list`, `select`, `show` | Não | `False` | Emite a resposta em JSON puro no `stdout`. |

---

## Exemplos

### 1. Listando workspaces acessíveis
```bash
neo git workspace list
```

### 2. Selecionando o workspace ativo
=== "Seleção Interativa (via menu no terminal)"
    ```bash
    neo git workspace select
    # Exibe menu navegável com setas e enter
    ```

=== "Definição Direta via Flag"
    ```bash
    neo git workspace select --workspace acme-corp --provider bitbucket
    ```

### 3. Inspecionando o workspace ativo
=== "Saída Visual"
    ```bash
    neo git workspace show
    ```

=== "Saída Estruturada (`--json`)"
    ```bash
    neo git workspace show --json | jq .
    ```
    ```json
    {
      "name": "Acme Corporation",
      "slug": "acme-corp",
      "is_admin": true,
      "provider": "github"
    }
    ```

---

## Erros comuns e códigos de saída

* **Código 3 (Erro de autenticação):** Token não configurado para o provedor ou permissão insuficiente para listar workspaces.
* **Código 4 (Não encontrado):** O slug informado em `--workspace` não existe ou não pertence à conta autenticada.
* **Código 2 (Uso incorreto):** Tentar invocar comandos legados descontinuados (consulte o [Guia de Migração](../../migration.md)).

---

## Veja também
- [neo git repo](repo.md) — Listar e buscar repositórios no workspace ativo
- [neo git config](config.md) — Definir o workspace padrão no `config.toml`
- [neo git status](status.md) — Verificar o workspace resolvido no diretório atual
