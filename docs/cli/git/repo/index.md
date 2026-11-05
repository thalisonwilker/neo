---
name: cli-git-repo-index
description: Visão geral do gerenciamento de repositórios locais e remotos no Neo.
alwaysApply: false
---

# neo git repo

O comando `neo git repo` gerencia repositórios Git locais registrados e remotos nos provedores GitHub e Bitbucket Cloud. O Neo mantém um repositório como contexto ativo, permitindo executar comandos sem precisar alterar o diretório atual do terminal.

---

## Ações Disponíveis

| Comando | Descrição |
|---|---|
| [`neo git repo list`](list.md) | Lista repositórios remotos no workspace do provedor configurado. |
| [`neo git repo remote-list`](remote-list.md) | Alias de compatibilidade para `neo git repo list`. |
| [`neo git repo local-list`](local-list.md) | Lista repositórios locais registrados e destaca o contexto ativo. |
| [`neo git repo select`](select.md) | Registra e seleciona um repositório local existente no contexto. |
| [`neo git repo search`](search.md) | Pesquisa repositórios remotos por termo ou palavra-chave. |
| [`neo git repo show`](show.md) | Exibe detalhes e metadados de um repositório remoto. |
| [`neo git repo create`](create.md) | Cria um novo repositório local e remoto privado com commit inicial. |
| [`neo git repo edit`](edit.md) | Atualiza a descrição do repositório remoto no provedor. |

---

## Opções Globais Aplicáveis

Todas as ações suportam:
- `--json`: Retorna a saída em formato JSON estruturado, ideal para automações e pipelines.
- `--help`: Exibe a ajuda detalhada do subcomando no terminal.

Consulte a documentação específica de cada ação nos links acima.
