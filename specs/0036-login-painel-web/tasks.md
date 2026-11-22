---
name: tasks
description: Decomposição e gates da feature 0036 (fluxo de login do painel web).
alwaysApply: false
---

# Tasks — Fluxo de login do painel web

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e tem um gate executável.
> Marque `[P]` nas tasks que podem rodar em paralelo. Os comandos do painel rodam dentro de `web/`.
> Sem ferramenta de gestão conectada: a coluna de issue não se aplica.

## Plano

| #  | Task | Cobre AC | Depende de | Gate (comando) | Status |
|----|------|----------|------------|----------------|--------|
| 1  | Excluir o código do template em `web/` da auditoria da esteira, mantendo `specs/` e `docs/` auditados | AC-14 | — | `node scripts/audit-esteira.mjs .` | todo |
| 2  | Preparar testes no painel: instalar Vitest, jsdom e Testing Library, criar o script `test` e um teste de fumaça | AC-14 | — | `cd web && npm run test` | todo |
| 3  | Funções puras de acesso em `features/auth`: política de rota, URL de entrada com `redirect_url` e destino pós-login (com a rejeição de destinos inválidos) | AC-1, AC-2, AC-3, AC-4 | 2 | `cd web && npx vitest run src/features/auth -t "AC-1\|AC-2\|AC-3\|AC-4"` | todo |
| 4  | Consolidar rotas e variáveis: remover `src/app/sign-in` e `src/app/sign-up`; ajustar `env.example.txt` e `.env.local` (`/auth/...` e `/dashboard/overview`) `[P]` | AC-7 | 2 | `cd web && npx vitest run -t "AC-7"` | todo |
| 5  | Provedor único e pt-BR: instalar `@clerk/localizations`, remover o `ClerkProvider` de `app/layout.tsx` e aplicar `ptBR` em `providers.tsx` `[P]` | AC-8 | 2 | `cd web && npx vitest run -t "AC-8"` | todo |
| 6  | Proxy protegido: `createRouteMatcher` e `auth.protect()` em `proxy.ts` usando a política da task 3. Verificar como o Clerk responde a `/api` sem sessão (spike) | AC-1, AC-2 | 3 | `cd web && npx vitest run src/proxy -t "AC-1\|AC-2"` | todo |
| 7  | Layout e raiz: manter `auth.protect()` em `dashboard/layout.tsx` e fazer `app/page.tsx` decidir pela sessão | AC-5, AC-6 | 3 | `cd web && npx vitest run -t "AC-5\|AC-6"` | todo |
| 8  | Telas de entrada e cadastro: remover "Logo" e o depoimento, aplicar marca NEO, a frase da visão e textos em pt-BR `[P]` | AC-9 | 5 | `cd web && npx vitest run -t "AC-9"` | todo |
| 9  | Saída da sessão: localizar o menu do usuário no template e configurar o retorno a `/auth/sign-in` `[P]` | AC-12 | 4 | `cd web && npx vitest run -t "AC-12"` | todo |
| 10 | Habilitar os quatro métodos na aplicação Clerk "Neo" (manual) e escrever `uat.md` com o roteiro e o resultado | AC-10, AC-11, AC-12, AC-13 | 4, 5, 6, 8, 9 | `uat.md` preenchido, com cada item marcado como passou ou falhou e a data | todo |
| 11 | Documentação viva e gates finais: seção "Painel web" em `docs/engineering/TESTING.md`, `docs/STATE.md` e checagem completa | AC-14 | 1, 6, 7, 10 | `cd web && npm run typecheck && npx oxlint && npm run test && npx next build` e `uv run mkdocs build --strict` e `node scripts/audit-esteira.mjs .` | todo |

> Uma task só vira `done` quando o **gate passa** (comandos em `docs/engineering/TESTING.md`), não por inspeção visual. Um commit por task.
> A task 10 é a única com gate manual; é uma exceção consciente, porque a entrada real depende do serviço do Clerk.

## Plano de teste
- **Unidade (Vitest):** as funções puras da task 3, com tabelas de entradas válidas e inválidas, incluindo `https://evil.example`, `//evil.example`, `javascript:alert(1)`, vazio e rotas de entrada.
- **Componentes e configuração (Vitest, Clerk simulado):** proxy, layout, página raiz, telas de entrada e cadastro, provedor único e leitura das variáveis. Nenhuma chamada externa real.
- **Aceite:** um teste por `AC-N`, com o ID no nome (`AC-3: ...`), como no restante do projeto.
- **UAT manual (`uat.md`):** AC-10 a AC-13 contra a instância de desenvolvimento do Clerk, mais a confirmação do AC-2 e do AC-12 de ponta a ponta.

## Spikes e verificações abertas
- [ ] Task 6: o que `auth.protect()` devolve para uma requisição a `/api` sem sessão (o AC-2 exige resposta não 2xx e sem dados).
- [ ] Task 9: qual componente do template faz a saída da sessão e onde ele aparece.
- [ ] Task 10: o link mágico do Clerk em desenvolvimento chega como link ou como código.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência identificada.

## Checklist de Definition of Done
- [ ] Todos os AC verdes **pelo gate executável** (os de UAT, pelo `uat.md`)
- [ ] Nenhum `SPEC_DEVIATION` pendente
- [ ] ADR-0010 registrado (feito) e revisto se o cadastro for restringido
- [ ] Glossário e context-map atualizados (feito)
- [ ] Spec reflete o que foi construído
- [ ] `docs/STATE.md` atualizado (próximo passo e decisões)
- [ ] Cobertura mínima do projeto Python mantida (`uv run pytest --cov=neo --cov-fail-under=80`), pois a feature não altera o Python
