---
name: TESTING
description: Comandos de gate e convenções de teste para o Neo.
alwaysApply: false
---

# TESTING — Como verificar o Neo

> **Fonte única dos comandos de gate** e das convenções de teste. É o que o **DoD**, a **CI** e os **agentes** consomem para provar que uma task/feature está pronta.

## Como rodar

| Nível | Comando | Quando |
|---|---|---|
| **Unidade** | `uv run pytest tests/unit -v` | Sempre durante desenvolvimento |
| **Integração** | `uv run pytest tests/integration -v` | Ao alterar adapters e clientes HTTP (com mocks `respx`) |
| **Aceite (CLI E2E)** | `uv run pytest tests/e2e -v` | Um teste por `AC-N` da spec via `CliRunner` |
| **Lint & Formatação** | `uv run ruff check . && uv run ruff format --check .` | Pré-commit / CI |
| **Análise Estática** | `uv run mypy src` | CI / Validação de types |
| **Cobertura** | `uv run pytest --cov=neo --cov-report=term-missing --cov-fail-under=80` | Validação de PR / CI |
| **Documentação Estrita** | `uv run mkdocs build --strict` | Ao alterar docs / CI |
| **Auditoria da Esteira** | `node scripts/audit-esteira.mjs .` | Ao criar/editar docs e specs / CI |

## Convenções
- Pirâmide: testes de unidade rápidos para lógica de análise e parsing; testes de integração para clientes de API com `respx` mockando respostas JSON; testes E2E executando o app Typer com `CliRunner`.
- **Cada `AC-N` da spec tem um teste de aceite que é o seu gate.** Nomeie o teste com o ID (`test_AC_1_*` / `AC-1: ...`) para rastreabilidade spec → teste.
- Zero chamadas externas reais para APIs durante a execução da suíte de testes.
- **Análise estática estrita:** Mypy configurado com checagem de tipos sem retorno `Any` não tipado.
- **Documentação viva e testada:** Toda alteração de comandos requer teste de paridade (`test_docs_parity.py`) e build estrito sem links quebrados.

## Gates (Definition of Done executável)
- Uma **task** só vira `done` quando o **Gate (comando)** dela em `tasks.md` passa.
- Uma **feature** só faz merge quando:
  1. `uv run ruff check .` passa sem warnings.
  2. `uv run ruff format --check .` passa.
  3. `uv run mypy src` passa sem erros de tipagem.
  4. Todos os testes de aceite (`AC-N`) passam.
  5. Cobertura mínima de 80% atingida.
  6. `uv run mkdocs build --strict` compila sem erros nem advertências.
  7. `node scripts/audit-esteira.mjs .` valida a integridade de frontmatter, links e specs.
  8. Se a feature toca o painel web (`web/`), os gates da seção abaixo também passam.

## Painel web (`web/`)

> Stack: Next.js + TypeScript, com autenticação via Clerk ([ADR-0010](../architecture/adr/0010-painel-web-nextjs-com-clerk.md)). Os comandos rodam **dentro de `web/`**.

| Nível | Comando | Quando |
|---|---|---|
| **Tipos** | `npm run typecheck` | Sempre durante o desenvolvimento |
| **Lint** | `npx oxlint` | Pré-commit / CI. Os avisos que já vêm do template são aceitos; **erros não** |
| **Formatação** | `npx oxfmt --check src vitest.config.mts vitest.setup.ts` | Pré-commit / CI (`npx oxfmt --write ...` corrige) |
| **Testes** | `npm run test` | Sempre (Vitest + jsdom + Testing Library). `npm run test:watch` em desenvolvimento |
| **Um critério** | `npx vitest run -t "AC-3"` | Gate de uma task: roda só os testes com o ID do critério |
| **Build** | `npx next build` | Ao fechar uma feature do painel |
| **Dependências** | `npm audit` | Ao instalar ou atualizar pacotes (alvo: 0 vulnerabilidades) |

### Convenções do painel
- **Um teste por `AC-N`**, com o ID no nome (`AC-3: ...`), ao lado do código (`*.test.ts` e `*.test.tsx`), como no Python.
- **Zero chamadas externas reais:** o Clerk e os cabeçalhos do Next são simulados com `vi.mock`. Rotas e componentes de servidor rodam com `// @vitest-environment node`.
- **Regra de negócio em funções puras**, sem Clerk e sem Next, dentro de `features/<área>/` (ex.: `features/auth/access.ts`). A borda (proxy, layout, páginas) só as chama.
- **Exceção documentada:** o login real contra o Clerk **não** é automatizado. Ele é verificado por um roteiro manual de UAT (`specs/NNNN-*/uat.md`), porque depende de um serviço externo e de credenciais.
- **Escreva o teste antes** e confira que ele falha pelo motivo certo.
- `web/` fica **fora** da auditoria da esteira (`scripts/audit-esteira.mjs`): é um template de terceiros. As specs e os docs do painel continuam em `specs/` e `docs/`.

### Armadilhas conhecidas
- O `.gitignore` da raiz ignora qualquer pasta `lib/`. `web/src/lib/` só é versionada por causa da exceção `!/src/lib/` em `web/.gitignore`. Confira com `git check-ignore -v <caminho>` antes de criar pastas novas em `web/`.
- `web/.env.local` (chaves do Clerk) nunca entra no git. Os nomes das variáveis ficam em `web/env.example.txt`.
- Depois de remover uma rota, o `tsc` pode acusar erro em `.next/dev/types/validator.ts` (cache gerado pelo `next dev`). Apague esse arquivo; o `next dev` o recria.
