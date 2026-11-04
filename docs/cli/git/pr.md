---
name: cli-git-pr
description: Listar, abrir, aprovar, recusar e pesquisar pull requests no GitHub ou Bitbucket Cloud.
alwaysApply: false
---

# neo git pr

Gerencie pull requests no GitHub ou Bitbucket Cloud a partir do repositório selecionado. O Neo utiliza o provedor, workspace e `origin` resolvidos para o contexto atual; `--provider`, `--workspace` e `--repo` permitem indicar o destino explicitamente.

## Listar pull requests abertos

```bash
neo git pr
neo git pr --json
neo git pr --repo minha-api --workspace minha-organizacao --provider github
```

Sem subcomando, o Neo lista os pull requests abertos com ID, título, estado, branches de origem e destino e URL. A listagem percorre as páginas do provedor. Se não houver resultados, mostra uma mensagem; com `--json`, retorna uma lista vazia (`[]`). Para ver os subcomandos, use `neo git pr --help`.

Cada item JSON contém `id`, `title`, `state`, `source`, `destination` e `url`. As opções `--repo`, `--workspace` e `--provider` substituem a resolução automática para essa consulta.

## Abrir um pull request

```bash
neo git pr open
neo git pr open --base main --title "Adicionar busca" --description "Implementa a busca de registros."
```

O comando usa a branch local atual como origem. Se `--base` for omitido, apresenta as branches remotas para seleção; título e descrição omitidos são solicitados. A branch de origem precisa existir no provedor: o comando não faz push automaticamente.

Para automação, forneça as opções e use `--json`:

```bash
neo git pr open --base main --title "Adicionar busca" --description "Implementa a busca." --json
```

## Aprovar ou recusar

```bash
neo git pr approve 42 --message "Revisado e aprovado"
neo git pr decline 42
neo git pr decline 42 --yes --json
```

A mensagem de aprovação é solicitada se omitida. No GitHub, ela acompanha a revisão; no Bitbucket, o Neo publica um comentário antes de registrar a aprovação. Caso o comentário seja publicado e a aprovação falhe, o Neo informa a falha parcial e preserva o comentário. Se o comentário falhar, a aprovação não é enviada.

`decline` pede confirmação ou aceita `--yes`; ele fecha ou recusa o pull request sem fazer merge. Em modo JSON, inclua `--message` na aprovação e `--yes` na recusa.

## Pesquisar

```bash
neo git pr search 42
neo git pr search "busca" --json
```

Um termo numérico busca o ID exato; texto busca por trecho do título sem diferenciar maiúsculas de minúsculas. A pesquisa inclui pull requests abertos, recusados ou fechados e mesclados. Os resultados apresentam ID, título, estado, branches e URL.

Consulte [repositórios](repo.md), [branches locais](branch.md) e [configuração Git](config.md).
