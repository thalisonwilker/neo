---
name: cli-api-index
description: Gerenciamento da Lista de permissão da API Neo pelo grupo neo api.
alwaysApply: false
---

# neo api
> Gerenciamento da Lista de permissão da API REST do Neo.

O grupo `neo api` controla quais endereços de e-mail podem criar um **Usuário** no primeiro acesso à API do Neo. A conexão usa a variável `NEO_DATABASE_URL`.

---

## Comandos disponíveis

### `neo api permitir <email>`
Normaliza o e-mail em minúsculas e adiciona-o à Lista de permissão. É idempotente: se o e-mail já estiver na lista, informa e encerra com código `0` sem duplicar. E-mail com formato inválido encerra com código `2` sem gravar.

```bash
neo api permitir dev@empresa.com
neo api permitir dev@empresa.com --json
```

### `neo api permissoes`
Lista todos os e-mails atualmente autorizados na Lista de permissão.

```bash
neo api permissoes
neo api permissoes --json
```

### `neo api remover-permissao <email>`
Remove um e-mail da Lista de permissão. Se o e-mail não estiver na lista, encerra com código `4` (não encontrado). **Usuários já registrados permanecem intactos** e continuam acessando a API.

```bash
neo api remover-permissao dev@empresa.com
neo api remover-permissao dev@empresa.com --json
```

---

## Veja também
- [Conceitos Gerais da CLI](../index.md)
- [Árvore de comandos](../comandos.md)
- [Glossário de Termos](../../glossary.md)
