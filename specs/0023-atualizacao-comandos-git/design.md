---
name: design
description: Design proposto para contexto Git, operações locais e autenticação validada.
alwaysApply: false
---

# Technical Design Doc — Atualização dos comandos Git

> **Tier:** arquitetural · **Status:** aprovado · **Data:** 2026-11-04

## Contexto e escopo

O [produto](product.md) define o fluxo desejado para autenticação, contexto, branches e repositórios. A CLI atual resolve o repositório a partir do diretório corrente e separa a autenticação em `neo git auth login`. Pull requests permanecem fora do escopo.

## Design proposto

1. Manter um registro persistente de repositórios locais conhecidos e o caminho do repositório selecionado. A seleção não muda o diretório do terminal; os comandos Git do Neo resolvem o repositório selecionado antes de consultar o diretório corrente. O registro também associa o ID da task a cada repositório.
2. Executar operações Git locais no caminho do repositório selecionado. A seleção de branch faz checkout; criação, listagem e exclusão são locais. Exigir confirmação antes da exclusão e recusar a exclusão da branch ativa.
3. Criar o repositório local e o remoto no provedor, configurando `origin` e enviando a branch inicial. Para um repositório vazio, criar `README.md` e `AGENTS.md` e um commit inicial; não inventar regras específicas para o projeto. Usar repositório privado por padrão e disponibilizar opção explícita para público. Se a operação remota falhar, preservar o diretório local, identificar o estágio e apresentar orientação de recuperação; não apagar automaticamente recursos já criados.
4. Atualizar a descrição no provedor para o repositório selecionado. Resolver provedor e workspace usando as regras existentes, salvo quando a spec definir mudança explícita.
5. Mudar o ponto de entrada de autenticação para `neo git config set api-key`: exigir provedor previamente configurado, solicitar a chave com entrada oculta, testar a credencial junto ao provedor e só salvá-la após validação bem-sucedida. Para Bitbucket, solicitar também o e-mail quando necessário. Reutilizar o armazenamento de credenciais existente; não exibir o segredo em `get`, `list`, status ou erros.
6. Manter `config get`, `list` e `unset` coerentes com os novos campos, explicitando na spec o tratamento de credenciais e da task. Preservar os comandos de commits existentes e deixar PRs para outra spec.

## Cinco eixos

- **Stack:** Python, Typer, Rich, httpx, keyring e Git local existentes.
- **Arquitetura:** CLI orquestra contexto e operações; integrações de provedores encapsulam chamadas remotas. A forma e a persistência exatas do registro exigem contrato na spec.
- **Infra:** arquivos locais de configuração e armazenamento de credenciais existentes; APIs GitHub e Bitbucket. Sem novos serviços próprios.
- **Qualidade:** testes unitários para persistência, resolução e falhas; testes de CLI isolados e mocks dos provedores; gates do projeto e critérios de aceite executáveis.
- **Observabilidade:** mensagens de etapa e erros acionáveis, saída JSON nos comandos de leitura e ausência de segredos em saídas e logs.

## Dependências e alternativas

| Dependência | Uso |
|---|---|
| Git local | Inicialização, branches, checkout, remote e envio |
| GitHub e Bitbucket | Validação da credencial, criação remota e edição de descrição |
| Keyring e fallback existente | Armazenamento de credenciais |

O registro explícito evita varredura do computador, mas somente repositórios criados ou selecionados aparecem na lista. A entrada oculta evita incluir a chave no histórico do shell; a validação antes de salvar impede substituir uma credencial funcional por outra inválida. Manter o repositório local após falha evita perda de trabalho, mas exige orientar a recuperação de recursos remotos parcialmente criados.

## Contratos propostos para detalhar na spec

- Sem repositório selecionado, manter a detecção atual pelo diretório corrente; uma seleção explícita tem prioridade. Caminhos inexistentes devem gerar erro acionável sem mudar a seleção.
- Registrar repositórios por caminho absoluto em arquivo próprio no diretório de configuração Neo; preservar configurações já existentes.
- `config get api-key` e `list` exibem apenas estado e origem, nunca o segredo. `unset api-key` remove a credencial armazenada do provedor configurado mediante confirmação; variáveis de ambiente continuam sendo controladas pelo ambiente.
- `neo git auth login` informa a mudança e orienta a usar `neo git config set api-key`. A validação usa diretamente a credencial fornecida, mesmo que variáveis de ambiente prevaleçam depois na resolução existente.
- Em colisão com arquivo ou diretório existente, recusar a criação sem sobrescrevê-los. Em falha parcial, indicar se o remoto chegou a ser criado e como retomar; não excluir automaticamente o remoto.
- A sintaxe detalhada, os códigos de saída e os casos de erro serão definidos como critérios testáveis na spec.

Decisões estruturais aprovadas devem ser avaliadas para ADR; critérios e casos de erro serão detalhados na spec antes da implementação.

Decisão estrutural: [ADR-0008](../../docs/architecture/adr/0008-contexto-git-local.md).
