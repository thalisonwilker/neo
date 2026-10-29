---
name: cli-fin-bank
description: Gerenciamento de contas bancárias e carteiras com neo fin bank.
alwaysApply: false
---

# neo fin bank
> Cadastro, listagem, edição e exclusão de contas bancárias e carteiras financeiras.

O comando `neo fin bank` gerencia os locais onde seu dinheiro está guardado (bancos tradicionais, fintechs, corretoras, dinheiro em espécie ou cartões). Cada conta possui um saldo inicial e um saldo atual calculado automaticamente com base nas receitas e despesas registradas.

---

## Comandos Disponíveis

### `neo fin bank add`
Cadastra uma nova conta bancária ou carteira.

```bash
neo fin bank add <slug> --name <nome> [--type <tipo>] [--balance <saldo_inicial>] [--json]
```

**Parâmetros e Opções:**
- `<slug>`: Identificador único em minúsculas (ex: `nubank`, `inter`, `carteira`).
- `--name`, `-n`: Nome legível da conta (ex: `"Nubank Conta Principal"`).
- `--type`, `-t`: Tipo de conta: `checking` (corrente), `savings` (poupança), `investment` (investimentos), `credit` (cartão de crédito), `cash` (dinheiro físico), `other`. Padrão: `checking`.
- `--balance`, `-b`: Saldo inicial da conta. Padrão: `0.0`.
- `--json`: Emite o registro criado em JSON.

**Exemplo:**
```bash
neo fin bank add nubank --name "Nubank Roxinho" --type checking --balance 1500.00
```

---

### `neo fin bank list`
Lista todas as contas bancárias cadastradas com seus respectivos saldos iniciais e saldos atuais calculados.

```bash
neo fin bank list [--json]
```

**Exemplo:**
```bash
neo fin bank list
```

---

### `neo fin bank edit`
Atualiza o nome de exibição ou o tipo de uma conta existente.

```bash
neo fin bank edit <slug> [--name <novo_nome>] [--type <novo_tipo>] [--json]
```

**Exemplo:**
```bash
neo fin bank edit nubank --name "Nubank PJ" --type checking
```

---

### `neo fin bank rm`
Remove uma conta bancária cadastrada.

```bash
neo fin bank rm <slug> [--json]
```

> [!NOTE]
> Por segurança e integridade referencial, uma conta que possua transações vinculadas **não pode ser excluída**. Remova as transações primeiro caso queira remover a conta.

**Exemplo:**
```bash
neo fin bank rm inter
```
