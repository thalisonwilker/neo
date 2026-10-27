---
name: spec
description: Contrato da feature 0002-fundacao-cli-e-configuracao (Typer CLI, Rich, Keyring, config).
alwaysApply: true
---

# Spec — 0002-fundacao-cli-e-configuracao

> **Fonte da verdade.** Status: aprovado
> Contrato de entrega da fundação do Neo: CLI base em Typer, saída visual em Rich, flag global `--json`, e gerenciador de configuração e credenciais com Keyring do SO.

## Resumo
O Neo passará a ser executável localmente via comando de terminal `neo`, oferecendo ajuda contextual (`--help`), identificação de versão (`--version`), saída formatada em Rich ou JSON (`--json`), e comandos para configurar e consultar autenticação (`neo config auth`) com armazenamento seguro no Keyring do SO.

## Critérios de aceite

### AC-1: Execução básica e verificação de versão
- **Dado** o pacote Neo instalado no ambiente
- **Quando** o usuário executar `neo --help`
- **Então** a CLI exibe a descrição oficial do Neo, as opções globais e os subcomandos disponíveis com saída formatada pelo Rich e exit code 0.
- **Quando** o usuário executar `neo --version`
- **Então** a CLI exibe o nome e a versão atual do Neo (ex: `Neo v0.1.0`) e encerra com exit code 0.

### AC-2: Armazenamento seguro de credenciais (Bitbucket / Shortcut)
- **Dado** que o usuário possui um token da API (Bitbucket App Password ou Shortcut Token)
- **Quando** o usuário executar `neo config auth set bitbucket --token "meu-secret-token"`
- **Então** o token é armazenado no Keyring do SO sob o serviço `neo-cli` e o sistema exibe uma mensagem de sucesso no terminal com Rich e exit code 0.
- **Quando** o usuário omitir a flag `--token` em ambiente interativo
- **Então** o sistema solicita o token via prompt com digitação oculta (secret prompt).

### AC-3: Consulta e mascaramento de credenciais
- **Dado** que um token para o serviço `shortcut` está cadastrado
- **Quando** o usuário executar `neo config auth get shortcut`
- **Então** a CLI exibe o status `configurado` e o valor mascarado (ex: `****oken` ou `[configurado no keyring]`), sem nunca exibir o token em texto puro, com exit code 0.
- **Quando** o serviço não tiver credencial configurada
- **Então** a CLI informa que o serviço não está configurado e encerra com exit code 1 (ou status não configurado se `--json`).

### AC-4: Resolução de credenciais com hierarquia de precedência
- **Dado** o sistema precisando resolver uma credencial para um serviço (ex: `bitbucket`)
- **Quando** existir uma variável de ambiente definida (`BITBUCKET_TOKEN`)
- **Então** o sistema utiliza o valor da variável de ambiente com prioridade sobre o Keyring e sobre o arquivo `~/.config/neo/config.toml`.
- **Quando** a variável de ambiente não existir, mas o Keyring possuir a chave
- **Então** o sistema obtém a chave do Keyring.
- **Quando** nem a variável nem o Keyring estiverem disponíveis, mas o arquivo `config.toml` contiver o token
- **Então** o sistema utiliza o token do arquivo `config.toml`.

### AC-5: Suporte à flag universal `--json`
- **Dado** qualquer comando da CLI (ex: `neo config auth get bitbucket --json` ou `neo config show --json`)
- **Quando** a flag global `--json` for informada
- **Então** a saída no `stdout` é estritamente um objeto ou array JSON válido e parseável, sem tags de cor ou painéis Rich, e o exit code reflete o sucesso ou falha da operação.

### AC-6: Remoção de credencial configurada
- **Dado** uma credencial armazenada para o serviço `bitbucket`
- **Quando** o usuário executar `neo config auth delete bitbucket`
- **Então** a credencial é removida do Keyring (ou arquivo de fallback) e o comando exibe confirmação com exit code 0.

## Matriz de decisão (Resolução de Credenciais)

| Variável de Ambiente | Keyring do SO | Arquivo config.toml | Fonte Utilizada | AC |
|---|---|---|---|---|
| Presente | Presente | Presente | Variável de Ambiente | AC-4 |
| Ausente | Presente | Presente | Keyring do SO | AC-4 |
| Ausente | Ausente | Presente | Arquivo config.toml | AC-4 |
| Ausente | Ausente | Ausente | Nenhuma (Retorna None/Erro) | AC-3, AC-4 |

## Casos de borda e erros
- **Serviço desconhecido:** `neo config auth set invalido --token xxx` retorna erro claro listando os serviços suportados (`bitbucket`, `shortcut`).
- **Falha de acesso ao Keyring:** Fallback automático para `~/.config/neo/config.toml` com criação do arquivo com permissões `0600` e aviso no terminal.

## Fora de escopo
- Chamadas HTTP reais para validação remota de credenciais contra as APIs do Bitbucket/Shortcut (escopo das specs `0003` e `0004`).
- Módulos `repo`, `story`, `commits`, `bug` (serão implementados nas specs subsequentes).

## Rastreabilidade
- Roadmap: Onda 1, Item 1
- ADRs relacionados:
  - [ADR-0002](../../docs/architecture/adr/0002-tech-stack-core.md)
  - [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md)
  - [ADR-0004](../../docs/architecture/adr/0004-gestao-de-credenciais-e-seguranca.md)
  - [ADR-0005](../../docs/architecture/adr/0005-padroes-de-qualidade-e-testes.md)
  - [ADR-0006](../../docs/architecture/adr/0006-observabilidade-e-ux-cli.md)
