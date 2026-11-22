---
name: adr-0011
description: API do Neo em FastAPI com PostgreSQL, validando o token do Clerk e com cadastro restrito por lista de permissão.
alwaysApply: false
---

# ADR-0011: API do Neo em FastAPI com PostgreSQL

- **Status:** aceito
- **Data:** 2026-11-22
- **Decisores:** Thalyson Wilker (mantenedor do Neo)

## Contexto
O painel web (ADR-0010, feature 0036) tem login pelo Clerk, mas nenhum backend: as rotas de API são dados de exemplo e não existe usuário do Neo. O objetivo é um painel completo de gerenciamento de projetos, que precisa de persistência e de uma API.

Fatos: a CLI já usa Python 3.13, Pydantic e `httpx` (ADR-0002) e tem contratos de provedores Git e de tarefas (ADR-0009). O painel já tem telas, formulários e login. O ADR-0010 aceitou cadastro aberto só enquanto não houvesse dados reais.

## Decisão
Vamos criar a **API do Neo em FastAPI**, no mesmo pacote `neo` (`src/neo/interfaces/api`, extra opcional `neo[api]`), com **PostgreSQL**, **SQLAlchemy 2** e **Alembic**, seguindo as camadas `interfaces → application → domain ← infrastructure`.

- A identidade continua no **Clerk**: a API valida o token de sessão localmente pela chave pública (JWKS) e cria o usuário do Neo no primeiro pedido.
- O **cadastro passa a ser restrito** por uma lista de permissão de e-mails na API, editada pelo comando `neo api permitir`, e também pela lista de permissão do próprio Clerk (configuração manual). Isso substitui a parte do ADR-0010 que aceitava cadastro aberto.

Alternativas descartadas:
- **Django com DRF (monólito modular):** ORM, admin e permissões prontos, mas duplica o que o Next.js e o Clerk já fazem e não reaproveita os modelos Pydantic da CLI.
- **Rotas de API do Next.js:** um runtime só, mas a lógica ficaria em TypeScript, longe do domínio Python.
- **Autenticação própria na API:** dispensa o Clerk, mas exige código sensível que o ADR-0010 já evitou.

## Consequências
- **+** CLI e API compartilham domínio e casos de uso; OpenAPI gera tipos para o painel.
- **+** Autorização testável no repositório; dados reais protegidos por lista de permissão.
- **−** Mais dois processos em desenvolvimento (API e PostgreSQL).
- **−** A estrutura de camadas nova convive com a antiga da CLI até uma migração.
- **−** Dependência do Clerk se estende ao backend (JWKS e Backend API).
