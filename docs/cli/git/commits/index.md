---
name: cli-git-commits-index
description: Visão geral de consulta e inspeção de commits remotos no GitHub e Bitbucket Cloud.
alwaysApply: false
---

# neo git commits

O comando `neo git commits` permite explorar o histórico de alterações remoto diretamente pelo terminal, com suporte a filtros por mensagem, autor e limite de registros, além de inspeção detalhada de commits por hash SHA.

---

## Ações Disponíveis

| Comando | Descrição |
|---|---|
| [`neo git commits list`](list.md) | Lista commits recentes do repositório remoto com filtros opcionais. |
| [`neo git commits search`](search.md) | Pesquisa commits por termo ou palavra-chave na mensagem. |
| [`neo git commits show`](show.md) | Inspeciona os detalhes completos de um commit específico pelo hash SHA. |

---

## Opções Comuns

Todas as ações operam sobre o repositório e provedor resolvidos no contexto ativo, aceitando sobrescrita via `--repo`, `--workspace` e `--provider`, além da flag `--json` para automações.
Consulte a documentação detalhada de cada ação nos links acima.

