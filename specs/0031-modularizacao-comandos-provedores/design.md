---
name: design
description: Design da modularização dos comandos e contratos de provedores Git e tarefas.
alwaysApply: false
---

# Design — Modularização de comandos e provedores

> **Tier:** arquitetural · **Status:** aprovado · **Data:** 2026-11-04

## Contexto, objetivos e limites

O [produto](product.md) aprovado descreve a fragmentação dos comandos e a necessidade de contratos comuns. A migração preserva os comandos, aliases, opções, saídas, códigos de erro, configuração e armazenamento seguro de credenciais existentes. Trello funcional e novas funcionalidades de negócio estão fora do escopo proposto.

## Design proposto

### Comandos

Cada grupo Typer fica em um pacote correspondente à hierarquia da CLI, com `__init__.py` registrando seus subgrupos e ações. Cada ação fica em módulo próprio; funções compartilhadas ficam em módulos internos. O registro deve evitar importações circulares e preservar callbacks, aliases ocultos, ajuda e a ordem de tratamento de erros. O dispatcher de `git config set` continua recebendo os mesmos argumentos e chama os módulos `provider.py`, `api_key.py` e `workspace.py`; eles não criam níveis adicionais na CLI.

### GitProvider

- Evoluir o `GitProviderProtocol` existente para `GitProvider` em `integrations/git/provider.py`, usando `Protocol` tipado e implementação estrutural.
- O contrato cobre validação de autenticação, listagem de workspaces, listagem/busca/consulta/criação/edição de repositórios, consulta de commits e operações de pull request já suportadas.
- Definir modelos neutros para workspace, repositório, commit e pull request; os adapters convertem dados externos e não expõem tipos específicos de outro fornecedor. A serialização utilizada pela CLI permanece compatível.
- `integrations/git/api/github` e `bitbucket` concentram transporte, parsing e detalhes de autenticação. Um resolvedor instancia o provider selecionado, mantendo a precedência e os mecanismos atuais de credenciais.
- Erros comuns representam autenticação, recurso ausente, limite de requisições, rede e operação não suportada; a borda os traduz para os códigos e mensagens já observáveis.

### TaskProvider

- `services/tasks/provider.py` define `TaskProvider` como `Protocol` tipado, com operações comuns para identidade autenticada, listar, buscar, consultar e criar tarefas, checklist e comentários.
- Capacidades adicionais, como iterações e estados de workflow, são contratos opcionais separados; comandos que dependem delas devem detectar ausência e produzir erro explícito, sem falhas silenciosas.
- `services/tasks/models.py` contém modelos neutros suficientes para o comportamento atual; `services/tasks/api/shortcut` adapta o cliente e seus tipos. `services/tasks/api/trello` é reservado e não configura nem anuncia um provider funcional.
- O resolvedor de tarefas recebe o provider selecionado e as credenciais existentes; os comandos dependem dos contratos e modelos comuns, sem importar o cliente Shortcut diretamente.

### Dependências e composição

A hierarquia física solicitada para tarefas coloca `api` dentro de `services/tasks`. Para preservar a direção lógica da regra de camadas, `provider.py`, `models.py` e a lógica de serviço não importam `api`; os adapters em `api` dependem dos contratos. O resolvedor faz a composição na borda da aplicação e não deve ser importado pelos contratos. A localização física dos adapters difere do ADR-0003, que os coloca em `integrations/`; se o design for aprovado, registrar novo ADR explicitando essa exceção e suas consequências, sem editar o ADR anterior.

## Cinco eixos

1. **Stack:** Python, Typer, Rich, httpx e Pydantic existentes; sem novas dependências propostas.
2. **Arquitetura:** contratos estruturais, modelos neutros, adapters isolados e composição na borda; sem novos bounded contexts previstos.
3. **Infra:** sem serviços ou recursos novos; reversão por versão de código, sem migração de dados prevista.
4. **Qualidade:** testes de contrato por provider existente, testes de regressão CLI e cobertura dos critérios da futura spec; executar pytest, Ruff, Mypy e os demais gates do projeto.
5. **Observabilidade:** manter mensagens, saída JSON e logs existentes; não registrar credenciais nem introduzir telemetria nova.

## Dependências

| Dependência | Uso |
|---|---|
| GitHub e Bitbucket | APIs de workspaces, repositórios, commits e pull requests já usadas |
| Shortcut | API de identidade, stories, workflows, iterações, checklist e comentários já usada |
| Configuração e credenciais do Neo | Seleção e autenticação dos providers, sem alterar persistência |
| Typer e Rich | Registro dos comandos e apresentação existente |

## Alternativas e consequências

| Alternativa | Benefício | Custo / decisão |
|---|---|---|
| Protocols e adapters na árvore solicitada | Contratos testáveis e organização por finalidade | Exige explicitar exceção ao ADR-0003 para adapters de tarefas |
| Classe abstrata com herança obrigatória | Implementação explícita e compartilhamento por herança | Mais acoplamento; o projeto já usa `Protocol` no Git |
| Adapters de tarefas em `integrations/` | Segue a localização do ADR-0003 | Não segue a árvore solicitada e aprovada |

## Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Mudança involuntária da CLI | Caracterizar ajuda, aliases, erros, JSON e fluxos existentes antes de migrar |
| Modelos neutros perdem dados ou alteram saída | Mapear todos os campos consumidos e testar paridade de serialização |
| APIs oferecem capacidades diferentes | Contratos opcionais e erro explícito; não prometer suporte ao Trello |
| Imports circulares durante extração | Separar registro Typer, ações e composição; validar importação e `neo --help` |
| Mocks existentes apontam para caminhos antigos | Migrar testes junto com consumidores e verificar comportamento, não somente imports |

## Etapas propostas

1. Registrar a decisão arquitetural e definir os critérios de aceite e tarefas.
2. Caracterizar comportamento existente e estabelecer contratos e modelos.
3. Migrar adapters Git e Shortcut, com testes de contrato.
4. Extrair comandos por grupo e atualizar pontos de composição.
5. Executar gates e atualizar documentação e estado.

## Questões para a spec

- Definir assinaturas e modelos precisos a partir dos usos atuais e validar recursos opcionais por comando.
- Definir o tratamento de compatibilidade dos imports internos antigos; a preservação da interface Python pública ainda não foi especificada.
- Definir critérios executáveis para a granularidade dos módulos e paridade da CLI.
