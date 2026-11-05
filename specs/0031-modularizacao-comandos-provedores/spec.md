---
name: spec
description: Contrato da modularização de comandos e provedores Git e tarefas.
alwaysApply: true
---

# Spec — Modularização de comandos e provedores

> **Status:** implementado. Critérios de aceite verificados pelos testes da feature e de regressão.

## Resumo

Organizar os comandos segundo a hierarquia da CLI e acessar GitHub, Bitbucket e Shortcut por contratos comuns de provedores, preservando o comportamento existente.

## Critérios de aceite

### AC-1: Comandos modularizados
- **Dado** os grupos `git`, `tasks`, `config`, `agent` e `fin` existentes.
- **Quando** os módulos de comandos forem organizados.
- **Então** cada grupo e subgrupo possui pacote próprio e cada ação possui módulo próprio, com helpers compartilhados separados.
- **E** `commands/git/config/set/` contém módulos para `provider`, `api_key` e `workspace`; o dispatcher também preserva `repo`, `task`, `branch` e demais chaves atualmente aceitas.
- **E** a inicialização da aplicação e `neo --help` executam sem importação circular.

### AC-2: Compatibilidade da CLI
- **Dado** uma invocação atualmente suportada, incluindo aliases, opções, argumentos e prompts.
- **Quando** executada após a refatoração com as mesmas configurações e respostas externas.
- **Então** preserva a gramática, os efeitos, a saída de sucesso ou erro, o JSON e o código de saída existentes, inclusive os aliases ocultos.
- **E** a configuração persistida e as credenciais continuam legíveis sem migração.

### AC-3: Contrato GitProvider e adapters
- **Dado** os adapters GitHub e Bitbucket com respostas HTTP simuladas equivalentes.
- **Quando** autenticam e executam as operações Git atualmente suportadas pelo contrato, incluindo workspaces, repositórios, commits e pull requests.
- **Então** ambos satisfazem o contrato tipado `GitProvider` e retornam os respectivos modelos comuns, sem expor modelos nomeados por outro provedor.
- **E** falhas de autenticação, recurso ausente, limite, rede e operação não suportada mantêm o comportamento observável atual na CLI.

### AC-4: Contrato TaskProvider e adapter Shortcut
- **Dado** o Shortcut configurado e respostas HTTP simuladas.
- **Quando** os comandos atuais de tarefas consultam identidade, stories, comentários, checklist, iterações e workflows ou criam os recursos atualmente suportados.
- **Então** usam o contrato `TaskProvider` e os contratos de capacidades opcionais aplicáveis, retornando os dados necessários ao comportamento atual.
- **E** os módulos de comandos não importam diretamente o cliente ou os modelos específicos do Shortcut.

### AC-5: Capacidades indisponíveis e Trello
- **Dado** um provider de tarefas de teste que não implementa uma capacidade opcional.
- **Quando** uma operação da CLI que a exige for solicitada.
- **Então** a operação termina com erro explícito de capacidade não suportada e sem alterar dados remotos.
- **E** Trello não aparece como provider funcional ou selecionável nesta entrega.

### AC-6: Limites de dependência e credenciais
- **Dado** os contratos e modelos de Git e tarefas e os adapters concretos.
- **Quando** suas dependências forem verificadas.
- **Então** contratos e modelos não importam os adapters, os comandos não executam requisições HTTP brutas e as credenciais continuam sendo obtidas pelos mecanismos existentes.
- **E** nenhuma credencial é incluída em saída ou logs.

## Casos de borda e erros

- Credencial ausente ou inválida, recurso ausente, limite de API e falha de rede: manter o comportamento já estabelecido para cada comando e provider.
- Mudança de provider Git e seleção interativa de workspace: preservar os contratos das features 0029 e 0030.
- Aliases e comandos legados: manter a visibilidade e o comportamento existentes.

## Fora de escopo

- Implementação funcional ou configuração de Trello.
- Mudanças de gramática, funcionalidades de negócio, configuração ou formato de armazenamento de credenciais.
- Garantia de compatibilidade de caminhos de importação Python internos anteriores; a interface de compatibilidade desta feature é a CLI.

## Rastreabilidade

- Product: [product.md](product.md)
- Design: [design.md](design.md)
- Domínio: [domain.md](domain.md)
- ADRs relacionados: [ADR-0003](../../docs/architecture/adr/0003-arquitetura-modular-e-integracoes.md) e [ADR-0009](../../docs/architecture/adr/0009-contratos-provedores-tarefas.md).
