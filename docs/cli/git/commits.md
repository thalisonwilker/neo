---
name: cli-git-commits
description: Manual do comando neo git commits para listar, buscar e detalhar commits no GitHub e Bitbucket Cloud.
alwaysApply: false
---

# neo git commits
> Lista, pesquisa e inspeciona commits no GitHub e Bitbucket Cloud.

O recurso `neo git commits` permite explorar o histórico de alterações remoto diretamente pelo terminal, com suporte a filtros por mensagem, autor e limite de registros, além de inspeção detalhada de commits por hash SHA.

---

## Sintaxe

```bash
neo git commits <ação> [argumentos] [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| `list` | Lista commits recentes de um repositório com filtro opcional por autor | `neo git commits list --limit 10` |
| `search` | Pesquisa commits cuja mensagem contenha o termo em `--query` | `neo git commits search --query "fix" --limit 5` |
| `show` | Exibe os detalhes completos de um commit específico pelo SHA | `neo git commits show a1b2c3d` |

---

## Opções

As opções abaixo são específicas do recurso `neo git commits`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Ações suportadas | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--query` | `search` | Sim | Nenhum | Termo textual obrigatório para buscar na mensagem do commit. |
| `--author` | `list`, `search` | Não | Nenhum | Filtra commits por nome ou e-mail do autor. |
| `--limit` | `list`, `search` | Não | `20` | Quantidade máxima de commits a retornar. |
| `--repo` | `list`, `search`, `show` | Não | Git local | Slug do repositório (inferido se executado dentro da pasta Git). |
| `--workspace` | `list`, `search`, `show` | Não | *(resolvido)* | Slug do workspace ou organização de destino. |
| `--provider` | `list`, `search`, `show` | Não | *(resolvido)* | Provedor Git: `github` ou `bitbucket`. |
| `--json` | `list`, `search`, `show` | Não | `False` | Emite a resposta em JSON puro no `stdout`. |

---

## Exemplos

### 1. Listando o histórico recente
```bash
neo git commits list --limit 5
```

### 2. Pesquisando commits de correção por autor
=== "Saída Humana"
    ```bash
    neo git commits search --query "fix(auth)" --author "Maria" --limit 5
    ```

=== "Extraindo Hash e Mensagem com `jq`"
    ```bash
    neo git commits search --query "fix" --limit 5 --json | jq '.[] | {hash: .hash[0:7], message: .message | split("\n")[0]}'
    ```

### 3. Inspecionando um commit específico pelo hash
```bash
neo git commits show 7f8c92a
```

---

## Erros comuns e códigos de saída

* **Código 2 (Uso incorreto):**
  * Omitir o hash `sha` obrigatório em `neo git commits show`.
  * Omitir a opção `--query` em `neo git commits search` (para listagem geral sem filtro de texto, use `list`).
* **Código 4 (Não encontrado):**
  * Hash do commit inexistente no repositório remoto (`404`).
  * Repositório alvo não encontrado ou executado fora de uma pasta Git sem `--repo`.
* **Código 3 (Erro de autenticação):**
  * Credencial ausente ou sem permissão de leitura no repositório.

---

## Veja também
- [neo git repo](repo.md) — Consultar e listar repositórios remotos
- [neo git status](status.md) — Verificar a branch atual e contexto de remote
- [Guia: Fluxo Diário (Tasks → Branch → Commit)](../../guias/fluxo-diario.md)

