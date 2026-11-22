---
name: design
description: Technical Design Doc da feature 0036 — fluxo de login do painel web com Clerk (5 eixos, alternativas, riscos).
alwaysApply: false
---

# Technical Design Doc — Fluxo de login do painel web

> **Tier:** arquitetural · **Status:** aprovado (22/11/2026)
> **Autor:** Thalyson Wilker (com agente) · **Revisores:** Thalyson Wilker · **Data:** 2026-11-22
> Responde: **como** no nível de sistema. Obrigatório no tier arquitetural.

## Links e artefatos

| Artefato                 | Onde        | Link                                         |
|--------------------------|-------------|----------------------------------------------|
| Página do design         | —           | nenhuma ferramenta de documentação conectada |
| Issue / épico            | —           | nenhuma ferramenta de gestão conectada       |
| Spec · Product · Domínio | repositório | `./spec.md` · `./product.md` · `./domain.md` |

## Contexto da funcionalidade
O painel web mora em `web/` (Next.js 16.4.6, React 19, shadcn/ui, Tailwind 4, tema NEO) e usa o Clerk (`@clerk/nextjs` 7.10.7) para login. Estado verificado no código em 22/11/2026:

- **Dois conjuntos de rotas de entrada.** As originais do template (`/auth/sign-in`, `/auth/sign-up`, com a view `features/auth/components/sign-in-view.tsx`, grade interativa, logo e depoimento de exemplo) e um segundo par (`/sign-in`, `/sign-up`) criado pelo `clerk init`.
- **Variáveis divergentes.** O `.env.local` gerado pelo init aponta para `/sign-in`, `/sign-up` e redireciona para `/` após entrar, enquanto o `env.example.txt` do template usa `/auth/...` e `/dashboard/overview`.
- **Proteção só no layout.** `web/src/app/dashboard/layout.tsx` chama `await auth.protect()`. O `proxy.ts` usa `clerkMiddleware()` sem bloquear nada. `app/page.tsx` redireciona conforme `userId`.
- **Dois `ClerkProvider`.** `app/layout.tsx` (adicionado pelo init, sem `appearance`) envolve `components/layout/providers.tsx`, que já tem um `ClerkProvider` com `appearance.variables` ligadas aos tokens do tema.
- **Sem testes.** O `web/` não tem ferramenta de teste; o `TESTING.md` cobre só o Python.

Problema de produto: ver `./product.md`.

## Goals / Non-goals
**Goals**
- Um único fluxo de entrada, cadastro e saída, com as rotas `/auth/sign-in` e `/auth/sign-up`.
- Métodos: Google, e-mail e senha, link mágico por e-mail e GitHub.
- Proteção de `/dashboard/*` e da API **no proxy e no layout** (defesa em profundidade), com retorno ao destino pedido.
- Telas em **português do Brasil**, sem textos de exemplo, com a identidade NEO.
- Um `ClerkProvider` só, e variáveis de ambiente coerentes com as rotas.
- Testes automatizados com Clerk simulado e um roteiro de UAT manual para o login real.

**Non-goals**
- Organizações, papéis, cobrança, 2FA, produção, vínculo com a CLI e autenticação própria (ver `product.md`).

## Glossário (da funcionalidade)

| Termo | Descrição |
|-------|-----------|
| **Painel** | Aplicação web do Neo em `web/`. Não é a CLI. |
| **Sessão do painel** | Estado autenticado do usuário no painel, mantido pelo Clerk. |
| **Rota protegida** | Rota que só responde com sessão válida; sem ela, redireciona para a entrada. |
| **Método de entrada** | Forma de provar identidade: Google, e-mail e senha, link mágico ou GitHub. |
| **Destino pós-login** | Página para onde o usuário vai depois de entrar: a pedida originalmente (`redirect_url`) ou `/dashboard/overview`. |
| **Instância de desenvolvimento** | Aplicação Clerk "Neo" criada para desenvolvimento, com chaves `pk_test`/`sk_test` e limites de uso. |

> **Atenção à linguagem ubíqua:** "workspace" no Neo é o escopo de repositórios do provedor Git (`docs/glossary.md`). Esta feature **não** usa as "Organizations" do Clerk e não usa "workspace" com outro sentido.

## Design proposto

### Fluxo de entrada
```text
Visitante ──► /dashboard/overview
                  │
          proxy.ts (clerkMiddleware + rota protegida?)
                  │ sem sessão
                  ▼
         /auth/sign-in?redirect_url=/dashboard/overview
                  │  <SignIn/> (pt-BR, tema NEO)
                  │  Google · e-mail+senha · link mágico · GitHub
                  ▼
              Clerk (SaaS) ── sessão criada ──► redirect_url
                                                   │
                                   /  ──► app/page.tsx ──► /dashboard/overview
```

### Cadastro e saída
- `/auth/sign-up` renderiza `<SignUp/>` com os mesmos métodos e visual.
- **Saída:** item "Sair" no menu do usuário da sidebar (`NavUser`, em `components/layout/app-sidebar.tsx`), via `useSignOut` de `features/auth`. Encerra a sessão no Clerk e volta para `/auth/sign-in`.

### Componentes e arquivos tocados
| Arquivo | Mudança |
|---|---|
| `web/.env.local` / `env.example.txt` | URLs de entrada/cadastro `/auth/...`; redirecionamento padrão `/dashboard/overview`. |
| `web/src/app/sign-in`, `web/src/app/sign-up` | **Removidos** (criados pelo init). |
| `web/src/app/layout.tsx` | Remove o `ClerkProvider` duplicado. |
| `web/src/components/layout/providers.tsx` | Único `ClerkProvider`, com `localization` pt-BR e a `appearance` existente. |
| `web/src/proxy.ts` | `createRouteMatcher` para `/dashboard(.*)` e rotas de API; `auth.protect()` no proxy. |
| `web/src/app/dashboard/layout.tsx` | Mantém `auth.protect()` como segunda camada. |
| `web/src/features/auth/components/*` | Remove "Logo" e o depoimento; marca NEO e a frase da visão ("Compreenda seus sistemas. Seja dono das suas escolhas."); textos em pt-BR. |

### Fronteiras
Nova fronteira: **Painel (web)**, ainda sem relação com os contextos Python. O Clerk entra como serviço externo (Generic). Nesta feature o uso do Clerk fica **restrito** a: `providers.tsx`, `proxy.ts`, `dashboard/layout.tsx`, `app/page.tsx` e `features/auth/`. Os usos de organizações e cobrança do template permanecem como estão e **não são ampliados**.

## Cobertura dos 5 eixos

### 1. Tech stack
- **Já presente:** `@clerk/nextjs` 7.10.7, Next.js 16.4.6, React 19.3, TypeScript.
- **Novas dependências:** `@clerk/localizations` (pacote oficial de traduções, para `ptBR`) e, só em desenvolvimento, **Vitest** com jsdom e Testing Library. Versões a fixar na implementação, conferidas no registro do npm.
- **Diverge do stack Python do Neo:** sim. É a primeira peça em TypeScript. Decisão estrutural → **ADR** (provedor de autenticação e painel web em Next.js).

### 2. Arquitetura base
Nova fronteira "Painel (web)" no `context-map.md`, independente da CLI. A proteção fica na borda (`proxy.ts`) e se repete no layout. A lógica de decisão (qual rota é protegida, como montar a URL de entrada com `redirect_url`) é extraída para funções puras em `web/src/features/auth/`, para poder ser testada sem o Clerk.

### 3. Infra
- Sem recurso novo no repositório. Configuração **manual e fora do código** no painel do Clerk da aplicação "Neo": habilitar os quatro métodos, URLs de entrada/cadastro e destino; registrar o resultado no `uat.md`.
- Segredos só em `web/.env.local` (já ignorado pelo git). `env.example.txt` documenta os nomes.
- **Reversão segura:** reverter o commit e restaurar as variáveis. Nenhum dado local é migrado.

### 4. Qualidade
- **Vitest + Clerk simulado** cobre: decisão de rota protegida, montagem do redirecionamento, coerência das variáveis de ambiente exigidas, ausência de textos de exemplo e textos em pt-BR nas telas. Nenhuma chamada externa real (respeita `TESTING.md`).
- **Roteiro de UAT manual** (`uat.md`) cobre o login real nos quatro métodos, saída e proteção, contra a instância de desenvolvimento.
- **Nomes:** `AC-N` no nome de cada teste, como no restante do projeto.
- **Gates do painel** (a registrar em `docs/engineering/TESTING.md`): `npm run typecheck`, `npx oxlint`, `npm run test`, `npx next build`. Os gates Python e `node scripts/audit-esteira.mjs .` continuam valendo.

### 5. Observabilidade
Sem impacto novo. O template traz Sentry (desligável por variável), fora do escopo. A prova de funcionamento é o UAT e o histórico de acessos no painel do Clerk.

## Mapa de dependências

| Dependência | Tipo | Descrição | Principais pontos |
|---|---|---|---|
| Clerk (SaaS) | serviço externo | Identidade, sessão e telas de entrada | `<SignIn/>`, `<SignUp/>`, `clerkMiddleware`, `createRouteMatcher`, `auth.protect()`, saída de sessão |
| Google e GitHub via Clerk | OAuth | Entrada social | Em desenvolvimento usam credenciais compartilhadas do Clerk |
| E-mail via Clerk | e-mail | Link mágico | Habilitado no painel do Clerk |
| `@clerk/localizations` | biblioteca | Textos em pt-BR | `ptBR` |
| Next.js `proxy.ts` | framework | Interceptação antes do render | `config.matcher` |
| Vitest | biblioteca (dev) | Testes unitários do painel | `npm run test` |

## Solução

| # | Bloco | Descrição | Status |
|---|---|---|---|
| 1 | Consolidar rotas | Remover `/sign-in` e `/sign-up`; manter `/auth/...` | definido |
| 2 | Variáveis de ambiente | URLs `/auth/...` e destino `/dashboard/overview` | definido |
| 3 | Provedor único | Remover `ClerkProvider` duplicado e aplicar `ptBR` | definido |
| 4 | Proteção no proxy | `createRouteMatcher` + `auth.protect()`; layout como segunda camada | definido |
| 5 | Telas de entrada e cadastro | Sem placeholders, marca NEO, pt-BR | definido |
| 6 | Saída de sessão | Item "Sair" no menu do usuário da sidebar | definido |
| 7 | Métodos no Clerk | Habilitar Google, e-mail e senha, link mágico e GitHub | definido (manual) |
| 8 | Cadastro aberto | Decisão do mantenedor: qualquer pessoa pode se cadastrar; restringir antes de conectar dados reais | definido |
| 9 | Testes e gates | Vitest, funções puras, `TESTING.md` | definido |
| 10 | Documentação viva | ADR, context-map, glossário, STATE | definido |

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que (não) escolhida |
|---|---|---|---|
| **A. Fechar o fluxo com Clerk (escolhida)** | Já instalado e funcionando; os quatro métodos sem código próprio; pouco risco de segurança caseiro | Dependência de SaaS; e-mails fora do controle local | Menor esforço e risco para o escopo pedido |
| B. Autenticação própria, local-first (ex.: biblioteca de auth + banco local) | Alinhada a "controle do usuário"; sem terceiros | Muito mais código sensível (senhas, sessão, link mágico); reimplementa o que já existe | Fora do escopo escolhido; reavaliar se a dependência virar problema |
| C. Clerk ligado à CLI | Uma identidade para painel e CLI | Mistura duas fronteiras antes de a primeira estar estável | Feature posterior |

## Trade-offs e consequências
Ganhamos entrega rápida e um login completo. Aceitamos depender de um serviço de terceiros e de configuração manual fora do repositório. Mantemos os usos de organização do template como dívida conhecida, sem ampliá-los.

## Riscos

| Risco | Descrição | Prob. × Impacto | Ações / mitigações |
|-------|-----------|-----------------|--------------------|
| Cadastro aberto | Qualquer pessoa cria conta e vê o painel (decisão aceita pelo mantenedor) | alto × médio | Aceitável só com dados de exemplo; **restringir antes de conectar dados reais** (ADR-0010) e registrar no UAT |
| Config fora do código | Métodos habilitados à mão se perdem ou divergem | médio × médio | Registrar o estado esperado no `uat.md` e checar a cada entrega |
| Chaves de desenvolvimento | Limites de uso e comportamento diferente de produção | alto × baixo | Declarar non-goal; feature própria para produção |
| Duas rotas de entrada ao mesmo tempo | Fluxos paralelos confundem e deixam rota sem proteção | médio × médio | Remover `/sign-in` e `/sign-up`; teste de coerência das variáveis |
| Conflito de termos | "workspace" e "organização" com sentidos diferentes | médio × baixo | Glossário e revisão de copy |

## Roadmap da feature

| Fase / onda | Entrega | Quando | Depende de |
|-------------|---------|--------|------------|
| 1 (MVP) | Fluxo completo com Clerk: rotas, proteção, visual, pt-BR, saída, testes e UAT | próximo ciclo | — |
| 2 | Instância de produção, 2FA e recuperação de conta | depois | 1 |
| 3 | Vínculo da sessão do painel com a CLI | depois | 1 e decisão de arquitetura própria |

## Questões em aberto
- [x] **1. Quem pode se cadastrar?** Decidido em 22/11/2026: **aberto a qualquer pessoa**. Consequência registrada no ADR-0010: rever antes de o painel exibir dados reais.
- [x] 2. O link mágico do Clerk em desenvolvimento chega como link ou como código? Verificado em 22/11/2026 (configuração pública da instância): hoje a verificação de e-mail é por **código**. Para o link, é preciso habilitar a verificação por link no painel do Clerk (passo C5 do `uat.md`).
- [x] 3. Qual componente do template faz a saída de sessão? Resolvido na tarefa 9: o item de saída de `NavUser` em `components/layout/app-sidebar.tsx`. O `UserNav` (`components/layout/user-nav.tsx`) não é usado em lugar nenhum.

> **ADR registrado:** [ADR-0010 — Painel web em Next.js com autenticação via Clerk](../../docs/architecture/adr/0010-painel-web-nextjs-com-clerk.md).
