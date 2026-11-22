---
name: spec
description: Contrato da feature 0036 — fluxo de login do painel web (critérios de aceite).
alwaysApply: true
---

# Spec — Fluxo de login do painel web

> **Fonte da verdade.** Status: em review · Tier: arquitetural.
> Os critérios de aceite são (a) o contrato com o negócio, (b) o oráculo de teste, (c) o prompt para o agente de IA implementar.

## Resumo
O painel web passa a ter um fluxo único de entrada, cadastro e saída com Clerk (Google, e-mail e senha, link mágico e GitHub), com todas as telas do `/dashboard` e da API protegidas no proxy e no layout, em português do Brasil e com a identidade NEO.

## Critérios de aceite

> **Verificação:** `Vitest` = teste automatizado com Clerk simulado (sem chamadas externas); `UAT` = roteiro manual em `./uat.md` contra a instância de desenvolvimento do Clerk.

### AC-1: Política de acesso por rota — Vitest
- **Dado** a política de acesso do painel,
- **Quando** ela classifica um caminho,
- **Então** todo caminho sob `/dashboard` e toda rota sob `/api` é **protegido**,
- **E** `/auth/sign-in` e `/auth/sign-up` são **públicos**.

### AC-2: Acesso sem sessão leva à entrada com o destino — Vitest e UAT
- **Dado** um visitante sem sessão,
- **Quando** ele pede `/dashboard/kanban`,
- **Então** é redirecionado para `/auth/sign-in?redirect_url=%2Fdashboard%2Fkanban`,
- **E** nenhum conteúdo da página protegida é enviado.
- **Dado** uma requisição a uma rota de API sem sessão, **então** a resposta **não** é 2xx e não traz dados protegidos (a API não redireciona).

### AC-3: Destino pós-login válido e padrão — Vitest
- **Dado** um `redirect_url` que seja um caminho interno (ex.: `/dashboard/kanban`, `/dashboard/chat?tab=1`),
- **Quando** a entrada ou o cadastro termina,
- **Então** o usuário vai para esse caminho.
- **Dado** `redirect_url` ausente, **então** o destino é `/dashboard/overview`.
- **Dado** uma URL absoluta da **mesma origem** (formato que o Clerk gera, ex.: `http://localhost:3100/dashboard/kanban?x=1`), **então** o destino é o caminho e a consulta dela (`/dashboard/kanban?x=1`).

### AC-4: Destino pós-login inválido é ignorado — Vitest
- **Dado** um `redirect_url` como `https://evil.example`, `//evil.example`, `javascript:alert(1)`, `/\evil.example`, vazio, com caractere de controle (como tabulação), com mais de 2048 caracteres, de **outra origem**, ou que aponte para `/auth/sign-in` ou `/auth/sign-up` (inclusive suas etapas),
- **Quando** o destino pós-login é calculado,
- **Então** ele é descartado e o destino passa a ser `/dashboard/overview` (sem sair do painel e sem laço de redirecionamento).

### AC-5: A raiz `/` decide pela sessão — Vitest
- **Dado** uma sessão ativa, **quando** o usuário abre `/`, **então** vai a `/dashboard/overview` sem nenhuma interação.
- **Dado** nenhuma sessão, **quando** abre `/`, **então** vai a `/auth/sign-in`.

### AC-6: Defesa em profundidade no layout — Vitest
- **Dado** que o proxy não barrou a requisição (ou foi contornado),
- **Quando** o layout do `/dashboard` renderiza sem sessão,
- **Então** ele exige autenticação por conta própria (`auth.protect()`) e não renderiza o conteúdo.

### AC-7: Configuração coerente e rotas únicas — Vitest
- **Dado** a configuração do painel,
- **Então** a URL de entrada é `/auth/sign-in`, a de cadastro é `/auth/sign-up` e o destino padrão após entrar ou cadastrar é `/dashboard/overview`, em `env.example.txt` e na leitura das variáveis,
- **E** as rotas `/sign-in` e `/sign-up` **não existem** no painel.

### AC-8: Provedor único e português do Brasil — Vitest
- **Dado** a árvore de componentes do painel,
- **Então** existe **um único** `ClerkProvider` (o de `providers.tsx`) e `app/layout.tsx` não importa o Clerk,
- **E** o provedor aplica a localização `ptBR`.

### AC-9: Telas de entrada e cadastro sem placeholders — Vitest
- **Dado** as telas `/auth/sign-in` e `/auth/sign-up`,
- **Quando** renderizadas,
- **Então** não contêm o texto "Logo" nem o depoimento do template,
- **E** exibem a marca NEO e a frase "Compreenda seus sistemas. Seja dono das suas escolhas.",
- **E** os títulos e textos próprios estão em português do Brasil.

### AC-10: Quatro métodos de entrada — UAT
- **Dado** a aplicação Clerk "Neo" com os métodos habilitados,
- **Quando** o usuário abre `/auth/sign-in`,
- **Então** vê **Google, GitHub, e-mail e senha e link mágico por e-mail**,
- **E** cada método, completado com sucesso, leva ao destino pós-login.

### AC-11: Cadastro aberto — UAT
- **Dado** um visitante sem conta,
- **Quando** conclui `/auth/sign-up` por qualquer um dos quatro métodos,
- **Então** a conta é criada e ele chega a `/dashboard/overview`,
- **E** não há restrição por e-mail (decisão registrada no ADR-0010).

### AC-12: Saída da sessão — Vitest e UAT
- **Dado** uma sessão ativa,
- **Quando** o usuário escolhe "Sair" no menu do usuário,
- **Então** a sessão é encerrada e ele vai a `/auth/sign-in`,
- **E** voltar a `/dashboard/overview` exige entrar de novo.
- (Vitest cobre o destino configurado da saída; o encerramento real é UAT.)

### AC-13: Erros claros em português — UAT
- **Dado** credencial inválida, link mágico expirado ou método indisponível,
- **Quando** o Clerk recusa a tentativa,
- **Então** a tela mostra mensagem clara em português do Brasil, sem detalhes técnicos internos.

### AC-14: Gates do painel passam — comandos
- **Dado** o código da feature,
- **Quando** rodam `npm run typecheck`, `npx oxlint`, `npm run test` e `npx next build` dentro de `web/`,
- **Então** todos passam sem erros,
- **E** esses comandos estão documentados em `docs/engineering/TESTING.md`.

## Matriz de decisão

| Sessão | Caminho pedido | Resultado esperado | AC |
|--------|----------------|--------------------|----|
| sem sessão | `/dashboard/*` | redireciona a `/auth/sign-in?redirect_url=<caminho>` | AC-2 |
| sem sessão | `/api/*` | resposta não 2xx, sem dados | AC-2 |
| sem sessão | `/auth/sign-in`, `/auth/sign-up` | exibe a tela | AC-1 |
| sem sessão | `/` | redireciona a `/auth/sign-in` | AC-5 |
| com sessão | `/` | redireciona a `/dashboard/overview` | AC-5 |
| com sessão | `/dashboard/*` | exibe a página | AC-1 |
| qualquer | layout `/dashboard` sem sessão (proxy contornado) | exige autenticação, não renderiza | AC-6 |
| qualquer | `redirect_url` externo, `//`, esquema ou rota de entrada | ignora e usa `/dashboard/overview` | AC-4 |
| qualquer | `redirect_url` interno válido | vai ao caminho | AC-3 |

## Casos de borda e erros
- **Sessão expira durante o uso:** o próximo pedido a rota protegida segue o AC-2.
- **Clerk indisponível ou chaves ausentes:** o painel **falha fechado**: não exibe conteúdo protegido e mostra erro de configuração (comportamento do template).
- **`redirect_url` com consulta** (`?a=1`): aceito; fragmento (`#...`) é descartado.
- **Rotas antigas** `/sign-in` e `/sign-up`: não existem; quem as acessar recebe a página de não encontrado.
- **Cadastro aberto:** qualquer pessoa pode criar conta. Aceito enquanto o painel exibe só dados de exemplo; **restringir antes de conectar dados reais** (ADR-0010).

## Fora de escopo
> Vinculante. Não implemente nada aqui.
- Organizações, papéis, permissões e cobrança do Clerk.
- Autenticação em dois fatores e recuperação avançada de conta.
- Instância de produção do Clerk e deploy do painel.
- Vínculo da sessão do painel com a CLI Neo (Keyring, `config.toml`).
- Conectar GitHub, Bitbucket ou Shortcut ao painel como fonte de dados.
- Restringir o cadastro por e-mail ou convite.
- Qualquer alteração no código Python da CLI.

## Rastreabilidade
- Product: `./product.md`
- Design: `./design.md`
- Domínio: `./domain.md`
- ADRs relacionados: [ADR-0010](../../docs/architecture/adr/0010-painel-web-nextjs-com-clerk.md)
