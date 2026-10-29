---
name: product
description: PRD-lite do módulo de micro gerenciamento financeiro pessoal (neo fin).
alwaysApply: false
---

# Product — 0019 Micro Gerenciamento Financeiro (`neo fin`)

> **Tier:** arquitetural · **Status:** aprovado · **Dono:** Thalyson
> Responde: **por quê** e **para quem**. Mantenha em 1 página.

## Problema
Desenvolvedores e profissionais técnicos que vivem no terminal frequentemente precisam registrar despesas rápidas do dia a dia (almoço, serviços de nuvem, assinaturas, freelances), mas enfrentam fricção ao trocar de contexto para planilhas pesadas ou aplicativos web/mobile lentos. Essa fricção resulta em falta de registro, perda de visibilidade sobre gastos mensais e descontrole orçamentário.

## Para quem
Desenvolvedores e usuários de terminal que buscam gerenciar finanças pessoais de forma ágil, privada e direta pela linha de comando, sem depender de nuvens externas ou logins de terceiros.

## Resultado esperado / métrica de sucesso
- **Tempo de registro de despesa:** < 2 segundos diretamente via comando de terminal (ex.: `neo fin expense add 45.00 "Almoço" -a nubank -c alimentacao`).
- **Visibilidade imediata:** Consulta de saldo e balanço mensal consolidado em um comando rápido (`neo fin summary` ou `neo fin balance`).
- **Privacidade total:** 100% dos dados armazenados localmente em SQLite seguro (`~/.config/neo/finance.db`).

## Goals
- Gerenciar bancos/contas (`neo fin bank`: `add`, `list`, `edit`, `rm`) com saldo inicial e saldo atual consolidado.
- Gerenciar categorias (`neo fin category`: `add`, `list`, `edit`, `rm`) para receitas e despesas com carga padrão inicial.
- Gerenciar transações (`neo fin tx`: `add`, `list`, `edit`, `rm`) com atalhos ergonômicos `neo fin expense` e `neo fin income`.
- Exibir resumo mensal consolidado e balanço (`neo fin summary` / `neo fin balance`) com total de entradas, saídas, saldo líquido e distribuição por categoria.
- Suporte a saída estruturada com `--json` para automações e dashboards.

## Non-goals
- Conexão direta com APIs bancárias (Open Finance / Open Banking) neste incremento.
- Suporte a multi-moeda e conversão cambial em tempo real (valores em Real / moeda única padrão).
- Importação/parsing de extratos bancários em formato OFX/PDF (previsto para onda futura).

## Riscos / premissas
- Premissa: O banco local SQLite é confiável, ACID e nativo no Python padrão, sem exigir instalação de bibliotecas externas pesadas ou serviços de background.
