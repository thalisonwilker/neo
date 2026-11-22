---
name: domain
description: Modelo DDD da feature 0036 — acesso e sessão do painel web (linguagem, invariantes, eventos).
alwaysApply: false
---

# Domain Model (DDD) — Acesso e sessão do painel web

> Responde: qual a **linguagem** e o **modelo** do negócio.
> DDD tático dentro do bounded context. Termos aqui devem aparecer iguais no código.

## Bounded Context
**Painel Web (Acesso)** — subdomínio **generic**. Identidade, credenciais e sessão são comprados prontos (Clerk). O Neo só é dono das **regras de acesso do painel**: quais rotas exigem sessão e para onde o usuário vai depois de entrar.

## Linguagem ubíqua
> Promovida ao `docs/glossary.md`.

| Termo | Definição | NÃO confundir com |
|-------|-----------|-------------------|
| **Painel** | Aplicação web do Neo em `web/` | A CLI `neo` |
| **Sessão do painel** | Estado autenticado do usuário no painel, mantido pelo Clerk | Sessão de terminal ou credencial da CLI no Keyring |
| **Rota protegida** | Rota do painel que só responde com sessão válida | Rota pública de entrada ou cadastro |
| **Método de entrada** | Forma de provar identidade: Google, e-mail e senha ou link mágico | Provedor Git do Neo (`github` e `bitbucket`) |
| **Destino pós-login** | Caminho interno para onde o usuário vai depois de entrar | URL externa informada em parâmetro |
| **Saída** | Encerramento da sessão do painel | Remoção da conta |

## Agregados, entidades e value objects
O estado de identidade vive no Clerk. O Neo modela só duas regras puras, sem persistência própria:

- **Política de acesso** (regra pura, sem estado)
  - Entrada: um caminho de rota.
  - Saída: `protegida` ou `pública`.
  - **Invariantes:** todo caminho sob `/dashboard` e toda rota de API é protegida; `/auth/sign-in` e `/auth/sign-up` são sempre públicas.
- **Destino pós-login** (value object)
  - Valor: caminho interno.
  - **Invariantes:**
    - começa com um único `/` e é relativo à mesma origem;
    - não começa com `//` nem contém esquema (`http:`, `javascript:`), exceto uma URL absoluta da **mesma origem**, que é reduzida a caminho e consulta (o Clerk gera `redirect_url` absoluto);
    - não contém barra invertida nem caractere de controle e tem no máximo 2048 caracteres;
    - não aponta para `/auth/sign-in` nem `/auth/sign-up` (evita laço);
    - se for inválido ou ausente, vale o padrão `/dashboard/overview`.
  - Existe para impedir redirecionamento aberto para fora do painel.

## Eventos de domínio
| Evento (passado) | Disparado quando | Quem reage |
|------------------|------------------|------------|
| `AcessoNegado` | Pedido a rota protegida sem sessão válida | Proxy: redireciona para `/auth/sign-in` com o destino pós-login |
| `UsuarioEntrou` | Clerk conclui a entrada por qualquer método | Redirecionamento para o destino pós-login |
| `CadastroConcluido` | Clerk conclui o cadastro | Redirecionamento para o destino pós-login |
| `UsuarioSaiu` | Usuário escolhe sair | Redirecionamento para `/auth/sign-in` |

Os três últimos são eventos do Clerk; o Neo só reage a eles, não os emite.

## Relações com outros contextos
- **Clerk (serviço externo):** o Painel é **Conformist** quanto ao modelo de identidade. O uso do Clerk fica restrito a `providers.tsx`, `proxy.ts`, `dashboard/layout.tsx`, `app/page.tsx` e `features/auth/`.
- **CLI & Commands, Configuration & Secrets e demais contextos Python:** sem relação nesta feature. O vínculo da sessão do painel com a CLI é uma feature futura.
- Atualizado em `docs/architecture/context-map.md`.
