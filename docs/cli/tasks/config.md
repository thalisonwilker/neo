---
name: cli-tasks-config
description: Manual do comando neo tasks config para gestão de token e colunas Kanban do Shortcut.
alwaysApply: false
---

# neo tasks config
> Gerencia credenciais e preferências de mapeamento de colunas do serviço de tarefas Shortcut.

O recurso `neo tasks config` administra o token de autenticação do Shortcut no Keyring seguro do sistema operacional e define o mapeamento das colunas do workflow ágil que compõem o quadro Kanban em `neo tasks resume`.

---

## Sintaxe

```bash
neo tasks config <ação> [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| `set` | Salva o token da API do Shortcut de forma segura no Keyring | `neo tasks config set` |
| `get` | Exibe o status e o token mascarado salvo | `neo tasks config get` |
| `delete` | Remove a credencial armazenada do Shortcut | `neo tasks config delete` |
| `columns` | Configura as colunas correspondentes a *A fazer*, *Fazendo* e *Feito* | `neo tasks config columns` |

---

## Opções

As opções abaixo são específicas de `neo tasks config`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Atalho | Ações suportadas | Padrão | Descrição |
|---|---|---|---|---|
| `--service` | `-s` | Todas | `shortcut` | Provedor de tarefas (`shortcut`). |
| `--token` | `-t` | `set` | Nenhum | Token da API (se omitido, solicita via prompt oculto seguro). |
| `--todo` | — | `columns` | Nenhum | Nome(s) da coluna para *A fazer* separados por vírgula. |
| `--doing` | — | `columns` | Nenhum | Nome(s) da coluna para *Fazendo* separados por vírgula. |
| `--done` | — | `columns` | Nenhum | Nome(s) da coluna para *Feito* separados por vírgula. |

---

## Exemplos

### 1. Configurando o token de acesso (modo interativo seguro)
```bash
neo tasks config set
# Solicita: Token do Shortcut: [entrada oculta]
```

### 2. Configurando o token em ambiente automatizado/CI
```bash
neo tasks config set --token "$SHORTCUT_API_TOKEN"
```

### 3. Consultando o status da credencial
=== "Saída Humana"
    ```bash
    neo tasks config get
    ```
    ```text
    Status: Conectado
    Token:  sh_tok_***...xyz
    ```

=== "Saída em JSON"
    ```bash
    neo --json tasks config get | jq .
    ```

### 4. Configurando colunas do Kanban via linha de comando
```bash
neo tasks config columns \
  --todo "Backlog de Sprint, Bug" \
  --doing "Em Progresso" \
  --done "Finalizado"
```

---

## Erros comuns e códigos de saída

* **Código 1 (Erro genérico):** Falha ao acessar o Keyring nativo ou token inválido rejeitado pela API do Shortcut.
* **Código 2 (Uso incorreto):** No modo `--json`, invocar `neo tasks config columns` sem fornecer `--todo`, `--doing` e `--done`.

---

## Veja também
- [neo tasks resume](resume.md) — Exibir quadro Kanban com as colunas configuradas
- [neo tasks whoami](whoami.md) — Validar a identidade do usuário autenticado
- [neo git auth](../git/auth.md) — Autenticação dos provedores Git

