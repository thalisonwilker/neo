---
name: spec
description: Contrato da feature 0039 — remover do painel web tudo o que é exemplo do template, deixando só o que é do Neo.
alwaysApply: true
---

# Spec — Painel só com o Neo

> **Fonte da verdade.** Status: aprovado (22/11/2026) · Tier: pequeno
> Decisões do mantenedor (22/11/2026): manter a tela de conta do Clerk como "Minha conta"; remover as
> Organizations do Clerk do painel; tema único NEO escuro.

## Resumo
O painel em `web/` nasceu do template Kiranism. Depois das features 0036–0038, o que é do Neo é: entrada e
cadastro, Primeiro acesso, Boas-vindas, página inicial e a conta do Usuário. Todo o resto (páginas de
demonstração, APIs falsas, seletor de organização, temas extras, busca, notificações) sai do código, do menu
e das dependências.

## Critérios de aceite

### AC-1: Páginas e APIs de exemplo deixam de existir
- **Dado** um Usuário com sessão e Primeiro acesso concluído
- **Quando** abre `/dashboard/product`, `/dashboard/users`, `/dashboard/kanban`, `/dashboard/chat`, `/dashboard/ai-chat`, `/dashboard/forms` (e subpáginas), `/dashboard/react-query`, `/dashboard/elements/icons`, `/dashboard/exclusive`, `/dashboard/billing`, `/dashboard/notifications`, `/dashboard/workspaces` (e `/team`), `/api/products` ou `/api/users`
- **Então** recebe a página de "não encontrado" (404); o código dessas rotas e das features que só elas usavam não existe mais em `web/src/`

### AC-2: Menu lateral do Neo
- **Dado** o painel aberto
- **Quando** a pessoa olha o menu lateral
- **Então** vê no topo a marca NEO (sem seletor de organização), um único item "Início" que leva a `/dashboard/overview`, e no rodapé o seu usuário; o menu do usuário tem só "Minha conta" e "Sair"

### AC-3: Minha conta
- **Dado** o menu do usuário aberto
- **Quando** a pessoa escolhe "Minha conta"
- **Então** vai para `/dashboard/profile`, que mostra a tela de conta do Clerk (em pt-BR) com o título de página "Minha conta | NEO"

### AC-4: Cabeçalho enxuto
- **Dado** qualquer página do painel
- **Quando** a pessoa olha o cabeçalho
- **Então** vê só o botão de recolher o menu e a trilha da página ("Início" ou "Minha conta"); não há busca, link do GitHub, seletor de tema, botão claro/escuro nem notificações

### AC-5: Tema único NEO escuro e identidade Neo
- **Dado** qualquer página (inclusive entrada e cadastro)
- **Quando** ela carrega, em qualquer preferência de cor do sistema
- **Então** usa sempre o tema NEO escuro; o título das páginas segue o padrão já usado pelas telas do Neo, "<página> | NEO" (padrão "NEO"), inclusive a página inicial ("Início | NEO") e a descrição e as metatags não citam o template

### AC-6: O que já é do Neo continua funcionando
- **Dado** as features 0036 (login), 0037 (Primeiro acesso, Boas-vindas, acesso não liberado, API indisponível) e 0038 (página inicial)
- **Quando** a limpeza termina
- **Então** todos os testes delas continuam verdes, sem mudança de comportamento

### AC-7: Dependências só do que é usado
- **Dado** o `web/package.json`
- **Quando** a limpeza termina
- **Então** não há dependência que só o código removido usava, e `npm ci`, `next build` e `npm audit` passam

## Fora de escopo
> Vinculante.
- A biblioteca de componentes base (`web/src/components/ui/`, primitivos shadcn): fica inteira, é a base de telas futuras.
- Desligar Organizations no painel do Clerk (passo manual do mantenedor, registrado no STATE).
- Reescrever `web/AGENTS.md` (guia do template para agentes); só `web/README.md` passa a descrever o painel do Neo.
- Mudar regras de acesso da 0036 (`isProtectedPath` continua protegendo `/api/*`).
- Novas telas ou itens de menu.

## Rastreabilidade
- Depende de: [0036](../0036-login-painel-web/spec.md), [0037](../0037-api-fundacao-primeiro-acesso/spec.md), [0038](../0038-home-painel/spec.md)
- ADRs: [ADR-0010](../../docs/architecture/adr/0010-painel-web-nextjs-com-clerk.md)
