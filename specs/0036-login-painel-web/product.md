---
name: product
description: PRD-lite da feature 0036 — fluxo de login do painel web do Neo (por quê e para quem).
alwaysApply: false
---

# Product — Fluxo de login do painel web

> **Tier:** arquitetural · **Status:** rascunho · **Dono:** Thalyson Wilker
> Responde: **por quê** e **para quem**.

## Problema
O painel web do Neo (`web/`, template Kiranism com o tema NEO) já abre e tem login do Clerk, mas esse login é o **padrão do template**, não um fluxo pensado para o Neo:

- as telas de entrada e cadastro mantêm textos de exemplo ("Logo" e um depoimento de terceiros) e o cartão do Clerk fica em cinza neutro, fora da identidade NEO;
- **não há definição** de quais formas de entrar existem, nem de para onde o usuário vai depois de entrar, nem de como sai;
- o `clerk init` deixou um `<ClerkProvider>` duplicado em `layout.tsx` e criou um **segundo par de rotas** (`/sign-in` e `/sign-up`) ao lado das originais (`/auth/...`), e o comportamento do conjunto nunca foi verificado ponta a ponta;
- as chaves em uso são de uma aplicação Clerk de **desenvolvimento**, sem decisão registrada sobre o provedor de autenticação.

Sem isso, o painel não pode ser tratado como produto: não há uma garantia verificada de que as telas só abrem com sessão, nem uma experiência de entrada coerente.

Evidência: sessão de 22/11/2026 (instalação do template, execução na porta 3100 e revisão visual do tema).

## Para quem
**Power User Produtivo** e **Engenheiro de Software Focado** (personas do `vision.md`). No início, **um único usuário**: o próprio dono do Neo, acessando o painel no próprio computador, com frequência diária.

## Resultado esperado / métrica de sucesso
- **Métrica 1:** nenhuma rota de `/dashboard/*` acessível sem sessão válida.
- **Métrica 2:** da primeira visita ao painel até a tela inicial, em até 3 interações, e na visita seguinte (sessão ativa) em 0 interações.
- Baseline: login do template, com métodos não definidos, sem verificação ponta a ponta → Alvo: fluxo definido, testado e coerente com a identidade NEO.

## Goals
- Entrar no painel por **Google, e-mail e senha, link mágico por e-mail e GitHub**.
- **Cadastrar** uma conta e **sair** (encerrar a sessão) com retorno claro à tela de entrada.
- **Proteger** todas as rotas do painel e, ao entrar, levar o usuário ao destino que ele pediu.
- Telas de entrada e cadastro **sem textos de exemplo** e com o **visual NEO** (cores, fontes e vidro do tema).
- Estados de erro claros: credencial inválida, link expirado, método indisponível.

## Non-goals
- Organizações, papéis, permissões e cobrança do Clerk (RBAC multiusuário).
- Ligar a sessão do painel à CLI Neo (tokens, `config.toml`, keyring): feature posterior.
- Conectar GitHub, Bitbucket ou Shortcut ao painel como **fonte de dados** (aqui o GitHub é só forma de entrar).
- Trocar o Clerk por autenticação própria.
- Publicar o painel em produção e criar a instância de produção do Clerk.
- Autenticação em dois fatores e recuperação avançada de conta.

## Riscos / premissas
- **Premissa:** os quatro métodos podem ser habilitados na aplicação Clerk "Neo" pelo painel do Clerk, uma configuração **fora do repositório** que precisa ser feita à mão e registrada.
- **Risco:** o Clerk é um serviço de terceiros; e-mails e identidades ficam fora do controle local do usuário, o que tensiona o princípio de "preservar o controle do usuário" do `vision.md`. A decisão precisa virar ADR no `design.md`.
- **Risco:** instâncias de desenvolvimento do Clerk têm limites de uso e não servem para produção.
- **Risco de linguagem ubíqua:** "workspace" no Neo significa o workspace do provedor Git, enquanto o Clerk tem "Organizations" e o protótipo do painel usa "workspace" para Trabalho, Estudos, Hobbies e Pessoal. A feature não usa o conceito de organização do Clerk.
