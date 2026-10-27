---
name: spec
description: Contrato da feature 0004-modulo-shortcut (Shortcut REST API v3 com 5 funções essenciais).
alwaysApply: true
---

# Spec — 0004-modulo-shortcut

> **Fonte da verdade.** Status: aprovado
> Contrato de entrega da integração com o Shortcut via REST API v3 (`https://api.app.shortcut.com/api/v3`) com 5 operações essenciais de consulta e análise.

## Resumo
O Neo passará a consultar o Shortcut utilizando a REST API v3 oficial (`Shortcut-Token`), permitindo verificar o usuário autenticado (`whoami`), listar e buscar stories (`list`, `search`), detalhar uma story específica (`show`) e analisar o contexto de uma story para correlacionar com o desenvolvimento (`analyze`).

## Critérios de aceite

### AC-1: Verificação de membro autenticado (`whoami`)
- **Dado** o token do Shortcut configurado
- **Quando** o usuário executar `neo story whoami`
- **Então** a CLI consulta `GET /api/v3/member`, exibindo Nome, Username, ID e E-mail do usuário autenticado em Rich ou JSON, com exit code 0.

### AC-2: Listagem de stories com filtro pessoal (`list [--mine]`)
- **Dado** stories cadastradas no workspace do Shortcut
- **Quando** o usuário executar `neo story list`
- **Então** a CLI consulta a API v3 e exibe tabela Rich com ID, Tipo (Feature/Bug/Chore), Título, Estado e Responsáveis, com exit code 0.
- **Quando** o usuário passar a flag `--mine`
- **Então** a listagem filtra apenas as stories atribuídas ao usuário autenticado atual.

### AC-3: Busca textual de stories (`search <query>`)
- **Dado** o usuário pesquisando por um termo de demanda ou bug
- **Quando** executar `neo story search "login timeout"`
- **Então** a CLI consulta `GET /api/v3/search/stories?query=...` e exibe as stories correspondentes.

### AC-4: Exibição detalhada de story (`show <id>`)
- **Dado** uma story existente no Shortcut com ID `1234`
- **Quando** o usuário executar `neo story show 1234`
- **Então** a CLI busca `GET /api/v3/stories/1234` e renderiza um painel com Título, Descrição formatada, Tipo, Workflow State, Labels, Owners e URL no browser.
- **Quando** a story não existir (404)
- **Então** a CLI exibe erro amigável de não encontrada e encerra com exit code 1.

### AC-5: Análise de contexto de story (`analyze <id>`)
- **Dado** uma story com descrição e critérios no Shortcut
- **Quando** o usuário executar `neo story analyze 1234`
- **Então** a CLI analisa o conteúdo da story, sugerindo nomes padronizados de branch git (ex: `feature/sc-1234-slug` ou `bug/sc-1234-slug`), extraindo palavras-chave e termos técnicos para investigação em commits.

### AC-6: Tratamento de ausência de credenciais e erros HTTP
- **Dado** que o token do Shortcut não foi configurado
- **Quando** o usuário executar qualquer comando `neo story`
- **Então** a CLI intercepta e exibe: "Credenciais do Shortcut não configuradas. Execute `neo config auth set shortcut`.", com exit code 1.
- **Quando** a API retornar erro de autenticação (401/403)
- **Então** a CLI exibe mensagem orientando a renovação do token.

## Rastreabilidade
- Roadmap: Onda 1, Item 3
- Documentação da API: [Shortcut REST API v3](https://developer.shortcut.com/api/rest/v3)
- ADRs relacionados:
  - [ADR-0002](../../docs/architecture/adr/0002-tech-stack-core.md)
  - [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md)
  - [ADR-0006](../../docs/architecture/adr/0006-observabilidade-e-ux-cli.md)
