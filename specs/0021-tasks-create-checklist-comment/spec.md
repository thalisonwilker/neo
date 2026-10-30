---
name: spec
description: Contrato da feature 0021 — criação de stories (tarefas), checklist items e comentários no módulo `neo tasks` (Shortcut API v3).
alwaysApply: true
---

# Spec — Criação de Tarefas, Checklist e Comentários (`neo tasks create`, `neo tasks check`, `neo tasks comment`)

> **Fonte da verdade.** Status: implementado
> Tier: **Pequeno** (`spec.md` + `tasks.md` — extensão do bounded context de Tasks / Shortcut Integration).

## Resumo
Permite que o usuário crie novas tarefas (stories) associadas automaticamente à iteração atual ativa e ao usuário logado, adicione e gerencie itens de checklist (marcar/desmarcar concluído) e adicione comentários diretamente pela CLI `neo tasks`.

---

## Critérios de Aceite

### AC-1: Criação de Tarefa (`neo tasks create`)
- **Dado** um usuário com credenciais válidas do Shortcut;
- **Quando** executa `neo tasks create <título> [-d/--description <desc>] [--type feature|bug|chore] [--owner me|<id>|none] [--iteration current|<id>|<nome>|none]`;
- **Então** o sistema:
  1. Cria uma story via `POST /api/v3/stories`;
  2. Associa por padrão à **última iteração ativa** (se houver e não for especificado `--iteration none`);
  3. Associa por padrão ao **membro atual** autenticado (`me`, via `get_current_member()`, a não ser que `--owner none` seja informado);
  4. Exibe os dados da story criada em painel Rich contendo ID, Título, Tipo, Iteração, Owner e URL Web;
  5. Quando executado com `--json`, retorna o objeto estruturado JSON da story criada com código de saída `0`.

### AC-2: Adição de Checklist Item (`neo tasks check add`)
- **Dado** uma story existente com ID `<task-id>`;
- **Quando** o usuário executa `neo tasks check add <task-id> <descrição>`;
- **Então** o sistema:
  1. Envia uma requisição `POST /api/v3/stories/<task-id>/tasks` com `{"description": "<descrição>", "complete": false}`;
  2. Exibe uma mensagem Rich de confirmação com ID do item criado, estado (`[ ] Aberto`) e texto;
  3. Com `--json`, retorna o payload do checklist item com `{"id": ..., "description": "...", "complete": false}`;
  4. Caso a story não exista, encerra com erro amigável e código de saída `1`.

### AC-3: Conclusão e Reabertura de Checklist Item (`neo tasks check complete` / `uncomplete`)
- **Dado** um item de checklist existente com ID `<check-id>` na story `<task-id>`;
- **Quando** o usuário executa `neo tasks check complete <task-id> <check-id>` (ou o alias `neo tasks check done <task-id> <check-id>`);
- **Então** o sistema envia `PUT /api/v3/stories/<task-id>/tasks/<check-id>` com `{"complete": true}` e exibe confirmação com status `[✓] Concluído`;
- **E Quando** o usuário executa `neo tasks check uncomplete <task-id> <check-id>` (ou o alias `neo tasks check undone <task-id> <check-id>`);
- **Então** o sistema envia `PUT /api/v3/stories/<task-id>/tasks/<check-id>` com `{"complete": false}` e exibe confirmação com status `[ ] Aberto`;
- **E** em modo `--json`, ambos retornam o objeto atualizado do checklist item com código `0`.

### AC-4: Adição de Comentário (`neo tasks comment add`)
- **Dado** uma story existente com ID `<task-id>`;
- **Quando** o usuário executa `neo tasks comment add <task-id> <comentário>` (ou `neo tasks comment <task-id> <comentário>`);
- **Então** o sistema envia `POST /api/v3/stories/<task-id>/comments` com `{"text": "<comentário>"}`;
- **E** exibe uma mensagem Rich de sucesso contendo o ID do comentário e prévia do texto;
- **E** em modo `--json`, retorna o objeto do comentário com código `0`.

### AC-5: Exibição no detalhe da Story (`neo tasks show`)
- **Dado** uma story com checklist items e/ou comentários;
- **Quando** o usuário executa `neo tasks show <task-id>`;
- **Então** o detalhe da story exibe as seções `Checklist (<completos>/<total>)` e `Comentários (<total>)` com seus respectivos itens e estados.
