---
name: cli-fin-tx
description: Registro e extrato de transações financeiras com neo fin tx, expense e income.
alwaysApply: false
---

# neo fin tx
> Registro de movimentações financeiras, filtros de extrato e atalhos de alta velocidade.

O Neo oferece um gerenciador de transações completo via `neo fin tx` e atalhos instantâneos `neo fin expense` e `neo fin income` para registrar despesas e receitas do dia a dia com um único comando.

---

## Atalhos Rápidos

### `neo fin expense`
Atalho ergonômico para registrar uma despesa.

```bash
neo fin expense <valor> <descrição> [-a <conta>] [-c <categoria>] [-d <YYYY-MM-DD>] [--json]
```

**Exemplo:**
```bash
neo fin expense 45.90 "Almoço no restaurante" -a nubank -c alimentacao
```

---

### `neo fin income`
Atalho ergonômico para registrar uma receita.

```bash
neo fin income <valor> <descrição> [-a <conta>] [-c <categoria>] [-d <YYYY-MM-DD>] [--json]
```

**Exemplo:**
```bash
neo fin income 5000.00 "Salário do mês" -a nubank -c salario
```

---

## Subcomando `neo fin tx`

### `neo fin tx create`
Registra uma transação genérica informando explicitamente o tipo (`expense` ou `income`) (alias: `neo fin tx add`).

```bash
neo fin tx create <valor> <descrição> --type <expense|income> [-a <conta>] [-c <categoria>] [-d <YYYY-MM-DD>] [--json]
```

**Exemplo:**
```bash
neo fin tx create 120.00 "Internet Residencial" --type expense -a inter -c moradia
```

---

### `neo fin tx get`
Exibe os detalhes de uma transação específica pelo ID (alias: `neo fin tx show`).

```bash
neo fin tx get <id> [--json]
```

**Exemplo:**
```bash
neo fin tx get 12
```

---

### `neo fin tx list`
Lista o extrato de transações com opções flexíveis de filtros.

```bash
neo fin tx list [--month YYYY-MM] [-a <conta>] [-c <categoria>] [-t <expense|income>] [--limit <N>] [--json]
```

**Opções de Filtro:**
- `--month`, `-m`: Filtra transações ocorridas em determinado mês (ex: `2026-10`).
- `--account`, `-a`: Filtra pelo slug da conta (ex: `nubank`).
- `--category`, `-c`: Filtra pelo slug da categoria (ex: `alimentacao`).
- `--type`, `-t`: Filtra por tipo (`expense` ou `income`).
- `--limit`, `-l`: Quantidade máxima de registros (padrão: 50).
- `--json`: Saída estruturada em JSON.

**Exemplo:**
```bash
neo fin tx list --month 2026-10 --category alimentacao
```

---

### `neo fin tx update`
Edita os atributos de uma transação pelo seu ID, recalculando automaticamente os saldos da conta envolvida (alias: `neo fin tx edit`).

```bash
neo fin tx update <id> [--amount <valor>] [--desc <descrição>] [-a <conta>] [-c <categoria>] [-d <YYYY-MM-DD>] [--json]
```

**Exemplo:**
```bash
neo fin tx update 12 --amount 52.00 --desc "Almoço e sobremesa"
```

---

### `neo fin tx delete`
Exclui uma movimentação financeira pelo seu ID e restaura o saldo original da conta (alias: `neo fin tx rm`).

```bash
neo fin tx delete <id> [--yes] [--json]
```

**Exemplo:**
```bash
neo fin tx delete 12 --yes
```
