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
| C3 | GitHub | **fora do escopo** (decisão de 22/11/2026) | não habilitado | nenhuma |
| C4 | E-mail e senha (AC-10) | senha habilitada como método de entrada | senha habilitada ✓ (campo aparece no cadastro) | nenhuma |
| C5 | Link mágico (AC-10) | verificação de e-mail por **link** | por código (`email_code`) na leitura de 22/11/2026; **habilitado depois da 1ª rodada** (U6 passou) | nenhuma |
| C6 | Rotas do painel | o app usa `/auth/sign-in`, `/auth/sign-up` e `/dashboard/overview` por variáveis de ambiente | `.env.local` alinhado na tarefa 4 ✓ | nenhuma |

> Os rótulos do painel do Clerk podem mudar; procure em **User & authentication** as seções de conexões sociais e de e-mail. Em desenvolvimento, o Google usa credenciais compartilhadas do Clerk, o que dispensa criar um aplicativo OAuth próprio.
>
> **Depois de ligar C5, recarregue `/auth/sign-in`**: a tela deve mostrar o botão do Google e, no e-mail, a opção de link. Se algo não aparecer, anote em "Observações".

## Parte 2 — Roteiro

Marque cada linha. Resultado: **passou**, **falhou** ou **n/a** (com motivo).

| # | AC | Passo | Esperado | Resultado | Data | Observações |
|---|----|-------|----------|-----------|------|-------------|
| U1 | AC-2 | Sem sessão, abra `/dashboard/kanban` | Termina em `/auth/sign-in?redirect_url=%2Fdashboard%2Fkanban`, sem mostrar o painel | passou | 2026-11-22 | |
| U2 | AC-3 | Entre por qualquer método a partir de U1 | Chega em `/dashboard/kanban` (o destino pedido), não em `/dashboard/overview` | passou | 2026-11-22 | |
| U3 | AC-10 | Entrar com **Google** | Chega ao painel | passou | 2026-11-22 | |
| U4 | AC-10 | Entrar com **GitHub** | Chega ao painel | n/a | 2026-11-22 | Fora do escopo: o mantenedor retirou o GitHub (22/11/2026) e pediu validar apenas o login com e-mail e senha. |
| U5 | AC-10 | Entrar com **e-mail e senha** | Chega ao painel | passou | 2026-11-22 | |
| U6 | AC-10 | Entrar com **link mágico** (e-mail) | O e-mail traz um link; abri-lo conclui a entrada | passou | 2026-11-22 | Refeito depois de habilitar a verificação por link no Clerk (2ª rodada). |
| U7 | AC-11 | Cadastrar com um e-mail novo (ex.: `seuemail+teste1@...`) em `/auth/sign-up` | Conta criada e chegada em `/dashboard/overview`, sem bloqueio por e-mail | passou | 2026-11-22 | |
| U8 | AC-4 | Abra `/auth/sign-in?redirect_url=https%3A%2F%2Fevil.example` e entre | Chega em `/dashboard/overview` e **nunca** em `evil.example` | passou | 2026-11-22 | |
| U9 | AC-12 | Com sessão ativa, menu do usuário na sidebar → **Sair** | Sessão encerrada e tela `/auth/sign-in` | passou | 2026-11-22 | |
| U10 | AC-12 | Depois de sair, volte a `/dashboard/overview` | Pede para entrar de novo (redireciona para a entrada) | passou | 2026-11-22 | |
| U11 | AC-13 | Entrar com **senha errada** | Mensagem clara em português, sem detalhes técnicos | passou | 2026-11-22 | |
| U12 | AC-13 | Informar um **e-mail inexistente** ou um **código/link expirado ou já usado** | Mensagem clara em português | passou | 2026-11-22 | |
| U13 | AC-13 | Passar os olhos em todas as telas de entrada e cadastro e nas mensagens acima | Nenhum texto em inglês | passou | 2026-11-22 | |
| U14 | AC-1 | Sem sessão, abra `/api/products` | Resposta de erro (401) e nenhum dado | passou | 2026-11-22 | |

## Resultado da rodada
- **Data:** 2026-11-22
- **Responsável:** Thalyson Wilker (resultados informados por ele; não observados por outra pessoa)
- **Conclusão:** **aprovado**. 13 de 14 passos passaram e 1 é **n/a** (U4, GitHub, retirado do escopo). Os três métodos do AC-10 foram verificados: Google (U3), e-mail e senha (U5) e link mágico (U6).
- **Falhas:** nenhuma nos passos executados.
- **Histórico:** 1ª rodada em 22/11/2026 com 12 passos aprovados e U4 e U6 pendentes. Na 2ª rodada, no mesmo dia, o link mágico foi habilitado e passou, e o GitHub saiu do escopo.

## Observações da configuração
- Clerk "Neo" (desenvolvimento): chaves `pk_test` e `sk_test` em `web/.env.local`, fora do git.
- Cadastro aberto é decisão registrada no ADR-0010: **restringir antes de conectar dados reais**.
