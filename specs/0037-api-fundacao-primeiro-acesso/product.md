---
name: product
description: PRD-lite da feature 0037 — fundação da API FastAPI do Neo com cadastro restrito, primeiro acesso e boas-vindas (por quê e para quem).
alwaysApply: false
---

# Product — Fundação da API e primeiro acesso

> **Tier:** arquitetural · **Status:** aprovado (22/11/2026) · **Dono:** Thalyson Wilker
> Responde: **por quê** e **para quem**.

## Problema
O painel web (`web/`, feature 0036) já tem login e cadastro pelo Clerk, mas **não tem backend próprio**:

- as rotas de API do painel (`web/src/app/api/products` e `users`) são **dados de exemplo** do template;
- não existe **usuário do Neo**: o Clerk sabe quem entrou, mas o Neo não guarda nada sobre essa pessoa (nome de exibição, workspaces, preferências);
- depois de cadastrar, a pessoa cai direto no painel de exemplo, **sem primeiro acesso nem boas-vindas**;
- o **cadastro está aberto a qualquer pessoa** (aceito no ADR-0010 só enquanto não houver dados reais). Esta feature cria os primeiros dados reais, então a restrição passa a ser obrigatória.

Sem uma API, o objetivo de um **painel completo de gerenciamento de projetos** não tem onde guardar nem servir dados.

Evidência: sessão de 22/11/2026 (análise do projeto e escolha de FastAPI em vez de Django).

## Para quem
**Power User Produtivo** e **Engenheiro de Software Focado** (`vision.md`). No início, um usuário (o dono do Neo) e, depois, poucas pessoas convidadas por ele.

## Resultado esperado / métrica de sucesso
- **Métrica 1:** 100% das rotas da API, exceto a de saúde, recusam pedidos sem token válido do Clerk.
- **Métrica 2:** nenhum e-mail fora da lista de permissão consegue criar usuário no Neo.
- **Métrica 3:** do cadastro até as boas-vindas, no máximo 2 telas (primeiro acesso → boas-vindas); quem já concluiu o primeiro acesso vai direto ao painel.
- Baseline: sem API, sem usuário local e cadastro aberto → Alvo: API no ar, usuário e workspace persistidos, cadastro restrito.

## Goals
- Subir a **API em FastAPI** dentro do pacote `neo` (`src/neo/interfaces/api`), com PostgreSQL, SQLAlchemy 2 e Alembic, documentação OpenAPI e rota de saúde.
- **Validar o token do Clerk** em toda rota protegida e **criar o usuário do Neo no primeiro pedido** de alguém autorizado.
- **Restringir o cadastro** com uma lista de permissão de e-mails mantida na API.
- **Primeiro acesso** no painel: coletar o nome de exibição e criar o primeiro workspace (nome e tipo).
- **Tela de boas-vindas** depois do primeiro acesso, levando ao painel.
- Começar a separar as camadas `domain/`, `application/`, `infrastructure/` e `interfaces/` (só para o que esta feature precisa).

## Non-goals
- Projetos, tarefas, quadros e o restante do gerenciamento de projetos (features seguintes).
- Trocar o Clerk por autenticação própria; organizações, papéis e permissões do Clerk.
- Mover os comandos atuais da CLI para a nova estrutura de camadas.
- Conectar GitHub, Bitbucket ou Shortcut pelo painel.
- Publicar a API em produção (deploy, domínio, instância de produção do Clerk).
- Tela para gerenciar a lista de permissão (nesta feature ela é editada por configuração ou comando).

## Riscos / premissas
- **Premissa:** o token de sessão do Clerk pode ser validado pela chave pública (JWKS) sem chamar o Clerk a cada pedido.
- **Premissa:** o e-mail principal vem no token ou pode ser lido da API do Clerk no primeiro acesso.
- **Risco:** a restrição só na API deixa a pessoa não autorizada criar conta no Clerk. Ela não acessa nada, mas a conta existe lá. Avaliar também restringir no próprio Clerk.
- **Risco de linguagem ubíqua:** "workspace" no Neo hoje é o **workspace do provedor Git** (`neo git config set workspace`). O workspace do painel (Trabalho, Estudos, Hobbies, Pessoal) é outra coisa. **Precisa de um termo próprio no `domain.md`** antes da spec.
- **Risco:** primeira peça com banco de dados e servidor HTTP no repositório; gates de qualidade novos entram no `TESTING.md`.
