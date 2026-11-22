---
name: spec
description: Contrato da feature 0037 — API FastAPI do Neo com Lista de permissão, Primeiro acesso e Boas-vindas no painel.
alwaysApply: true
---

# Spec — Fundação da API e primeiro acesso

> **Fonte da verdade.** Status: aprovado (22/11/2026) · Tier: arquitetural
> Termos conforme [domain.md](domain.md). Erros da API no corpo `{erro, mensagem}` (mensagem em pt-BR).

## Resumo
O Neo passa a ter uma API que reconhece quem entrou pelo Clerk, só registra Usuários com E-mail autorizado e conduz o Usuário novo pelo Primeiro acesso até as Boas-vindas.

## Critérios de aceite

### API

### AC-1: Saúde da API
- **Dado** a API no ar
- **Quando** alguém chama `GET /health` sem token
- **Então** recebe 200 com `{"status": "ok", "db": "ok"}`; se o banco estiver fora, recebe 503 com `"db": "erro"`

### AC-2: Pedido sem token válido é recusado
- **Dado** uma rota `/v1/*`
- **Quando** o pedido vem sem token, com token expirado, com assinatura inválida, emissor diferente de `CLERK_ISSUER` ou `azp` fora de `CLERK_AUTHORIZED_PARTIES`
- **Então** recebe 401 com `erro: "token_invalido"` e nada é gravado no banco

### AC-3: Primeiro pedido de E-mail autorizado cria o Usuário
- **Dado** um token válido de uma identidade sem Usuário, cujo e-mail principal está na Lista de permissão
- **Quando** chama `GET /v1/me`
- **Então** um Usuário é criado com esse `clerk_user_id` e e-mail (minúsculo), e a resposta é 200 com `primeiro_acesso_concluido: false`, `nome_exibicao: null` e `espacos: []`

### AC-4: E-mail fora da Lista de permissão é recusado
- **Dado** um token válido de uma identidade sem Usuário, cujo e-mail **não** está na Lista de permissão
- **Quando** chama qualquer rota `/v1/*`
- **Então** recebe 403 com `erro: "acesso_nao_liberado"`, nenhum Usuário é criado e a recusa é registrada em log

### AC-5: Usuário existente é reconhecido
- **Dado** um Usuário já registrado
- **Quando** chama `GET /v1/me`
- **Então** recebe 200 com os dados atuais, sem consultar o Clerk, **mesmo que o e-mail tenha sido removido da Lista de permissão depois**

### AC-6: Concluir o Primeiro acesso
- **Dado** um Usuário com Primeiro acesso pendente
- **Quando** chama `POST /v1/primeiro-acesso` com `{"nome_exibicao": "Thalyson", "espaco": {"nome": "Neo", "tipo": "trabalho"}}`
- **Então** recebe 201 com `primeiro_acesso_concluido: true`, `nome_exibicao: "Thalyson"` e um Espaço `{nome: "Neo", tipo: "trabalho"}`; Usuário e Espaço são gravados na mesma transação

### AC-7: Dados inválidos no Primeiro acesso
- **Dado** um Usuário com Primeiro acesso pendente
- **Quando** envia nome de exibição vazio, só com espaços ou com mais de 60 caracteres; nome do Espaço vazio ou com mais de 100 (era 40; alterado na [0040](../0040-criar-espaco/spec.md) AC-6); ou tipo fora de `trabalho`, `estudos`, `hobbies`, `pessoal`
- **Então** recebe 422 com `erro: "dados_invalidos"` indicando o campo, e nada é gravado. Espaços nas pontas são removidos antes de validar.

### AC-8: Primeiro acesso não se repete
- **Dado** um Usuário com Primeiro acesso concluído
- **Quando** chama `POST /v1/primeiro-acesso` de novo
- **Então** recebe 409 com `erro: "primeiro_acesso_ja_concluido"` e nada muda

### AC-9: Logs sem dados sensíveis e CORS restrito
- **Dado** a API atendendo pedidos
- **Quando** qualquer pedido é registrado em log
- **Então** o log tem método, rota, status, duração e `request_id`, e **nunca** contém o token nem o e-mail completo (só mascarado, ex.: `t***@gmail.com`); e pedidos de origem diferente de `NEO_API_CORS_ORIGINS` (padrão `http://localhost:3100`) não recebem cabeçalhos CORS

### CLI — Lista de permissão

### AC-10: Gerenciar a Lista de permissão pela CLI
- **Dado** o banco configurado em `NEO_DATABASE_URL`
- **Quando** o mantenedor roda `neo api permitir <email>`, `neo api permissoes` e `neo api remover-permissao <email>`
- **Então**:
  - `permitir` grava o e-mail em minúsculas e confirma; se já existir, informa e sai com código 0 sem duplicar;
  - e-mail com formato inválido sai com código de erro de uso e não grava;
  - `permissoes` lista os e-mails (aceita `--json`);
  - `remover-permissao` apaga o e-mail; se não existir, informa e sai com código de "não encontrado"; **Usuários já registrados não são afetados** (AC-5)

### Painel

### AC-11: Direcionamento após entrar
- **Dado** uma sessão válida no painel
- **Quando** a pessoa abre qualquer rota de `/dashboard/*`, `/primeiro-acesso` ou `/boas-vindas`
- **Então** o painel consulta `GET /v1/me` e direciona conforme a matriz abaixo

### AC-12: Tela de Primeiro acesso
- **Dado** um Usuário com Primeiro acesso pendente em `/primeiro-acesso`
- **Quando** preenche o nome de exibição, o nome do Espaço e escolhe um dos 4 tipos, e envia
- **Então** o painel chama `POST /v1/primeiro-acesso` e vai para `/boas-vindas`; com erro 422, mostra a mensagem junto ao campo, sem sair da tela; o botão de envio fica desabilitado enquanto o pedido está em andamento

### AC-13: Boas-vindas
- **Dado** um Usuário que acabou de concluir o Primeiro acesso
- **Quando** chega em `/boas-vindas`
- **Então** vê "Boas-vindas, <nome de exibição>" com o nome do Espaço criado e um botão que leva a `/dashboard`; ao abrir `/boas-vindas` depois, numa nova visita, vai direto para `/dashboard`

### AC-14: Acesso não liberado no painel
- **Dado** uma sessão válida cuja API responde 403 `acesso_nao_liberado`
- **Quando** a pessoa abre qualquer rota protegida
- **Então** vê a tela "Acesso não liberado" explicando que o e-mail não está autorizado, com o botão "Sair" (encerra a sessão e volta para `/auth/sign-in`), e não vê nenhum dado do painel

### AC-15: API indisponível no painel
- **Dado** uma sessão válida e a API fora do ar ou respondendo 5xx
- **Quando** a pessoa abre uma rota protegida
- **Então** vê a mensagem "Não foi possível falar com o Neo agora" com o botão "Tentar de novo", sem quebrar a página

## Matriz de decisão — direcionamento no painel (AC-11)

| Resposta de `/v1/me` | Primeiro acesso | Boas-vindas pendentes nesta visita | Rota pedida | Resultado | AC |
|---|---|---|---|---|---|
| 200 | pendente | — | `/dashboard/*` | vai para `/primeiro-acesso` | AC-11 |
| 200 | pendente | — | `/primeiro-acesso` | mostra o formulário | AC-12 |
| 200 | pendente | — | `/boas-vindas` | vai para `/primeiro-acesso` | AC-11 |
| 200 | concluído | não | `/dashboard/*` | mostra a rota pedida | AC-11 |
| 200 | concluído | não | `/primeiro-acesso` | vai para `/dashboard` | AC-11 |
| 200 | concluído | sim | `/boas-vindas` | mostra as Boas-vindas | AC-13 |
| 200 | concluído | não | `/boas-vindas` | vai para `/dashboard` | AC-13 |
| 403 | — | — | qualquer protegida | tela "Acesso não liberado" | AC-14 |
| 401 | — | — | qualquer protegida | encerra a sessão e vai para `/auth/sign-in` | AC-11 |
| 5xx / sem resposta | — | — | qualquer protegida | tela de API indisponível | AC-15 |

> "Boas-vindas pendentes nesta visita" = o Primeiro acesso foi concluído na navegação atual (estado do lado do painel, não da API).

## Casos de borda e erros
- Dois pedidos simultâneos no primeiro acesso de uma mesma identidade → um só Usuário é criado; o segundo pedido recebe o mesmo Usuário (200).
- E-mail com maiúsculas no Clerk e minúsculas na Lista de permissão → considerado autorizado.
- Clerk indisponível ao ler o e-mail de uma identidade nova → 503 `erro: "clerk_indisponivel"`, nada gravado.
- Chave de assinatura nova do Clerk (`kid` desconhecido) → a API recarrega o JWKS uma vez antes de recusar.
- Corpo do `POST /v1/primeiro-acesso` com campos extras → ignorados.

## Fora de escopo
> Vinculante.
- Projetos, tarefas, quadros, editar ou criar outros Espaços, editar o nome de exibição.
- Tela para gerenciar a Lista de permissão; bloquear Usuários já registrados.
- Mover os comandos atuais da CLI para as novas camadas.
- Deploy em produção, instância de produção do Clerk, webhooks do Clerk.
- Traduzir o restante do template do painel.
- Configurar a lista de permissão do Clerk por código (é manual, registrada no UAT).

## Rastreabilidade
- Product: [product.md](product.md)
- Design: [design.md](design.md)
- Domínio: [domain.md](domain.md)
- ADRs: [ADR-0010](../../docs/architecture/adr/0010-painel-web-nextjs-com-clerk.md), [ADR-0011](../../docs/architecture/adr/0011-api-fastapi-com-postgresql.md)
