---
name: uat
description: Roteiro de UAT manual da feature 0036 — configuração do Clerk e verificação do login real (AC-10 a AC-13 e confirmações de AC-2, AC-3, AC-4 e AC-12).
alwaysApply: false
---

# UAT — Fluxo de login do painel web

> **Gate da tarefa 10:** todos os passos abaixo marcados como **passou** ou **falhou**, com a data.
> Esta é a única verificação manual da feature: a entrada real depende do serviço do Clerk, e o `TESTING.md` proíbe chamadas externas nos testes automatizados.
> **Segurança:** nunca cole senhas, códigos ou URLs de retorno com `code=` neste arquivo nem no chat.

## Como preparar
```bash
cd ~/Projects/neo/web && npm run dev -- -p 3100
```
Abra **http://localhost:3100** numa **janela anônima** do navegador (sessão limpa a cada rodada).

## Parte 1 — Configuração da aplicação Clerk "Neo" (manual, no painel do Clerk)

Estado lido em 22/11/2026 na instância de desenvolvimento (somente leitura, sem credenciais):

| # | Item | Esperado | Estado em 22/11/2026 | Ação |
|---|------|----------|----------------------|------|
| C1 | Cadastro aberto (AC-11) | modo **público** | público ✓ | nenhuma |
| C2 | Google (AC-10) | habilitado | habilitado ✓ | nenhuma |
| C3 | GitHub (AC-10) | habilitado | **não habilitado** | habilitar a conexão social do GitHub |
| C4 | E-mail e senha (AC-10) | senha habilitada como método de entrada | senha habilitada ✓ (campo aparece no cadastro) | nenhuma |
| C5 | Link mágico (AC-10) | verificação de e-mail por **link** | **por código** (`email_code`), sem link | habilitar a verificação por link no e-mail e conferir se a tela passa a oferecer o link |
| C6 | Rotas do painel | o app usa `/auth/sign-in`, `/auth/sign-up` e `/dashboard/overview` por variáveis de ambiente | `.env.local` alinhado na tarefa 4 ✓ | nenhuma |

> Os rótulos do painel do Clerk podem mudar; procure em **User & authentication** as seções de conexões sociais e de e-mail. Em desenvolvimento, Google e GitHub usam credenciais compartilhadas do Clerk, o que dispensa criar um aplicativo OAuth próprio.
>
> **Depois de ligar C3 e C5, recarregue `/auth/sign-in`**: a tela deve mostrar os botões do Google e do GitHub e, no e-mail, a opção de link. Se algo não aparecer, anote em "Observações".

## Parte 2 — Roteiro

Marque cada linha. Resultado: **passou**, **falhou** ou **n/a** (com motivo).

| # | AC | Passo | Esperado | Resultado | Data | Observações |
|---|----|-------|----------|-----------|------|-------------|
| U1 | AC-2 | Sem sessão, abra `/dashboard/kanban` | Termina em `/auth/sign-in?redirect_url=%2Fdashboard%2Fkanban`, sem mostrar o painel | | | |
| U2 | AC-3 | Entre por qualquer método a partir de U1 | Chega em `/dashboard/kanban` (o destino pedido), não em `/dashboard/overview` | | | |
| U3 | AC-10 | Entrar com **Google** | Chega ao painel | | | |
| U4 | AC-10 | Entrar com **GitHub** | Chega ao painel | | | |
| U5 | AC-10 | Entrar com **e-mail e senha** | Chega ao painel | | | |
| U6 | AC-10 | Entrar com **link mágico** (e-mail) | O e-mail traz um link; abri-lo conclui a entrada | | | |
| U7 | AC-11 | Cadastrar com um e-mail novo (ex.: `seuemail+teste1@...`) em `/auth/sign-up` | Conta criada e chegada em `/dashboard/overview`, sem bloqueio por e-mail | | | |
| U8 | AC-4 | Abra `/auth/sign-in?redirect_url=https%3A%2F%2Fevil.example` e entre | Chega em `/dashboard/overview` e **nunca** em `evil.example` | | | |
| U9 | AC-12 | Com sessão ativa, menu do usuário na sidebar → **Sair** | Sessão encerrada e tela `/auth/sign-in` | | | |
| U10 | AC-12 | Depois de sair, volte a `/dashboard/overview` | Pede para entrar de novo (redireciona para a entrada) | | | |
| U11 | AC-13 | Entrar com **senha errada** | Mensagem clara em português, sem detalhes técnicos | | | |
| U12 | AC-13 | Informar um **e-mail inexistente** ou um **código/link expirado ou já usado** | Mensagem clara em português | | | |
| U13 | AC-13 | Passar os olhos em todas as telas de entrada e cadastro e nas mensagens acima | Nenhum texto em inglês | | | |
| U14 | AC-1 | Sem sessão, abra `/api/products` | Resposta de erro (401) e nenhum dado | | | |

## Resultado da rodada
- **Data:** ____
- **Responsável:** ____
- **Conclusão:** ____ (todos os passos passaram / há falhas: listar)
- **Falhas e ajustes necessários:** ____

## Observações da configuração
- Clerk "Neo" (desenvolvimento): chaves `pk_test` e `sk_test` em `web/.env.local`, fora do git.
- Cadastro aberto é decisão registrada no ADR-0010: **restringir antes de conectar dados reais**.
