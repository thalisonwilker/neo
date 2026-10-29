---
name: design
description: Technical Design Doc do micro gerenciamento financeiro pessoal (neo fin) com persistência local SQLite.
alwaysApply: false
---

# Technical Design Doc — 0019 Micro Gerenciamento Financeiro (`neo fin`)

> **Tier:** arquitetural · **Status:** aprovado
> **Autor:** Antigravity · **Revisores:** Thalyson · **Data:** 2026-10-29
> Responde: **como** no nível de sistema. Obrigatório no tier arquitetural.

## Links e artefatos
| Artefato | Onde | Link |
|---|---|---|
| Spec · Product · Domínio | repositório | `./spec.md` · `./product.md` · `./domain.md` |

## Contexto da funcionalidade
O Neo evolui para além de tarefas e Git, iniciando a Onda 2 de funcionalidades voltadas à organização pessoal. O micro gerenciamento financeiro provê uma maneira ultrarrápida de registrar gastos e ganhos diários sem sair do terminal, com persistência relacional local segura em SQLite (`~/.config/neo/finance.db`).

## Goals / Non-goals
**Goals**
- Criar banco de dados SQLite local inicializado sob demanda em `~/.config/neo/finance.db`.
- Oferecer CRUD completo de contas/bancos (`neo fin bank`), categorias (`neo fin category`) e transações (`neo fin tx`).
- Oferecer atalhos ergonômicos de alta velocidade `neo fin expense` e `neo fin income`.
- Disponibilizar extrato consolidado e balanço mensal (`neo fin summary` / `neo fin balance`).
- Suportar `--json` em todos os comandos para automação e extração de dados.

**Non-goals**
- Conexão bancária via Open Finance ou webhooks.
- Multi-moeda dinâmica.
- Backup remoto ou sincronização em nuvem neste ciclo.

## Glossário (da funcionalidade)
| Termo | Descrição |
|---|---|
| `Account` | Conta bancária ou carteira que detém saldo. |
| `Category` | Classificação de despesa ou receita. |
| `Transaction` | Movimentação financeira registrada. |
| `Balance` | Saldo disponível calculado por conta ou consolidado. |

## Design proposto

### 1. Modelo de Dados Relacional (SQLite)
O banco local utiliza `PRAGMA foreign_keys = ON` e o seguinte esquema:

```sql
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    account_type TEXT NOT NULL DEFAULT 'checking',
    initial_balance REAL NOT NULL DEFAULT 0.0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    category_type TEXT NOT NULL CHECK(category_type IN ('expense', 'income')),
    is_default INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE(slug, category_type)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('expense', 'income')),
    amount REAL NOT NULL CHECK(amount > 0),
    description TEXT NOT NULL,
    date TEXT NOT NULL, -- ISO-8601 YYYY-MM-DD
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_tx_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_tx_category ON transactions(category_id);
```

### 2. Categorias Padrão Semeadas (Seed)
Na criação do banco, categorias iniciais são carregadas automaticamente se vazias:
- **Despesas:** `Alimentação`, `Moradia`, `Transporte`, `Lazer`, `Saúde`, `Educação`, `Outros`.
- **Receitas:** `Salário`, `Freelance`, `Investimentos`, `Outros`.

### 3. Estrutura de Camadas (DDD)
- `src/neo/integrations/finance_db.py`: Adaptador de persistência SQLite, conexões e migrações DDL.
- `src/neo/services/finance.py`: Serviços de domínio (cálculo de saldos, agregações mensais, validações de integridade).
- `src/neo/commands/finance.py`: Subcomandos Typer e renderizadores Rich (`neo fin`).

## Cobertura dos 5 eixos

### 1. Tech stack
- **Linguagem & Runtime:** Python >= 3.13.
- **Banco de Dados:** `sqlite3` da biblioteca padrão do Python (zero dependências adicionais).
- **CLI Framework:** Typer + Rich.

### 2. Arquitetura base
- Respeita rigorosamente a regra de dependências: `commands` → `services` → `integrations/finance_db`.
- Banco de dados encapsulado em caminho configurável para testes (`tests/` usam banco isolado em `tmp_path`).

### 3. Infra
- Arquivo SQLite salvo em `~/.config/neo/finance.db` com permissões `0600`.

### 4. Qualidade
- 100% dos fluxos testados com Pytest (unitário e E2E via `CliRunner`).
- Validação estrita com Mypy e formatação Ruff.

### 5. Observabilidade
- Códigos de saída consistentes com o padrão Neo: `0` para sucesso, `1` para erros de negócio, `2` para erros de uso, `4` para não encontrado.
- Logs em nível `DEBUG` para operações SQLite.

## Alternativas consideradas

| Alternativa | Prós | Contras | Por que (não) escolhida |
|---|---|---|---|
| **SQLite (escolhida)** | ACID, relacional, consultas agregadas SQL eficientes, nativo no Python. | Cria um arquivo `.db`. | Escolhida por robustez e velocidade. |
| **JSON / TOML** | Legível com editor de texto simples. | Péssimo para relatórios, queries por data, sem integridade referencial. | Rejeitada pelo risco de corrupção e baixa performance em muitas transações. |

## Roadmap da feature
- **Fase 1 (MVP Atual):** Gestão de contas, categorias, transações (despesas e receitas) e balanço consolidado mensal com CLI completa.
- **Fase 2:** Transferências entre contas e exportação CSV/OFX.
