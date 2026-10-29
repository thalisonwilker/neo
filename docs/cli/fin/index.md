---
name: cli-fin-index
description: Visão geral do micro gerenciamento financeiro pessoal local com SQLite (neo fin).
alwaysApply: false
---

# neo fin
> Micro gerenciamento financeiro pessoal ultrarrápido com persistência local SQLite.

O módulo `neo fin` permite controlar despesas diárias, registrar receitas, acompanhar saldos por conta e analisar o extrato mensal consolidado diretamente do terminal, com segurança, total privacidade e armazenamento local em banco SQLite (`~/.config/neo/finance.db`).

---

## Sintaxe Geral

```bash
neo fin <subcomando> [argumentos] [--opções]
```

Atalhos rápidos para registro de movimentações:
```bash
neo fin expense <valor> <descrição> [-a <conta>] [-c <categoria>] [-d <YYYY-MM-DD>]
neo fin income <valor> <descrição> [-a <conta>] [-c <categoria>] [-d <YYYY-MM-DD>]
```

---

## Submenus e Funcionalidades

O gerenciamento financeiro do Neo é estruturado em submenus modulares:

### 1. Bancos e Contas
- [**Contas Bancárias e Carteiras (`neo fin bank`)**](bank.md): Cadastro, edição, remoção e listagem de contas (`checking`, `savings`, `investment`, `credit`, `cash`).

### 2. Categorias
- [**Categorias (`neo fin category`)**](category.md): Gestão de categorias personalizadas de despesas e receitas com categorias padrão semeadas no primeiro uso.

### 3. Transações e Atalhos
- [**Transações (`neo fin tx`)**](tx.md): Extrato detalhado com filtros por data, conta, categoria e tipo, além de atalhos ergonômicos `neo fin expense` e `neo fin income`.

### 4. Balanço e Resumos
- [**Balanço e Resumo Mensal (`neo fin balance` e `neo fin summary`)**](summary.md): Visão consolidada de patrimônio por conta e detalhamento mensal de gastos por categoria.

---

## Saída Estruturada (`--json`)

Assim como toda a CLI Neo, todos os comandos do módulo financeiro suportam a flag `--json` para integração com scripts e automações:

```bash
neo fin balance --json
neo fin summary --month 2026-10 --json
```

---

## Veja também
- [Conceitos Gerais da CLI](../index.md)
- [Uso em CI com --json](../../guias/ci-json.md)
- [Glossário de Termos](../../glossary.md)
