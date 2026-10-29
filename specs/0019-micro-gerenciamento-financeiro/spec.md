---
name: spec
description: Contrato e critérios de aceite para o módulo de micro gerenciamento financeiro pessoal (neo fin).
alwaysApply: true
---

# Spec — 0019 Micro Gerenciamento Financeiro (`neo fin`)

> **Fonte da verdade.** Status: aprovado
> Contrato de entrega para o gerenciador financeiro pessoal via terminal com SQLite local, cobrindo contas/bancos, categorias, despesas, receitas e resumos consolidados.

## Resumo
Permite que o usuário gerencie finanças pessoais diretamente pelo terminal através do comando `neo fin`: cadastrar e gerenciar bancos/contas, categorias de gastos e ganhos, registrar despesas e receitas rapidamente e acompanhar o balanço consolidado e extrato mensal.

---

## Critérios de Aceite

### AC-1: Inicialização do Banco SQLite e Carga Padrão
- **Dado** o primeiro uso do comando `neo fin`,
- **Quando** qualquer comando financeiro for invocado,
- **Então** o Neo deve criar automaticamente o banco SQLite local em `~/.config/neo/finance.db` com permissão restrita `0600`, aplicar as tabelas necessárias e semear categorias padrão (`Alimentação`, `Moradia`, `Transporte`, `Lazer`, `Saúde`, `Salário`, `Freelance`, `Outros`).

### AC-2: Gerenciamento de Bancos e Contas (`neo fin bank`)
- **Dado** o subcomando `neo fin bank`,
- **Quando** `neo fin bank add <slug> --name <nome> [--type <tipo>] [--balance <saldo_inicial>]` for executado,
- **Então** a conta deve ser persistida com sucesso e saldo inicial informado (default: 0.00).
- **E Quando** `neo fin bank list` for executado,
- **Então** exibe a lista de contas, tipos, saldo inicial e saldo atual consolidado.
- **E Quando** `neo fin bank edit <slug> [--name <novo_nome>] [--type <novo_tipo>]` for executado,
- **Então** os metadados da conta são atualizados.
- **E Quando** `neo fin bank rm <slug>` for executado,
- **Então** a conta deve ser removida caso não possua transações vinculadas (ou alertar com erro de integridade referencial).

### AC-3: Gerenciamento de Categorias (`neo fin category`)
- **Dado** o subcomando `neo fin category`,
- **Quando** `neo fin category add <slug> --name <nome> --type <expense|income>` for executado,
- **Então** a categoria deve ser persistida.
- **E Quando** `neo fin category list [--type <expense|income>]` for executado,
- **Então** lista as categorias cadastradas e seus tipos.
- **E Quando** `neo fin category rm <slug> --type <tipo>` for executado,
- **Então** remove a categoria se não estiver em uso em transações.

### AC-4: Registro de Despesas e Receitas (`neo fin tx`, `expense`, `income`)
- **Dado** contas e categorias cadastradas,
- **Quando** o usuário executar o atalho rápido `neo fin expense <valor> <descrição> [-a <conta>] [-c <categoria>] [-d <YYYY-MM-DD>]`,
- **Então** uma transação do tipo `expense` é registrada debitando o valor da conta indicada (ou da conta padrão se omitida).
- **E Quando** o usuário executar `neo fin income <valor> <descrição> [-a <conta>] [-c <categoria>] [-d <YYYY-MM-DD>]`,
- **Então** uma transação do tipo `income` é registrada creditando o valor na conta indicada.
- **E Quando** o comando genérico `neo fin tx add <valor> <descrição> --type <expense|income>` for executado,
- **Então** a transação é criada com os mesmos campos.

### AC-5: Listagem e Filtros de Transações (`neo fin tx list`)
- **Dado** transações registradas no banco de dados,
- **Quando** `neo fin tx list` for executado,
- **Então** exibe as transações em formato tabular estilizado com valores coloridos (despesas em vermelho, receitas em verde), conta e categoria.
- **E Quando** filtros forem informados (`--month YYYY-MM`, `--account <slug>`, `--category <slug>`, `--type <tipo>`),
- **Então** apenas as transações correspondentes aos filtros devem ser exibidas.

### AC-6: Edição e Remoção de Transações (`neo fin tx edit`, `neo fin tx rm`)
- **Dado** uma transação existente com `ID`,
- **Quando** `neo fin tx edit <id> [--amount <valor>] [--desc <descrição>] [--account <conta>] [--category <categoria>]` for executado,
- **Então** os dados são atualizados recalculando o saldo correspondente.
- **E Quando** `neo fin tx rm <id> [--yes]` for executado,
- **Então** a transação é excluída e o saldo da conta é recalculado.

### AC-7: Resumo Mensal e Balanço Consolidado (`neo fin summary`, `neo fin balance`)
- **Dado** registros de transações no período,
- **Quando** `neo fin balance` for executado,
- **Então** apresenta tabela com cada conta bancária, saldo inicial, total de receitas, total de despesas e saldo atual, além do total de patrimônio consolidado.
- **E Quando** `neo fin summary [--month YYYY-MM]` for executado,
- **Então** apresenta um painel consolidado do mês com: Total de Entradas, Total de Saídas, Saldo Líquido do mês, e tabela de distribuição de despesas por categoria.

### AC-8: Suporte a JSON e Tratamento de Erros
- **Dado** qualquer subcomando de `neo fin`,
- **Quando** a opção `--json` for informada,
- **Então** emite a saída estruturada no `stdout` em formato JSON puro.
- **E Quando** uma conta ou categoria inexistente for referenciada,
- **Então** encerra com código de saída `4` (`ExitCode.NOT_FOUND`) e mensagem clara.

---

## Casos de Borda e Erros
- Valor monetário negativo ou zero informado: rejeita com código `2` (`ExitCode.USAGE_ERROR`).
- Formato de data inválido: rejeita exigindo formato `YYYY-MM-DD`.
- Remoção de conta que possui histórico de transações: rejeita com código `1` (`ExitCode.ERROR`) orientando a remover as transações antes ou arquivar.

## Fora de Escopo
- Conciliação bancária automática com arquivos OFX/PDF.
- Integração com provedores bancários externos ou Open Finance.

## Rastreabilidade
- Tasks: `./tasks.md`
- Product: `./product.md`
- Design: `./design.md`
- Domínio: `./domain.md`
