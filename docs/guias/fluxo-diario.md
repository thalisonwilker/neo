---
name: guias-fluxo-diario
description: Guia de fluxo diário de desenvolvimento conectando Shortcut, Git e commits padronizados com o Neo.
alwaysApply: false
---

# Fluxo Diário: Tasks → Branch → Commit

Este guia apresenta o fluxo de trabalho ideal para iniciar e desenvolver demandas com o Neo, saindo do quadro de tarefas para o código em poucos comandos.

---

## 1. Comece o Dia pelo Quadro Kanban

Abra o terminal e verifique suas tarefas atribuídas na sprint atual com:

```bash
neo tasks resume
```

Você verá suas histórias organizadas nas colunas **A fazer**, **Fazendo** e **Feito**.

---

## 2. Escolha e Analise a História

Identifique o ID da story que você vai iniciar (por exemplo, `#2157`) e obtenha o contexto com:

```bash
neo tasks analyze 2157
```

O comando analisa o card e entrega:
- Critérios de aceite mapeados.
- Sugestão de branch (ex.: `feature/sc-2157-adicionar-fcp-st`).
- Sugestão da mensagem de commit inicial.

---

## 3. Crie a Branch e Comece a Codar

Você pode utilizar a sugestão fornecida manualmente ou capturá-la diretamente via terminal:

```bash
# Cria e entra na branch sugerida
git checkout -b $(neo --json tasks analyze 2157 | jq -r '.suggested_branch')
```

Valide se o contexto Git foi reconhecido pelo Neo:

```bash
neo git status
```

---

## 4. Implemente e Realize Commits Padronizados

Após implementar o código e rodar seus testes locais:

```bash
git add .
git commit -m "feat(fiscal): adiciona calculo de FCP ST no CSOSN 900"
```

Inspecione seus commits recentes para conferir o histórico antes de enviar:

```bash
neo git commits list --limit 3
```

---

## Veja também
- [neo tasks resume](../cli/tasks/resume.md) — Quadro Kanban no terminal
- [neo tasks analyze](../cli/tasks/analyze.md) — Análise contextual de histórias
- [neo git commits](../cli/git/commits.md) — Histórico e consulta de commits

