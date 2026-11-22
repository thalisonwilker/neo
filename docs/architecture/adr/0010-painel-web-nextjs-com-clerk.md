---
name: adr-0010
description: Painel web em Next.js com autenticação delegada ao Clerk.
alwaysApply: false
---

# ADR-0010: Painel web em Next.js com autenticação via Clerk

- **Status:** aceito
- **Data:** 2026-11-22
- **Decisores:** Thalyson Wilker (mantenedor do Neo)

## Contexto
O Neo é uma CLI em Python (ADR-0002). Surgiu a necessidade de um painel web para visualizar tarefas, calendário e workspaces. Foi instalado em `web/` um template gratuito (Kiranism next-shadcn-dashboard-starter, licença MIT) com Next.js 16, shadcn/ui e Tailwind 4, já integrado ao Clerk para autenticação, e foi aplicado o tema NEO.

O painel é um **novo bounded context** e a **primeira peça em TypeScript** do repositório. O login precisa de métodos de entrada (Google, e-mail e senha, link mágico e GitHub), sessão e proteção de rotas. Implementar isso do zero é caro e sensível a segurança. A visão do produto pede preservar o controle do usuário e não guardar credenciais de forma insegura (ADR-0004).

Fatos verificados: o template usa o Clerk em rotas, proxy, layout e organizações; as chaves em uso são de uma instância de desenvolvimento.

## Decisão
Vamos manter o painel em Next.js em `web/` e **delegar identidade e sessão ao Clerk**, limitando o uso do Clerk a `providers.tsx`, `proxy.ts`, `dashboard/layout.tsx`, `app/page.tsx` e `features/auth/`.

Alternativas descartadas:
- **Autenticação própria, local-first:** alinhada ao controle do usuário, mas implica código sensível (senhas, sessão, link mágico) e reimplementar o que já funciona. Reavaliar se a dependência do Clerk virar problema.
- **Clerk ligado à CLI Neo:** mistura duas fronteiras antes de a primeira estar estável. Fica para uma feature posterior com decisão própria.

O cadastro fica **aberto a qualquer pessoa**, por decisão do mantenedor. Isso é aceitável enquanto o painel exibir apenas dados de exemplo. **Antes de conectar dados reais, o cadastro deve ser restringido** (lista de permissão ou convite) e esta decisão deve ser revista.

## Consequências
- **+** Login completo e seguro sem código sensível próprio; entrega rápida.
- **+** Fronteira clara: o uso do Clerk fica restrito a poucos arquivos.
- **−** Dependência de um serviço de terceiros; e-mails e identidades ficam fora do controle local.
- **−** Configuração manual no painel do Clerk, fora do repositório.
- **−** Stack TypeScript nova, com gates de qualidade próprios que precisam entrar no `TESTING.md`.
- **−** Cadastro aberto expõe o painel a qualquer pessoa até a restrição ser aplicada.
