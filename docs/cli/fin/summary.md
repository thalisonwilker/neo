---
name: cli-fin-summary
description: Balanço consolidado de patrimônio e resumo mensal de gastos com neo fin balance e neo fin summary.
alwaysApply: false
---

# Balanço e Resumo Mensal
> Visão patrimonial consolidada e análise detalhada de despesas por categoria.

O módulo financeiro do Neo consolida o estado de todas as suas contas através do comando `neo fin balance` e sintetiza os resultados de cada mês através de `neo fin summary`.

---

## Comandos Disponíveis

### `neo fin balance`
Apresenta o balanço consolidado de todas as contas cadastradas, exibindo o saldo inicial, o total histórico de receitas, o total histórico de despesas e o saldo atual disponível em cada uma, além do total de patrimônio líquido somado.

```bash
neo fin balance [--json]
```

**Exemplo:**
```bash
neo fin balance
```

**Exemplo de Saída JSON:**
```bash
neo fin balance --json
```

---

### `neo fin summary`
Gera um painel com o resumo financeiro consolidado de um mês específico (por padrão, o mês atual). Apresenta:
- Total de Entradas (Receitas)
- Total de Saídas (Despesas)
- Saldo Líquido do mês
- Tabela de distribuição de despesas por categoria com valor total e percentual de participação

```bash
neo fin summary [--month YYYY-MM] [--json]
```

**Opções:**
- `--month`, `-m`: Mês de apuração no formato `YYYY-MM` (ex: `2026-10`). Se omitido, utiliza o mês corrente.
- `--json`: Emite os dados consolidados em formato JSON.

**Exemplo:**
```bash
neo fin summary --month 2026-10
```
