---
name: cli-git-repo
description: Manual do comando neo git repo para listar, pesquisar e detalhar repositórios no GitHub e Bitbucket Cloud.
alwaysApply: false
---

# neo git repo
> Lista, pesquisa e exibe detalhes de repositórios no GitHub e Bitbucket Cloud.

O recurso `neo git repo` permite explorar e inspecionar repositórios remotos acessíveis pela conta autenticada, com paginação automática e detecção inteligente do repositório local.

---

## Sintaxe

```bash
neo git repo <ação> [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| `list` | Lista repositórios disponíveis no workspace resolvido | `neo git repo list --limit 15` |
| `search` | Pesquisa repositórios por nome, slug ou descrição via `--query` | `neo git repo search --query "api"` |
| `show` | Exibe os detalhes completos e URLs de clone de um repositório | `neo git repo show --repo core-api` |
| `clone` 🚧 | *(Planejado)* Clonagem assistida de repositório remoto | *(Em desenvolvimento)* |
| `create` 🚧 | *(Planejado)* Criação de novo repositório remoto | *(Em desenvolvimento)* |

---

## Opções

As opções abaixo são específicas do recurso `neo git repo`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Ações suportadas | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--query` | `search` | Sim | Nenhum | Termo textual obrigatório para busca no nome ou descrição. |
| `--repo` | `show` | Não | Git local | Slug do repositório (inferido automaticamente se executado em uma pasta Git). |
| `--workspace` | `list`, `search`, `show` | Não | *(resolvido)* | Slug do workspace ou organização de destino. |
| `--provider` | `list`, `search`, `show` | Não | *(resolvido)* | Provedor Git: `github` ou `bitbucket`. |
| `--limit` | `list`, `search` | Não | Nenhum | Quantidade máxima de repositórios retornados. |
| `--json` | `list`, `search`, `show` | Não | `False` | Emite a resposta em JSON puro no `stdout`. |

---

## Exemplos

### 1. Listando repositórios do workspace ativo
```bash
neo git repo list --limit 10
```

### 2. Pesquisando repositórios por palavra-chave
=== "Saída Humana"
    ```bash
    neo git repo search --query "service"
    ```

=== "Extraindo Slugs e URLs SSH com `jq`"
    ```bash
    neo git repo search --query "service" --json | jq '.[] | {name, slug, ssh: .clone_links[0].href}'
    ```

### 3. Exibindo detalhes de um repositório
```bash
# Dentro do repositório local (slug inferido automaticamente)
neo git repo show

# Consultando repositório específico explicitamente
neo git repo show --repo payment-service --workspace acme-inc
```

---

## Erros comuns e códigos de saída

* **Código 2 (Uso incorreto):**
  * Omitir a flag obrigatória `--query` no comando `search`.
  * Tentar executar `neo git repo clone` ou `create` (que emitem orientação do backlog planejado).
* **Código 4 (Não encontrado):**
  * Repositório ou workspace inexistente no provedor remoto (`404`).
  * Executar `neo git repo show` fora de uma pasta Git sem informar `--repo`.
* **Código 3 (Erro de autenticação):**
  * Token não configurado ou sem permissão de leitura nos repositórios.

---

## Veja também
- [neo git workspace](workspace.md) — Gerenciar o workspace ativo
- [neo git commits](commits.md) — Inspecionar histórico e commits do repositório
- [neo git repo planejado](planejado.md) — Roadmap de ações de criação e clonagem

