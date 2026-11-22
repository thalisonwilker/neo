# Painel web do Neo

Painel em Next.js do Neo: entrada e cadastro pelo Clerk, Primeiro acesso, Boas-vindas, página inicial e
Minha conta. Os dados vêm da API do Neo (`GET /v1/me`), na raiz do repositório.

> Base: template [next-shadcn-dashboard-starter](https://github.com/Kiranism/next-shadcn-dashboard-starter)
> (MIT, ver `LICENSE`). As páginas de exemplo do template foram removidas na spec 0039; ficam a moldura do
> painel e os componentes base em `src/components/ui/`.

## Páginas

| Rota | O que é | Spec |
|---|---|---|
| `/auth/sign-in`, `/auth/sign-up` | Entrada e cadastro (Clerk, pt-BR) | 0036 |
| `/primeiro-acesso` | Nome de exibição e primeiro Espaço | 0037 |
| `/boas-vindas` | Boas-vindas depois do Primeiro acesso | 0037 |
| `/dashboard/overview` | Página inicial (Início) | 0038 |
| `/dashboard/profile` | Minha conta (tela de conta do Clerk) | 0039 |

## Rodar localmente

1. Suba a API do Neo na raiz do repositório (Postgres em Docker, migrations e `uvicorn` na porta 8000).
2. Copie `env.example.txt` para `.env.local` e preencha as chaves do Clerk e `NEXT_PUBLIC_NEO_API_URL`.
3. Instale e rode o painel na porta 3100 (a origem liberada no CORS da API):

```bash
npm ci
npm run dev -- -p 3100
```

## Gates

```bash
npm run typecheck && npx oxlint && npx oxfmt --check src && npm run test && npx next build
```

## Estrutura

```
src/
├── app/            # Rotas (App Router)
├── components/
│   ├── layout/     # Menu lateral, cabeçalho e provedores
│   ├── themes/     # Fontes e provedor do tema NEO (escuro, único)
│   └── ui/         # Componentes base (shadcn)
├── features/
│   ├── auth/       # Entrada, cadastro, acesso e saída (0036)
│   ├── onboarding/ # Guarda de acesso, Primeiro acesso e Boas-vindas (0037)
│   ├── home/       # Página inicial (0038)
│   └── profile/    # Minha conta
├── lib/api/        # Cliente da API do Neo
└── styles/         # Tailwind e tema NEO
```
