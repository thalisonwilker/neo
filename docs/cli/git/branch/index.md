---
name: cli-git-branch-index
description: Visão geral das operações de branches locais no Neo.
alwaysApply: false
---

# neo git branch

O comando `neo git branch` gerencia as branches locais do repositório selecionado no contexto. As operações alteram diretamente o estado do repositório Git local, refletindo também para outras ferramentas de linha de comando e IDEs.

---

## Ações Disponíveis

| Comando | Descrição |
|---|---|
| [`neo git branch list`](list.md) | Lista branches locais e destaca a branch ativa. |
| [`neo git branch create`](create.md) | Cria uma nova branch a partir da branch atual. |
| [`neo git branch select`](select.md) | Faz checkout para a branch indicada e atualiza o contexto. |
| [`neo git branch delete`](delete.md) | Remove uma branch local de forma segura (sem exclusão forçada). |

---

## Opções Globais Aplicáveis

Todas as ações suportam `--json` para automações e `--help` para obter ajuda interativa no terminal.
Consulte a documentação específica de cada subcomando nos links acima.

