---
name: tasks
description: Decomposição e gates da feature 0037 (fundação da API e primeiro acesso).
alwaysApply: false
---

# Tasks — Fundação da API e primeiro acesso

> Decomposição da implementação. Cada task mapeia para um ou mais `AC-N` e tem um gate executável.
> Marque `[P]` nas tasks que podem rodar em paralelo. Os comandos do painel rodam dentro de `web/`.
> Sem ferramenta de gestão (Jira/Linear) conectada nesta sessão: a coluna de issue não se aplica (pode ser adicionada rodando `/integracoes`).

## Plano

| # | Task | Cobre AC | Depende de | Gate (comando) | Status |
|---|---|---|---|---|---|
| 1 | Infraestrutura local e extra `neo[api]`: adicionar extra opcional `api` no `pyproject.toml` (FastAPI, Uvicorn, SQLAlchemy 2, asyncpg, Alembic, PyJWT[crypto], pydantic-settings), `docker-compose.yml` com PostgreSQL 17 (dev + banco de teste separado), configurações em `src/neo/infrastructure/` e exemplo de variáveis de ambiente | AC-1, AC-9 | — | `uv sync --extra api && uv run pytest tests/unit/test_api_settings.py -v && uv run mypy src` | done |
| 2 | Domínio `identidade` `[P]`: modelar em `src/neo/domain/identidade/` as entidades `Usuario` e `Espaco`, value objects (`Email`, `NomeDeExibicao` 1–60, `NomeDoEspaco` 1–40, `TipoEspaco` com 4 valores fixos, `IdentidadeExterna`, `EmailAutorizado`), as 5 invariantes, exceções de domínio e portas (`RepositorioDeUsuarios`, `RepositorioDeListaDePermissao`, `VerificadorDeToken`, `LeitorDeEmailExterno`) sem importar framework nem I/O | AC-3, AC-4, AC-6, AC-7, AC-8 | — | `uv run pytest tests/unit/domain/test_identidade.py -v && uv run mypy src` | todo |
| 3 | Casos de uso em `application/identidade/`: implementar `ObterOuCriarUsuario`, `ConcluirPrimeiroAcesso` e `GerenciarListaDePermissao` dependendo apenas de `domain/`, com testes unitários usando repositórios em memória (inclui normalização de e-mail, usuário existente sem consultar Clerk após remoção da lista, idempotência e concorrência) | AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-10 | 2 | `uv run pytest tests/unit/application/test_identidade_use_cases.py -v && uv run mypy src` | todo |
| 4 | Persistência PostgreSQL (`infrastructure/db/`) e migration Alembic: engine/sessão async SQLAlchemy 2, modelos ORM (`usuarios` com `UNIQUE(clerk_user_id)`, `espacos`, `emails_autorizados`), repositórios concretos (transação atômica Usuário + Espaço, tratamento de corrida no primeiro pedido, health check) e migration inicial com `upgrade`/`downgrade` | AC-1, AC-3, AC-5, AC-6, AC-8, AC-10 | 1, 2 | `uv run alembic upgrade head && uv run pytest tests/integration/test_identidade_db.py -v` | todo |
| 5 | Adapter Clerk (`infrastructure/clerk/`) `[P]`: executar o spike curto sobre origem do e-mail principal no Clerk (Backend API `GET /v1/users/{user_id}` vs claim customizada) e implementar verificação local via JWKS (assinatura, `exp`, `iss`, `azp`, recarga única em `kid` desconhecido) e leitura de e-mail com erro `clerk_indisponivel` em falha/timeout; testes sem chamadas externas reais (chave de teste + `respx`) | AC-2, AC-3, AC-4, AC-5 | 1, 2 | `uv run pytest tests/integration/test_clerk_adapter.py -v && uv run mypy src` | todo |
| 6 | Interface FastAPI (`interfaces/api/`): app FastAPI, rotas `GET /health`, `GET /v1/me` e `POST /v1/primeiro-acesso`, dependência de autenticação Bearer, erros padronizados `{erro, mensagem}` em pt-BR (401, 403, 409, 422 com indicação de campo, 503), logs estruturados sem token nem e-mail completo (mascarado, ex.: `t***@gmail.com`) com contagem de 401/403 e CORS restrito a `NEO_API_CORS_ORIGINS` (padrão `http://localhost:3100`) | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9 | 3, 4, 5 | `uv run pytest tests/e2e/test_api_identidade.py -v && uv run ruff check . && uv run mypy src` | todo |
| 7 | CLI da Lista de permissão (`neo api`) e paridade de documentação `[P]`: criar `neo api permitir <email>`, `neo api permissoes` (com `--json`) e `neo api remover-permissao <email>` usando `GerenciarListaDePermissao`; atualizar `docs/cli/api/index.md`, `docs/cli/comandos.md`, `docs/cli/index.md`, `mkdocs.yml` e `expected_pages` em `tests/unit/test_docs_parity.py` | AC-10 | 3, 4 | `uv run pytest tests/e2e/test_api_allowlist_cli.py tests/unit/test_docs_parity.py -v && uv run mkdocs build --strict` | todo |
| 8 | Painel: cliente da API Neo e regras puras de direcionamento `[P]`: criar cliente em `web/src/lib/api/` (anexando token do Clerk e usando `NEXT_PUBLIC_NEO_API_URL`, documentada em `web/env.example.txt`); incluir `/primeiro-acesso` e `/boas-vindas` em `isProtectedPath` (`web/src/features/auth/access.ts`, preservando a suíte da 0036) e implementar funções puras cobrindo todas as 10 linhas da matriz de decisão de direcionamento | AC-11 | — | `cd web && npx vitest run -t "AC-11"` | todo |
| 9 | Painel: guarda de rotas protegidas, "Acesso não liberado" e "API indisponível": consultar `GET /v1/me` nas rotas protegidas (`/dashboard/*`, `/primeiro-acesso`, `/boas-vindas`), encerrando sessão em 401 (`/auth/sign-in`), exibindo "Acesso não liberado" com botão "Sair" em 403 sem vazar dados do painel, exibindo "Não foi possível falar com o Neo agora" com "Tentar de novo" em 5xx/falha de rede, e aplicando os redirecionamentos de primeiro acesso | AC-11, AC-14, AC-15 | 8 | `cd web && npx vitest run -t "AC-11\|AC-14\|AC-15"` | todo |
| 10 | Painel: telas `/primeiro-acesso` e `/boas-vindas`: formulário de Nome de exibição + Espaço (nome e 4 tipos fixos) chamando `POST /v1/primeiro-acesso`, botão desabilitado durante envio, erro 422 por campo, navegação para `/boas-vindas` com estado local de visita; tela `/boas-vindas` exibindo `"Boas-vindas, <nome de exibição>"`, nome do Espaço e botão para `/dashboard`, redirecionando direto para `/dashboard` em visitas futuras | AC-12, AC-13 | 9 | `cd web && npx vitest run -t "AC-12\|AC-13"` | todo |
| 11 | UAT ponta a ponta (Clerk + API + Postgres + Painel): configurar manualmente a lista de permissão no painel do Clerk (ADR-0011), rodar o fluxo real completo (e-mail autorizado, primeiro acesso, boas-vindas, revisita, e-mail bloqueado, remoção de e-mail mantendo usuário existente) e registrar em `specs/0037-api-fundacao-primeiro-acesso/uat.md` (gate manual documentado) | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-10, AC-11, AC-12, AC-13, AC-14 | 6, 7, 10 | `` `uat.md` preenchido com cada cenário marcado como passou ou falhou e a data `` | todo |
| 12 | Documentação viva e gates finais: adicionar seção da API em `docs/engineering/TESTING.md`, atualizar `docs/STATE.md` e executar a bateria completa (Python, cobertura ≥ 80%, Ruff, Mypy, MkDocs estrito, auditoria da esteira e gates do painel em `web/`) | AC-1 a AC-15 | 6, 7, 10, 11 | `uv run pytest --cov=neo --cov-report=term-missing --cov-fail-under=80 && uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run mkdocs build --strict && node scripts/audit-esteira.mjs . && (cd web && npm run typecheck && npx oxlint && npx oxfmt --check src vitest.config.mts vitest.setup.ts && npm run test && npx next build)` | todo |

> Uma task só vira `done` quando o **gate passa** (comandos em `docs/engineering/TESTING.md`) — não por inspeção visual. Um commit por task.

## Plano de teste
- **Unidade (`tests/unit/`):** invariantes e value objects do domínio `identidade` (normalização de e-mail, limites de caracteres 1–60 e 1–40, tipos de espaço fixos), além dos casos de uso com repositórios em memória (criação no primeiro pedido, usuário existente não consulta Clerk após remoção da lista, idempotência e concorrência).
- **Integração (`tests/integration/`):** repositórios concretos contra PostgreSQL real (contêiner de teste, transação atômica, `UNIQUE(clerk_user_id)`, rollback/health check) e adapter Clerk com tokens assinados por chave de teste e respostas HTTP simuladas com `respx` (zero chamadas externas reais).
- **Aceite — API e CLI (`tests/e2e/`):** `httpx.AsyncClient` contra o app FastAPI e `CliRunner` para os comandos `neo api`; um teste rastreável por `AC-N` (`test_AC_1_*`, etc.) com o ID no nome do teste.
- **Painel (Vitest):** regras puras da matriz de decisão de direcionamento (`AC-11`, 10 linhas), cliente da API, guarda de rotas protegidas (`AC-11`, `AC-14`, `AC-15`) e telas `/primeiro-acesso` e `/boas-vindas` (`AC-12`, `AC-13`) com Clerk e fetch simulados (`vi.mock`), zero chamadas externas reais.
- **UAT manual (`uat.md`):** fluxo real ponta a ponta integrando painel do Clerk (com lista de permissão manual), API FastAPI, PostgreSQL e painel Next.js.

## Spikes e verificações abertas
- [ ] Task 5: verificar na documentação do Clerk se o e-mail principal vem por Backend API (`GET /v1/users/{user_id}`) ou claim customizada no token de sessão.
- [ ] Task 8: inspecionar `web/src/lib/api-client.ts` (do template) antes de criar `web/src/lib/api/` e validar com `git check-ignore -v` (armadilha do `.gitignore` da raiz com `lib/`).
- [ ] Task 8: confirmar que incluir `/primeiro-acesso` e `/boas-vindas` em `isProtectedPath` preserva 100% dos testes da feature 0036 em `web/src/features/auth/access.test.ts`.

## Divergências (SPEC_DEVIATION)
- Nenhuma divergência identificada.

## Checklist de Definition of Done
- [ ] Todos os AC verdes **pelo gate executável** (incluindo UAT em `uat.md`)
- [ ] Cobertura mínima de 80% mantida no projeto Python
- [ ] Análise estática limpa (Ruff, Mypy estrito, typecheck/oxlint/oxfmt do painel)
- [ ] Nenhum `SPEC_DEVIATION` pendente
- [ ] ADR-0011 registrado e aceito
- [ ] Glossário e `docs/architecture/context-map.md` atualizados
- [ ] Spec reflete o que foi construído
- [ ] `docs/STATE.md` e `docs/engineering/TESTING.md` atualizados
