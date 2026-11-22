---
name: tasks
description: Decomposição e gates da feature 0040 (criar Espaço).
alwaysApply: false
---

# Tasks — Criar Espaço

> Cada task mapeia para um ou mais `AC-N` e tem um gate executável. Comandos do painel rodam dentro de `web/`.
> Sem ferramenta de gestão conectada: a coluna de issue não se aplica (pode ser adicionada com `/integracoes`).

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Domínio `identidade`: `NomeDoEspaco` 1–100, novo `MetaSemanal` (1–168), `TipoEspaco.meta_sugerida`, `Espaco` com `meta_semanal` e `agentes_sugeridos`, `Usuario.criar_espaco` com as invariantes 6–8; o campo do erro passa a ser informado por quem valida (`nome`/`tipo` na criação, `espaco.nome`/`espaco.tipo` no Primeiro acesso) | AC-1, AC-2, AC-3, AC-4, AC-6 | — | `uv run pytest tests/unit/domain/test_identidade.py -v && uv run mypy src` | done |
| 2 | Caso de uso `CriarEspaco` (log `EspacoCriado` sem nome nem e-mail) e `ConcluirPrimeiroAcesso` criando o Espaço com Meta sugerida e sem Agentes sugeridos; testes com repositório em memória | AC-1, AC-2, AC-4, AC-6 | 1 | `uv run pytest tests/unit/application/test_identidade_use_cases.py -v && uv run mypy src` | done |
| 3 | Persistência: migração `0002_espaco_meta_e_agentes` (nome 100, `meta_semanal` com CHECK e preenchimento pela Meta sugerida, `agentes_sugeridos`, `downgrade`), modelo ORM e `RepositorioDeUsuarios.adicionar_espaco` | AC-1, AC-5 | 1 | `uv run alembic upgrade head && uv run pytest tests/integration/test_identidade_db.py -v` | done |
| 4 | API: `POST /v1/espacos` (201, 422 por campo, 409 `primeiro_acesso_pendente`), `EspacoResponse` com `meta_semanal` e `agentes_sugeridos` | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 | 2, 3 | `uv run pytest tests/e2e/test_api_identidade.py tests/e2e/test_api_espacos.py -v && uv run ruff check . && uv run mypy src` | done |
| 5 | Painel `[P]`: perfil do tipo único em `features/espacos/perfis.ts` (substitui o da 0038), tipos do DTO e cliente `criarEspaco()` em `lib/api/` | AC-8, AC-10, AC-11, AC-13 | — | `cd web && npx vitest run src/features/espacos src/lib/api` | done |
| 6 | Painel: modal "Criar Espaço" e as entradas ("+" do cartão Espaços e "Novo Espaço" no menu lateral), com validação, envio, erros e cancelamento | AC-7, AC-8, AC-9, AC-10, AC-11, AC-12 | 5 | `cd web && npx vitest run -t "0040 AC-(7\|8\|9\|10\|11\|12)"` | done |
| 7 | Painel: dashboard `/dashboard/espacos/[id]`, "Espaço não encontrado", grupo "Espaços" no menu lateral e trilha do cabeçalho | AC-13, AC-14, AC-15 | 5 | `cd web && npx vitest run -t "0040 AC-(13\|14\|15)"` | done |
| 8 | Limite de 100 no Primeiro acesso: formulário do painel e atualização consciente da spec 0037 (AC-7) | AC-6 | 1, 4 | `cd web && npx vitest run -t "AC-12" && uv run pytest tests/e2e/test_api_identidade.py -v` | done |
| 9 | Gates finais, verificação no navegador (criar um Espaço de cada tipo) e docs vivas (`docs/STATE.md`, `docs/engineering/TESTING.md` se mudar) | AC-1 a AC-15 | 4, 6, 7, 8 | `uv run pytest --cov=neo --cov-fail-under=80 && uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run mkdocs build --strict && node scripts/audit-esteira.mjs . && (cd web && npm run typecheck && npx oxlint && npx oxfmt --check src && npm run test && npx next build)` | done |

> Uma task só vira `done` quando o **gate passa**. Um commit por task.

## Plano de teste
- **Unidade (domínio):** limites do nome (0, 1, 100, 101 após trim), MetaSemanal (0, 1, 168, 169), Meta sugerida por tipo, invariantes 6–8, campo do erro por contexto.
- **Unidade (aplicação):** `CriarEspaco` feliz, omitidos, Primeiro acesso pendente; `ConcluirPrimeiroAcesso` com meta sugerida.
- **Integração (Postgres):** migração sobe e desce; Espaço existente recebe a Meta sugerida; CHECK recusa meta fora da faixa.
- **E2E (API):** um teste por AC-1 a AC-6.
- **Painel (Vitest):** um teste por AC-7 a AC-15, com a API simulada; a matriz do perfil do tipo vira um `it.each` com as 4 linhas.
- **Navegador:** criar um Espaço de cada tipo e conferir o dashboard e o menu lateral.

## Divergências (SPEC_DEVIATION)
- [x] Task 1 · os value objects nomeiam o campo como no Primeiro acesso (`espaco.nome`) · resolução: `CriarEspaco` traduz para `nome`/`tipo`; domínio e 0037 sem mudança de contrato.
- [x] Task 7 · título da aba: o Next sobrescrevia `document.title` · resolução: tag `<title>` do React 19 no dashboard do Espaço (comportamento igual ao AC-13).

## Checklist de Definition of Done
- [x] Todos os AC verdes pelo gate executável (355 testes Python, cobertura 88,5%; 213 no painel; criação de um Espaço Estudos conferida no navegador em 1440 e 375 px)
- [x] Nenhum `SPEC_DEVIATION` pendente
- [x] ADRs de decisões difíceis de reverter registrados (nenhum previsto; ver `design.md`)
- [x] Glossário / context-map atualizados (glossário feito no gate de domínio)
- [x] Spec reflete o que foi construído; spec 0037 atualizada para o limite de 100
- [x] `docs/STATE.md` atualizado
