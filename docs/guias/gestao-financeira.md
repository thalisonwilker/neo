---
name: guias-gestao-financeira
description: Guia prático de micro gerenciamento financeiro pessoal local com o módulo neo fin.
alwaysApply: false
---

# Guia Prático: Gestão Financeira Pessoal com `neo fin`

> Como controlar gastos e receitas em segundos pelo terminal com banco SQLite local, total privacidade e visão consolidada mensal.

O desenvolvedor moderno passa a maior parte do tempo no terminal ou no editor. Abrir planilhas complexas ou aplicativos de banco no celular toda vez que compra um café ou paga uma conta gera atrito cognitivo e quebra de fluxo.

Com o **`neo fin`**, você registra movimentações diárias em menos de 2 segundos, mantém seus dados em um banco de dados relacional local seguro (`~/.config/neo/finance.db`) com permissão restrita `0600` e acompanha seu balanço consolidado mensal com tabelas estilizadas via **Rich**.

---

## 1. Passo 1: Configure suas Contas / Bancos

O banco SQLite é inicializado automaticamente no primeiro comando. O primeiro passo é registrar as contas onde seu dinheiro fica armazenado (contas correntes, carteiras de dinheiro, investimentos ou cartões):

```bash
# Cadastrar conta com saldo inicial
neo fin bank create nubank --name "Nubank Principal" --type checking --balance 1500.00
neo fin bank create inter --name "Banco Inter" --type checking --balance 400.00
neo fin bank create carteira --name "Dinheiro Físico" --type cash --balance 80.00
```

Para inspecionar as contas e saldos atuais a qualquer momento:

```bash
# Listar todas as contas
neo fin bank list

# Consultar detalhes de uma conta específica
neo fin bank get nubank
```

---

## 2. Passo 2: Categorias de Despesas e Receitas

No primeiro uso, o Neo já semeia automaticamente as categorias mais comuns do dia a dia:
- **Despesas:** `alimentacao`, `moradia`, `transporte`, `lazer`, `saude`, `educacao`, `outros`.
- **Receitas:** `salario`, `freelance`, `investimentos`, `outros`.

Para visualizar todas as categorias disponíveis:

```bash
neo fin category list --type expense
neo fin category list --type income
```

Se desejar criar categorias personalizadas:

```bash
neo fin category create cursos --name "Cursos & Livros" --type expense
neo fin category create dividendos --name "Dividendos de Ações" --type income
```

---

## 3. Passo 3: O Fluxo Diário (Atalhos de 2 Segundos)

Para evitar fricção, você não precisa informar IDs nem comandos longos para registrar o que gastou ou recebeu. Utilize os atalhos rápidos:

### Registrando uma Despesa (`expense`)
```bash
# Registra na conta padrão com categoria 'outros'
neo fin expense 12.00 "Café e água"

# Informando conta (-a) e categoria (-c)
neo fin expense 48.90 "Almoço executivo" -a nubank -c alimentacao
neo fin expense 29.90 "Uber para reunião" -a nubank -c transporte
neo fin expense 119.90 "Internet fibra" -a inter -c moradia -d 2026-10-10
```

### Registrando uma Receita (`income`)
```bash
# Salário creditado na conta
neo fin income 5000.00 "Salário mensal" -a nubank -c salario

# Projeto freelance ou consultoria
neo fin income 1200.00 "Landing page cliente" -a inter -c freelance
```

---

## 4. Passo 4: Extrato e Auditoria de Transações (`tx`)

Para checar o histórico de movimentações, use `neo fin tx list`. O terminal exibirá uma tabela colorida com despesas em vermelho e receitas em verde:

```bash
# Ver as últimas transações registradas
neo fin tx list

# Filtrar pelo mês atual (ou específico)
neo fin tx list --month 2026-10

# Filtrar por conta ou categoria específica
neo fin tx list --account nubank --category alimentacao
```

### Corrigindo Erros
Se digitou um valor errado ou deseja excluir uma transação:

```bash
# Obter detalhes da transação
neo fin tx get 14

# Atualizar valor ou descrição (o saldo da conta é recalculado na hora)
neo fin tx update 14 --amount 52.00 --desc "Almoço com sobremesa"

# Excluir transação (o valor é estornado do saldo da conta)
neo fin tx delete 14 --yes
```

---

## 5. Passo 5: Fechamento do Mês e Balanço Patrimonial

O Neo sintetiza a saúde do seu bolso em duas visões complementares:

### Balanço Patrimonial Consolidado (`balance`)
Apresenta o saldo inicial, o total histórico de receitas, o total histórico de despesas e o saldo atual disponível em cada banco, além do patrimônio líquido consolidado:

```bash
neo fin balance
```

### Resumo Mensal com Distribuição por Categoria (`summary`)
Gera um painel com o resultado do mês (Receitas, Despesas, Resultado Líquido) e a tabela percentual de para onde foi seu dinheiro:

```bash
# Resumo do mês corrente
neo fin summary

# Resumo de um mês específico
neo fin summary --month 2026-10
```

---

## 6. Passo 6: Automações com `--json` e Shell Scripts

Como todo o ecossistema Neo, todos os comandos do `neo fin` aceitam a opção `--json`, permitindo criar relatórios customizados com `jq` ou scripts em shell:

```bash
# Extrair o patrimônio total líquido
neo fin balance --json | jq '.total_current'

# Listar as maiores despesas do mês por categoria
neo fin summary --month 2026-10 --json | jq '.expenses_by_category[] | {categoria: .category_name, total: .total, participacao: .percentage}'
```

---

## Resumo dos Comandos Principais

| Ação | Comando |
|---|---|
| Criar conta | `neo fin bank create <slug> --name <nome> [--balance <saldo>]` |
| Ver saldo das contas | `neo fin bank list` ou `neo fin balance` |
| Registrar gasto rápido | `neo fin expense <valor> <descrição> [-a <conta>] [-c <categoria>]` |
| Registrar ganho rápido | `neo fin income <valor> <descrição> [-a <conta>] [-c <categoria>]` |
| Ver extrato do mês | `neo fin tx list --month YYYY-MM` |
| Resumo mensal consolidado | `neo fin summary [--month YYYY-MM]` |
