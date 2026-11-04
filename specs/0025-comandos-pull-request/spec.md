---
name: spec
description: Contrato dos comandos de criação, aprovação, recusa e pesquisa de pull requests.
alwaysApply: true
---

# Spec — Comandos de Pull Request

> **Fonte da verdade.** Status: implementado · Tier: pequeno

## Resumo

Adicionar `neo git pr open`, `approve`, `decline` e `search` para GitHub e Bitbucket, aproveitando o repositório e o provedor resolvidos pelo Neo. Esta spec detalha e substitui o escopo correspondente de PR da spec 0010.

## Critérios de aceite

### AC-1: Abrir pull request
- **Dado** um repositório Git selecionado com branch atual e provedor configurado, **quando** o usuário executa `neo git pr open [--base <branch>] [--title <título>] [--description <descrição>]`, **então** utiliza a branch local atual como origem, solicita interativamente os valores omitidos e cria o pull request no provedor.
- **E** a seleção de destino apresenta as branches remotas do repositório quando `--base` é omitido; `--base` seleciona diretamente uma branch remota existente. Título não vazio e descrição são solicitados quando omitidos.
- **E** o Neo informa ID e URL; aceita `--json` com todas as opções fornecidas. Sem branch local, sem destino válido ou com origem ausente no provedor, falha sem publicar a branch e informa como corrigir.

### AC-2: Aprovar pull request
- **Dado** o ID de um pull request e mensagem não vazia, **quando** o usuário executa `neo git pr approve <id> --message <mensagem>`, **então** o provedor registra a aprovação e a mensagem; a mensagem omitida é solicitada interativamente.
- **E** no Bitbucket o Neo publica o comentário antes de aprovar; se o comentário for publicado e a aprovação falhar, informa explicitamente que o comentário foi publicado, não remove o comentário e retorna erro. Se o comentário falhar, não envia a aprovação.
- **E** no GitHub a aprovação e a mensagem são enviadas na mesma revisão. Os comandos não fazem merge.

### AC-3: Recusar pull request
- **Dado** o ID de um pull request aberto, **quando** o usuário executa `neo git pr decline <id> [--yes]`, **então** o provedor fecha ou recusa o pull request sem fazer merge, após confirmação ou com `--yes`.

### AC-4: Pesquisar pull request
- **Dado** um ID ou trecho do título, **quando** o usuário executa `neo git pr search <termo> [--json]`, **então** pesquisa no repositório selecionado por ID exato numérico ou título sem distinção entre maiúsculas e minúsculas, incluindo pull requests abertos, recusados/fechados e mesclados.
- **E** apresenta ID, título, estado, branches e URL; pesquisa sem resultado retorna lista vazia.

### AC-5: Listar pull requests abertos
- **Dado** o repositório resolvido, **quando** o usuário executa `neo git pr` sem subcomando, **então** lista os pull requests abertos no provedor, com ID, título, estado, branches e URL.
- **E** `--json` retorna uma lista estruturada, vazia quando não houver pull requests abertos; `--repo`, `--workspace` e `--provider` permitem indicar o destino. `neo git pr --help` mantém a ajuda dos subcomandos.

## Regras comuns e erros
- Os comandos usam repositório selecionado, `origin` e resolução existente de provedor e workspace; `--repo`, `--workspace` e `--provider` permitem selecionar explicitamente o destino.
- `--json` funciona nas leituras e mutações; em modo JSON, dados que normalmente exigem prompt devem ser informados, e `decline` exige `--yes`.
- Não expor credenciais. Erros de autenticação, recurso inexistente, falha de rede ou permissão são informados sem repetir automaticamente operações de escrita.

## Fora de escopo
- Fazer merge ou publicar automaticamente uma branch local.

## Rastreabilidade
- [Backlog Git](../0010-branches-prs-e-detalhes-repo/spec.md)
