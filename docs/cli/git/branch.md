---
name: cli-git-branch
description: Operações em branches locais do repositório Git selecionado.
alwaysApply: false
---

# neo git branch

Os comandos operam nas branches locais do repositório selecionado. Selecionar faz checkout e altera a branch ativa também para outras ferramentas.

```bash
neo git branch list
neo git branch list --json
neo git branch create feature/minha-task
neo git branch select feature/minha-task
neo git branch delete feature/minha-task
neo git branch delete feature/minha-task --yes
```

A exclusão exige confirmação, não usa exclusão forçada e não remove a branch ativa. Para definir a branch ativa pela configuração, use `neo git config set branch <nome>`. Operações de branch na nuvem não fazem parte desta feature.
