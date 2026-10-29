---
name: cli-tasks-whoami
description: Manual do comando neo tasks whoami para validação de credencial e membro autenticado no Shortcut.
alwaysApply: false
---

# neo tasks whoami
> Verifica e exibe o membro autenticado na API do Shortcut.

O comando `neo tasks whoami` confirma a validade do token de acesso configurado, realizando uma requisição de leitura ao endpoint do membro no Shortcut e exibindo o nome completo, nome de usuário e e-mail vinculados à conta.

---

## Sintaxe

```bash
neo tasks whoami [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Exibe o perfil do membro autenticado no serviço de tarefas | `neo tasks whoami` |

---

## Opções

As opções abaixo são específicas de `neo tasks whoami`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Atalho | Obrigatório | Padrão | Descrição |
|---|---|---|---|---|
| `--service` | `-s` | Não | `shortcut` | Serviço de tarefas (`shortcut`). |

---

## Exemplos

### 1. Verificando o membro autenticado no terminal
```bash
neo tasks whoami
```

Exemplo de visualização:
```text
╭─ Membro Autenticado (Shortcut) ────────╮
│ Nome:       Thalyson                   │
│ Username:   thalyson                   │
│ ID:         654a3b2c-1234-5678-90ab    │
╰────────────────────────────────────────╯
```

### 2. Validação automatizada com `--json` e `jq`
```bash
neo --json tasks whoami | jq -r '{name: .profile.name, mention_name: .profile.mention_name}'
```

---

## Erros comuns e códigos de saída

* **Código 1 (Erro genérico):** Token de acesso ausente ou inválido no Shortcut. Execute `neo tasks config set` para recadastrar a credencial.

---

## Veja também
- [neo tasks config](config.md) — Configurar ou atualizar o token do Shortcut
- [neo tasks resume](resume.md) — Visualizar quadro Kanban das suas tarefas
- [neo git auth](../git/auth.md) — Autenticação dos provedores Git
