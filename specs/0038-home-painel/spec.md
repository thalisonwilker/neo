---
name: spec
description: Contrato da feature 0038 — página inicial (home) do painel do Neo com saudação, contadores, calendário do mês, Espaços reais e próximas tarefas.
alwaysApply: true
---

# Spec — Página inicial do painel

> **Fonte da verdade.** Status: aprovado (22/11/2026) · Tier: pequeno
> Termos conforme [domínio da 0037](../0037-api-fundacao-primeiro-acesso/domain.md) e `docs/glossary.md`.
> Referência visual: protótipo `neo-command-center.html` (visão "hub"), adaptado ao que já existe.

## Resumo
Depois de entrar, o Usuário cai numa página inicial no visual do protótipo NEO: saudação com o nome de
exibição, quatro contadores de tarefas, o calendário do mês, a lista dos seus **Espaços** (dados reais de
`GET /v1/me`) e as próximas tarefas. Como tarefas ainda não existem no backend, contadores, calendário e
lista de tarefas aparecem **vazios** — sem dados fictícios.

A página fica em `/dashboard/overview` (destino pós-login da 0036) e substitui o conteúdo de exemplo do template.

## Critérios de aceite

### AC-1: Saudação e data de hoje
- **Dado** um Usuário com Primeiro acesso concluído e nome de exibição "Thalyson"
- **Quando** abre `/dashboard/overview`
- **Então** vê o título "Olá, Thalyson" (o nome em destaque), o subtítulo "Sua agenda com todos os Espaços. Acesse um deles ou crie um novo." e a data de hoje no formato `Dom, 22 Nov 2026` (dia da semana e mês abreviados em pt-BR, com inicial maiúscula)

### AC-2: Contadores de tarefas vazios
- **Dado** que o Neo ainda não tem tarefas
- **Quando** a página inicial carrega
- **Então** mostra quatro contadores, nesta ordem — "Hoje", "Esta semana", "Este mês", "Este ano" — todos com o número `0` e a legenda "tarefas"

### AC-3: Calendário do mês
- **Dado** a página inicial aberta
- **Quando** ela carrega
- **Então** mostra o calendário do mês atual com título no formato "novembro de 2026", semana começando no domingo (`dom.` a `sáb.`), dias de meses vizinhos esmaecidos para completar as semanas, o dia de hoje destacado, e nenhum item nos dias

### AC-4: Navegar no calendário
- **Dado** o calendário mostrando o mês atual
- **Quando** a pessoa clica em "›" (próximo), "‹" (anterior) ou "Hoje"
- **Então** o calendário vai para o mês seguinte, para o anterior ou volta ao mês atual, atualizando o título e a grade; os botões "‹" e "›" têm nome acessível ("Mês anterior", "Próximo mês")

### AC-5: Lista de Espaços reais
- **Dado** um Usuário cujo `GET /v1/me` devolve os Espaços "Neo" (`trabalho`) e "Faculdade" (`estudos`)
- **Quando** a página inicial carrega
- **Então** o cartão "Espaços" lista os dois na ordem de criação, cada um com o nome, a legenda "<Tipo> · sem tarefas ainda" e o ícone e a cor do Tipo de espaço:

| Tipo de espaço | Rótulo | Cor | Ícone |
|---|---|---|---|
| `trabalho` | Trabalho | `#00FFB2` | pasta |
| `estudos` | Estudos | `#38BDF8` | livro |
| `hobbies` | Hobbies | `#A78BFA` | brilho |
| `pessoal` | Pessoal | `#F472B6` | coração |

### AC-6: Próximas tarefas vazias
- **Dado** que o Neo ainda não tem tarefas
- **Quando** a página inicial carrega
- **Então** o cartão "Próximas tarefas" mostra "Nenhuma tarefa ainda. Crie a primeira para vê-la no calendário."

### AC-7: Layout responsivo
- **Dado** a página inicial
- **Quando** aberta em tela larga (≥ 1280 px)
- **Então** os contadores ficam em 4 colunas e o calendário fica à esquerda, com Espaços e Próximas tarefas numa coluna à direita;
- **e quando** aberta em tela estreita (< 768 px), contadores ficam em 2 colunas e calendário, Espaços e Próximas tarefas empilham em uma coluna, sem rolagem horizontal da página

## Casos de borda
- Nome de exibição ausente (não deveria ocorrer com Primeiro acesso concluído) → título "Olá" sem nome.
- Lista de Espaços vazia → o cartão mostra "Nenhum Espaço ainda."
- Nome de Espaço longo → cortado com reticências numa linha, nome completo no `title`.
- Virada de mês (ex.: 31/01 → fevereiro) → a navegação usa o 1º dia do mês e nunca pula um mês.

## Fora de escopo
> Vinculante.
- Tarefas, agenda e eventos reais (criar, listar, contar); itens no calendário.
- Visões "Dia", "Semana" e "Ano" do calendário (chegam junto com tarefas).
- Criar, editar ou abrir um Espaço (botões "+" e "Acessar" do protótipo); horas na semana por Espaço.
- Plano, créditos, botão flutuante de IA e o cartão de usuário do canto superior (o usuário já aparece no menu lateral).
- Alterar o menu lateral, a rota pós-login ou as demais páginas de exemplo do template.
- Nova rota ou mudança na API.

## Rastreabilidade
- Depende de: [0036 — login no painel](../0036-login-painel-web/spec.md), [0037 — API e primeiro acesso](../0037-api-fundacao-primeiro-acesso/spec.md) (`GET /v1/me`, `NeoAccessGuard`)
- ADRs: [ADR-0010](../../docs/architecture/adr/0010-painel-web-nextjs-com-clerk.md)
