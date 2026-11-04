---
name: cli-config-index
description: Visão geral dos comandos de configuração geral e de agente do Neo.
alwaysApply: false
---

# neo config

`neo config` reúne a visão geral das configurações e as preferências do agente de codificação.

- **`neo config show`** — apresenta um resumo do contexto Git, tasks, agente e serviços configurados. Consulte os detalhes em [configuração](../../configuration.md).
- **`neo config agent`** — gerencia as preferências do agente com `set`, `get`, `list` e `unset`. Consulte [configuração do agente](../agent/config.md).

```bash
neo config show
neo config agent list
neo config agent set command agy
```

Para as preferências Git, use [`neo git config`](../git/config.md); para o Shortcut, use [`neo tasks config`](../tasks/config.md).
