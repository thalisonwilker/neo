---
name: tasks
description: Decomposição e gates da feature 0039 (painel só com o Neo).
alwaysApply: false
---

# Tasks — Painel só com o Neo

> Os comandos rodam dentro de `web/`.

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Remover as rotas de exemplo (`app/dashboard/*` de demonstração, `app/api/*`), as features, constantes, hooks e componentes que só elas usavam | AC-1, AC-6 | — | `npm run typecheck && npm run test` | done |
| 2 | Menu lateral e cabeçalho do Neo: marca NEO no topo, item "Início", menu do usuário com "Minha conta" e "Sair", cabeçalho só com recolher menu e trilha em pt-BR; página "Minha conta" | AC-2, AC-3, AC-4 | 1 | `npx vitest run -t "0039"` | done |
| 3 | Tema único NEO escuro e metadados do Neo: remover temas extras, seletor, botão claro/escuro e o cookie `active_theme` | AC-5 | 1 | `npx vitest run -t "0039" && npm run typecheck` | done |
| 4 | Dependências órfãs fora do `package.json`/lockfile e `web/README.md` descrevendo o painel do Neo | AC-7 | 1, 2, 3 | `npm ci && npm audit --omit=dev && npx next build` | done |
| 5 | Gates finais e verificação no navegador (menu, cabeçalho, Minha conta, 404 de uma rota removida) | AC-1 a AC-7 | 4 | `npm run typecheck && npx oxlint && npx oxfmt --check src && npm run test && npx next build` | done |

## Divergências (SPEC_DEVIATION)
- Task 3 · o tema NEO dependia do mapeamento `@theme` do Tailwind que vinha dentro dos temas removidos · resolução: bloco movido para `neo.css` (sem mudança de comportamento).
- AC-5 · títulos seguem o padrão já existente "<página> | NEO" (teste da 0036) · resolução: spec atualizada antes de codar.

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável (175 testes; menu, Minha conta e 404 conferidos no navegador)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] Spec reflete o que foi construído
- [x] `docs/STATE.md` atualizado (inclui o passo manual de desligar Organizations no Clerk)
