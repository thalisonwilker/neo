---
name: spec
description: Contrato da atualização de contexto Git, autenticação, branches e repositórios locais.
alwaysApply: true
---

# Spec — Atualização dos comandos Git

> **Fonte da verdade.** Status: implementado · Tier: arquitetural

## Resumo

O Neo passa a manter contexto por repositório local, manipular branches locais, criar e publicar repositórios e validar credenciais configuradas por `api-key`.

Esta spec substitui os comportamentos correspondentes das specs 0014 e 0010: `repo list` passa a listar repositórios locais (`repo remote-list` preserva a consulta remota), `auth login` é substituído, e as operações de branch desta entrega são locais.

## Critérios de aceite

### AC-1: Registro e seleção de repositórios
- **Dado** um diretório que contém um repositório Git, **quando** executar `neo git repo select <caminho>`, **então** o Neo registra o caminho absoluto e o seleciona persistentemente sem alterar o diretório do terminal.
- **E** `neo git repo list` lista os repositórios locais registrados e identifica o selecionado; `--json` retorna dados estruturados.
- **E** caminho inexistente ou que não seja repositório Git falha sem alterar a seleção. Sem seleção, mantém-se a detecção pelo diretório corrente.

### AC-2: Task associada ao repositório
- **Dado** um repositório selecionado, **quando** executar `neo git config set task <id>`, **então** associa o ID não vazio a esse repositório.
- **E** `get task`, `list` e `status` mostram o ID correspondente à seleção; `unset task` remove essa associação. Ao selecionar outro repositório, sua própria task é usada.

### AC-3: Branches locais
- **Dado** um repositório selecionado, **quando** executar `neo git branch list`, `select <nome>`, `create <nome>` ou `delete <nome>`, **então** lista, faz checkout, cria ou exclui, respectivamente, a branch local nesse repositório.
- **E** a exclusão exige confirmação ou `--yes`, não remove a branch ativa e não usa exclusão forçada. A listagem suporta `--json`.
- **E** `neo git config get branch` e `status` mostram a branch ativa; `config set branch <nome>` faz o mesmo checkout de `branch select`. `unset branch` falha com orientação, pois a branch ativa é estado do Git e não uma preferência removível.

### AC-4: Criar e publicar repositório
- **Dado** nome e caminho de destino inexistente, **quando** executar `neo git repo create <nome> --path <caminho>`, **então** cria repositório local, arquivos iniciais `README.md` e `AGENTS.md`, commit inicial, repositório remoto privado, `origin` e envia a branch inicial.
- **E** `--public` permite criar o remoto público; o repositório criado é registrado e selecionado.
- **E** não sobrescreve caminho existente. Se uma etapa remota falhar, preserva o local, informa a etapa e se o remoto foi criado; não remove recursos já criados automaticamente.

### AC-5: Editar descrição
- **Dado** repositório selecionado com `origin` reconhecido e credencial, **quando** executar `neo git repo edit --description <texto>`, **então** atualiza a descrição no provedor e informa o resultado.

### AC-6: Credencial validada
- **Dado** provedor configurado explicitamente, **quando** executar `neo git config set api-key`, **então** solicita chave por entrada oculta, solicita e-mail para Bitbucket quando necessário, testa a credencial diretamente no provedor e a salva apenas após sucesso.
- **E** sem provedor configurado, com credencial inválida ou falha de rede, encerra com erro e mantém a credencial anteriormente armazenada.
- **E** `get api-key`, `list` e `status` mostram estado/origem sem mostrar o segredo; `unset api-key` solicita confirmação ou aceita `--yes` e remove a credencial armazenada, sem alterar variáveis de ambiente.
- **E** `neo git auth login` informa a migração para `neo git config set api-key`; variáveis de ambiente de credenciais mantêm a precedência existente.

### AC-7: Configuração e status
- **Dado** o contexto Git, **quando** executar `neo git config get|list` ou `neo git status`, **então** apresenta provedor, workspace, repositório, branch, task e estado de autenticação sem expor credenciais.
- **E** `config set repo <caminho>` equivale a `repo select`; `get repo` retorna o selecionado e `unset repo` limpa a seleção sem apagar o diretório nem seu registro. `provider` e `workspace` mantêm o contrato de configuração existente.
- **E** os comandos de leitura existentes de commits usam o repositório selecionado e mantêm suas opções explícitas; `--json` continua disponível para leituras.

## Casos de borda e erros
- Não há repositório selecionado nem Git no diretório atual: comandos que exigem repositório retornam erro e orientam a selecionar um caminho.
- Falhas de Git, API e autenticação são informadas sem imprimir credenciais. Uma falha de rede não invalida a credencial salva anteriormente.
- Variáveis de ambiente podem continuar sobrepondo uma credencial armazenada; a saída informa a origem efetiva.

## Fora de escopo
- `neo git pr`, operações remotas de branch e novas ações de commits.

## Rastreabilidade
- [Produto](product.md) · [Design](design.md) · [Domínio](domain.md) · [Tasks](tasks.md)
