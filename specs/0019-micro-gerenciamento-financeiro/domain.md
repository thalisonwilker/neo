---
name: domain
description: Modelo DDD do módulo de micro gerenciamento financeiro pessoal (Financeiro).
alwaysApply: false
---

# Domain Model (DDD) — 0019 Micro Gerenciamento Financeiro

> Responde: qual a **linguagem** e o **modelo** do negócio.
> DDD tático dentro do bounded context. Termos aqui devem aparecer iguais no código.

## Bounded Context
**Financeiro (`Finance`)**: Subdomínio de suporte/vida pessoal (Onda 2 do roadmap do Neo). Responsável por contas bancárias, categorização e registro de receitas e despesas com integridade local.

## Linguagem ubíqua

| Termo | Definição | NÃO confundir com |
|---|---|---|
| **Conta / Banco (`Account`)** | Entidade que representa uma conta corrente, carteira física, poupança ou instituição financeira onde o dinheiro reside. | Provedor Git ou serviço de tarefas. |
| **Categoria (`Category`)** | Classificação semântica de uma movimentação (ex.: Alimentação, Moradia, Salário). Pertence a um tipo (receita ou despesa). | Workflow state de tasks. |
| **Transação (`Transaction`)** | Registro imutável de uma movimentação financeira (receita ou despesa), associada a uma conta, categoria, data e valor monetário. | Commit Git. |
| **Receita (`Income`)** | Transação com valor positivo que incrementa o saldo da conta. | Saldo inicial. |
| **Despesa (`Expense`)** | Transação com valor positivo que debita/reduz o saldo da conta. | Transferência interna. |
| **Saldo (`Balance`)** | Valor monetário consolidado resultante da soma do saldo inicial com receitas menos despesas. | Limite de crédito. |
| **Resumo (`Summary`)** | Agregação periódica (mensal ou total) das receitas, despesas, saldo líquido e distribuição por categoria. | Board de tarefas. |

## Agregados, entidades e value objects

### 1. Entidade / Agregado `Account`
- **Identificador:** `id: int` (autoincrement) e `slug: str` (identificador textual amigável único, ex.: `nubank`, `itau`, `carteira`).
- **Atributos:** `name: str`, `account_type: str` (checking, savings, investment, cash), `initial_balance: Decimal`, `created_at: datetime`.
- **Invariantes:**
  - `slug` deve ser único e não-vazio.
  - `initial_balance` é um valor decimal fixo com 2 casas de precisão.

### 2. Entidade `Category`
- **Identificador:** `id: int` e `slug: str` (ex.: `alimentacao`, `salario`).
- **Atributos:** `name: str`, `category_type: str` (`expense` ou `income`), `is_default: bool`.
- **Invariantes:**
  - `slug` deve ser único por tipo de categoria (`expense` ou `income`).

### 3. Entidade `Transaction`
- **Identificador:** `id: int`.
- **Atributos:**
  - `account_id: int` (FK para `Account`)
  - `category_id: int` (FK para `Category`)
  - `transaction_type: str` (`expense` ou `income`)
  - `amount: Decimal` (sempre positivo, >= 0.01)
  - `description: str`
  - `date: date` (ISO 8601: YYYY-MM-DD)
  - `created_at: datetime`
- **Invariantes:**
  - `amount` deve ser estritamente positivo (> 0).
  - Toda transação deve referenciar uma conta e uma categoria válidas.

## Relações com outros contextos
- **Isolamento de Domínio:** O contexto `Finance` é autocontido no dispositivo do usuário, persistindo dados em SQLite (`finance.db`) sem acoplamento a provedores Git ou serviços de tarefas.
