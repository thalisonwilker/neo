---
name: cli-fin-bank
description: Gerenciamento de contas bancárias e carteiras com neo fin bank.
alwaysApply: false
---

# neo fin bank
> Cadastro, consulta, listagem, atualização e exclusão de contas bancárias e carteiras financeiras.

O comando `neo fin bank` gerencia os locais onde seu dinheiro está guardado (bancos tradicionais, fintechs, corretoras, dinheiro em espécie ou cartões). Cada conta possui um saldo inicial e um saldo atual calculado automaticamente com base nas receitas e despesas registradas.

---

## Comandos Disponíveis

### `neo fin bank create`
Cadastra uma nova conta bancária ou carteira (alias: `neo fin bank add`).

```bash
neo fin bank create <slug> --name <nome> [--type <tipo>] [--balance <saldo_inicial>] [--json]
```

**Parâmetros e Opções:**
- `<slug>`: Identificador único em minúsculas (ex: `nubank`, `inter`, `carteira`).
- `--name`, `-n`: Nome legível da conta (ex: `"Nubank Conta Principal"`).
- `--type`, `-t`: Tipo de conta: `checking` (corrente), `savings` (poupança), `investment` (investimentos), `credit` (cartão de crédito), `cash` (dinheiro físico), `other`. Padrão: `checking`.
- `--balance`, `-b`: Saldo inicial da conta. Padrão: `0.0`.
- `--json`: Emite o registro criado em JSON.

**Exemplo:**
```bash
neo fin bank create nubank --name "Nubank Roxinho" --type checking --balance 1500.00
```

---

### `neo fin bank get`
Exibe os detalhes completos de uma conta bancária específica (alias: `neo fin bank show`).

```bash
neo fin bank get <slug> [--json]
```

**Exemplo:**
```bash
neo fin bank get nubank
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

### `neo fin bank update`
Atualiza o nome de exibição ou o tipo de uma conta existente (alias: `neo fin bank edit`).

```bash
neo fin bank update <slug> [--name <novo_nome>] [--type <novo_tipo>] [--json]
```

**Exemplo:**
```bash
neo fin bank update nubank --name "Nubank PJ" --type checking
```

---

### `neo fin bank delete`
Remove uma conta bancária cadastrada (alias: `neo fin bank rm`).

```bash
neo fin bank delete <slug> [--json]
```

> [!NOTE]
> Por segurança e integridade referencial, uma conta que possua transações vinculadas **não pode ser excluída**. Remova as transações primeiro caso queira remover a conta.

**Exemplo:**
```bash
neo fin bank delete inter
```
