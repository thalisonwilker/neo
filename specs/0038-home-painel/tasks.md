---
name: tasks
description: Decomposição e gates da feature 0038 (página inicial do painel).
alwaysApply: false
---

# Tasks — Página inicial do painel

> Cada task mapeia para um ou mais `AC-N` e tem um gate executável. Os comandos rodam dentro de `web/`.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Regras puras da home em `web/src/features/home/`: formatação da data de hoje, grade do mês (semana a partir do domingo, dias vizinhos, hoje), navegação de mês sem pular meses, perfil visual por Tipo de espaço e ordenação dos Espaços | AC-1, AC-3, AC-4, AC-5 | — | `cd web && npx vitest run src/features/home/home-rules.test.ts` | done |
| 2 | Componentes da home (`HomeView`, contadores, calendário do mês, cartão de Espaços, próximas tarefas) lendo o Usuário de `useUsuarioNeo()`, no visual do tema NEO, responsivos | AC-1 a AC-7 | 1 | `cd web && npx vitest run -t "0038"` | done |
| 3 | Trocar o conteúdo de exemplo de `/dashboard/overview` pela `HomeView` (remover as rotas paralelas de gráficos de exemplo) e verificar no navegador em tela larga e estreita | AC-7 | 2 | `cd web && npm run typecheck && npx oxlint && npx oxfmt --check src && npm run test && npx next build` | done |

> Uma task só vira `done` quando o **gate passa**.

## Plano de teste
- Unidade: data formatada, grade do mês (fev/2026 com 28 dias, mês começando no sábado), navegação 31/01 → fevereiro, perfil por tipo.
- Componente (aceite): um teste por AC-1 a AC-6 com `useUsuarioNeo` simulado e data fixa.
- AC-7: verificação no navegador (largura 1440 e 375), registrada no PR.

## Divergências (SPEC_DEVIATION)
- (nenhuma)

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável (AC-7 verificado no navegador em 1440 e 375 px, sem rolagem horizontal)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado
