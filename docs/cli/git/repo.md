---
name: cli-git-repo
description: Gerenciamento de repositórios locais e remotos com neo git repo.
alwaysApply: false
---

# neo git repo

O Neo registra repositórios locais criados ou selecionados e mantém um deles como contexto, mesmo quando o terminal está em outro diretório. Selecionar um repositório não muda o diretório do terminal.

| Comando | Resultado |
|---|---|
| `neo git repo list` | Lista repositórios locais registrados e destaca o selecionado. |
| `neo git repo select <caminho>` | Registra e seleciona um repositório Git local existente. |
| `neo git repo create <nome> --path <caminho>` | Cria o repositório local e no provedor e envia o commit inicial. |
| `neo git repo edit --description <texto>` | Atualiza a descrição do repositório no provedor. |
| `neo git repo remote-list` | Lista repositórios remotos no workspace resolvido. |
| `neo git repo search --query <termo>` | Pesquisa repositórios remotos. |
| `neo git repo show` | Exibe detalhes do repositório remoto do contexto. |

```bash
neo git repo select /projetos/minha-api
neo git repo list --json
neo git repo create minha-api --path /projetos/minha-api
neo git repo create site-publico --path /projetos/site-publico --public
neo git repo edit --description "Descrição atualizada"
neo git repo remote-list --limit 10
neo git repo search --query "api"
neo git repo show --repo minha-api
```

A criação remota é **privada por padrão**. Em um repositório vazio, o Neo cria `README.md` e `AGENTS.md`, faz o commit inicial, configura `origin` e envia a branch. A criação recusa caminhos existentes. Se uma etapa remota falhar, o diretório local é preservado e o erro informa a etapa e se o repositório remoto foi criado. Não há remoção automática de recursos criados.

Os comandos remotos requerem credenciais e permissões no provedor. Se nenhum repositório estiver selecionado, o Neo pode detectar o repositório do diretório atual. Consulte [configuração](config.md) e [branches](branch.md).
