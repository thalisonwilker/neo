---
name: spec
description: Contrato da feature 0003-modulo-bitbucket (comandos neo repo e neo commits).
alwaysApply: true
---

# Spec — 0003-modulo-bitbucket

> **Fonte da verdade.** Status: aprovado
> Contrato de entrega da integração com Bitbucket Cloud: listagem, busca, criação e clonagem de repositórios (`neo repo`) e consulta a commits (`neo commits`).

## Resumo
O Neo passará a permitir que desenvolvedores consultem, pesquisem, clonem e criem repositórios no Bitbucket diretamente pela linha de comando (`neo repo`), bem como busquem commits filtrados por autor e mensagem (`neo commits search`), tanto no modo interativo Rich quanto em formato JSON (`--json`).

## Critérios de aceite

### AC-1: Listagem de repositórios (`neo repo list`)
- **Dado** o usuário com credenciais do Bitbucket configuradas
- **Quando** executar `neo repo list` (com workspace configurado ou passado via `--workspace`)
- **Então** a CLI consulta a API do Bitbucket Cloud e exibe os repositórios em tabela Rich contendo Nome, Slug, Visibilidade, Branch padrão e Data de atualização, com exit code 0.
- **Quando** a flag global `--json` for fornecida
- **Então** a saída no `stdout` é uma lista de objetos JSON contendo os metadados dos repositórios.

### AC-2: Busca de repositórios (`neo repo search <termo>`)
- **Dado** repositórios existentes no workspace do Bitbucket
- **Quando** o usuário executar `neo repo search <termo>`
- **Então** a CLI busca os repositórios cujo nome, slug ou descrição contenha o termo especificado e exibe os resultados correspondentes em Rich ou JSON.
- **Quando** nenhum repositório for encontrado
- **Então** a CLI exibe aviso informativo ("Nenhum repositório encontrado para o termo...") com exit code 0.

### AC-3: Clonagem de repositório (`neo repo clone <slug>`)
- **Dado** um repositório existente no Bitbucket
- **Quando** o usuário executar `neo repo clone <slug> [--ssh | --https]`
- **Então** a CLI resolve a URL de clone do repositório (por padrão preferindo SSH, ou HTTPS se explicitado) e executa o clone para a máquina local com feedback no terminal e exit code 0.
- **Quando** o repositório não for encontrado
- **Então** a CLI exibe erro amigável de não encontrado e encerra com exit code 1.

### AC-4: Criação de repositório com confirmação (`neo repo create <nome>`)
- **Dado** o desejo de criar um novo repositório no Bitbucket
- **Quando** o usuário executar `neo repo create <nome> [--private/--public] [--description "..."]`
- **Então** a CLI solicita confirmação interativa antes de criar o recurso remoto, a menos que a flag `--yes` / `-y` seja informada.
- **Quando** confirmado
- **Então** o repositório é criado no Bitbucket e os links de clone e página web são exibidos ao usuário com exit code 0.

### AC-5: Busca e histórico de commits (`neo commits search`)
- **Dado** um repositório no Bitbucket (especificado via `--repo <slug>` ou inferido do git remote local)
- **Quando** o usuário executar `neo commits search [--author <nome>] [--query <termo>] [--limit N]`
- **Então** a CLI consulta a API do Bitbucket e exibe a lista de commits contendo Hash reduzido (7 chars), Autor, Data formatada e Mensagem resumida em tabela Rich ou JSON.

### AC-6: Falha amigável por ausência de credenciais
- **Dado** que o token do Bitbucket não foi configurado
- **Quando** o usuário executar qualquer comando `neo repo` ou `neo commits`
- **Então** a CLI intercepta a ausência de credenciais e instrui o usuário com a mensagem: "Credenciais do Bitbucket não configuradas. Execute `neo config auth set bitbucket`.", encerrando com exit code 1.

## Matriz de decisão (Clonagem de Repositório)

| Flags de Protocolo | Clone URL SSH disponível | Clone URL HTTPS disponível | Protocolo Selecionado | AC |
|---|---|---|---|---|
| `--ssh` | Sim | Sim | SSH | AC-3 |
| `--https` | Sim | Sim | HTTPS | AC-3 |
| Nenhuma (default) | Sim | Sim | SSH (padrão) | AC-3 |
| Nenhuma (default) | Não | Sim | HTTPS (fallback) | AC-3 |

## Casos de borda e erros
- **Rate limiting da API (429):** Exibir aviso de limite de requisições excedido com tempo de espera sugerido.
- **Token inválido ou expirado (401/403):** Exibir mensagem de erro de autenticação instruindo a atualizar o token via `neo config auth set bitbucket`.
- **Workspace não especificado:** Se não houver workspace configurado nem passado via flag, buscar o workspace padrão do usuário autenticado via `/2.0/user/workspaces`.

## Fora de escopo
- Edição de configurações de repositório (pipelines, permissões de branch).
- Criação e aprovação de pull requests (previsto na expansão da Onda 1).

## Rastreabilidade
- Roadmap: Onda 1, Item 2
- ADRs relacionados:
  - [ADR-0002](../../docs/architecture/adr/0002-tech-stack-core.md)
  - [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md)
  - [ADR-0006](../../docs/architecture/adr/0006-observabilidade-e-ux-cli.md)
