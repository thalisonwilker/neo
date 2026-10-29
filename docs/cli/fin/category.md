---
name: cli-fin-category
description: Gerenciamento de categorias de despesas e receitas com neo fin category.
alwaysApply: false
---

# neo fin category
> Gestão de categorias de despesas e receitas.

O comando `neo fin category` organiza suas movimentações financeiras em grupos para permitir a análise detalhada no resumo mensal. No primeiro uso do comando `neo fin`, o Neo inicializa automaticamente categorias padrão como `Alimentação`, `Moradia`, `Transporte`, `Lazer`, `Saúde`, `Salário`, `Freelance` e `Outros`.

---

## Comandos Disponíveis

### `neo fin category add`
Cadastra uma nova categoria personalizada.

```bash
neo fin category add <slug> --name <nome> --type <expense|income> [--json]
```

**Parâmetros e Opções:**
- `<slug>`: Slug identificador único (ex: `cursos`, `jogos`, `dividendos`).
- `--name`, `-n`: Nome exibido da categoria.
- `--type`, `-t`: Tipo da categoria: `expense` (despesa) ou `income` (receita).
- `--json`: Saída estruturada em JSON.

**Exemplo:**
```bash
neo fin category add jogos --name "Jogos & Steam" --type expense
```

---

### `neo fin category list`
Lista todas as categorias cadastradas ou filtra por tipo.

```bash
neo fin category list [--type <expense|income>] [--json]
```

**Exemplo:**
```bash
neo fin category list --type expense
```

---

### `neo fin category rm`
Remove uma categoria cadastrada.

```bash
neo fin category rm <slug> [--type <expense|income>] [--json]
```

> [!NOTE]
> Categorias que já estejam sendo utilizadas em transações financeiras não podem ser removidas sem antes reclassificar ou excluir as transações correspondentes.

**Exemplo:**
```bash
neo fin category rm jogos --type expense
```
