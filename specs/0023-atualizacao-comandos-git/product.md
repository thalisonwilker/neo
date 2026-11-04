---
name: product
description: Objetivos da atualização dos comandos Git e da autenticação do Neo.
alwaysApply: false
---

# Product — Atualização dos comandos Git

> **Tier:** arquitetural · **Status:** aprovado · **Dono:** mantenedor do Neo

## Problema
As operações de configuração, branch e repositório exigidas para o trabalho cotidiano não estão disponíveis em um fluxo unificado no Neo. A autenticação também usa um comando diferente daquele desejado para configuração da chave de API.

## Para quem
Desenvolvedores que trabalham com repositórios Git locais e com GitHub ou Bitbucket e desejam gerenciar seu contexto pela CLI.

## Resultado esperado / métrica de sucesso
- Baseline: `neo git config` não aceita `api-key` nem `task`; seleção, criação e remoção de branches e os fluxos solicitados de repositório não estão disponíveis como solicitados.
- Alvo: os fluxos abaixo ficam disponíveis e são verificáveis por testes de aceite. O contrato detalhado será definido na spec.

## Goals
- Exibir o status e gerenciar propriedades Git por `config set`, `get`, `list` e `unset`, incluindo provedor, workspace, chave de API, branch, task e repositório, conforme o contrato a definir.
- Configurar uma chave de API por `neo git config set api-key`, exigindo provedor configurado e testando a autenticação antes de considerá-la válida.
- Solicitar a chave com entrada oculta e salvá-la somente após validação; preservar a credencial anterior se o teste falhar. Solicitar o e-mail do Bitbucket quando necessário.
- Listar, selecionar, criar e deletar branches locais no repositório selecionado.
- Selecionar uma branch por checkout no repositório selecionado, tornando-a ativa para o Git e outras ferramentas.
- Associar uma task por seu ID ao repositório selecionado e recuperá-la ao selecionar novamente esse repositório.
- Criar repositórios locais e enviá-los para a nuvem; listar repositórios locais, editar descrição e selecionar um repositório.
- Editar a descrição do repositório no provedor Git configurado.
- Criar repositórios privados por padrão, com opção explícita de torná-los públicos.
- Ao criar um repositório vazio, gerar `README.md` e `AGENTS.md` e criar um commit inicial para possibilitar o envio.
- Preservar o repositório local e informar a etapa que falhou quando a criação ou o envio à nuvem falhar.
- Manter um registro dos repositórios locais criados ou selecionados pelo Neo para compor a listagem.
- Usar o repositório local selecionado como contexto persistente dos comandos Git do Neo, mesmo quando o terminal estiver em outro diretório, sem alterar o diretório do terminal.
- Preservar o acesso aos comandos de commits existentes.

## Non-goals
- Implementar `neo git pr`: fica para uma próxima spec.
- Expandir operações de commits além do que for necessário para esta atualização.
- Criar, enviar ou deletar branches na nuvem.

## Riscos / premissas
- O armazenamento da chave, as diferenças entre provedores e a transição do comando anterior de autenticação exigem definição no design e na spec.
- A recuperação após falha parcial de criação ou envio precisa de contrato explícito.
- Integração com ferramenta de gestão não foi utilizada: nenhuma está validada no roteamento MCP do projeto.
