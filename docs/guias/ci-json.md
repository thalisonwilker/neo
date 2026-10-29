---
name: guias-ci-json
description: Guia de automação e integração em CI/CD usando neo --json e jq com códigos de saída semânticos.
alwaysApply: false
---

# Uso em CI com `--json` e `jq`

Todo comando de leitura do Neo aceita a flag global `--json`, emitindo payloads estruturados no `stdout` sem bordas decorativas ou códigos de cor ANSI, ideal para automações, scripts shell e esteiras de CI/CD.

---

## 1. Configurando Credenciais em CI

Em ambientes não interativos (como GitHub Actions, GitLab CI ou contêineres Docker), o Keyring do SO não está disponível. Utilize as **variáveis de ambiente oficiais**, que possuem precedência automática:

=== "GitHub Actions"
    ```yaml
    - name: Executar Neo no CI
      env:
        NEO_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: |
        neo git status --json
    ```

=== "Bitbucket Pipelines"
    ```yaml
    - step:
        name: Diagnosticar Repositórios
        script:
          - export NEO_BITBUCKET_EMAIL="dev@empresa.com"
          - export NEO_BITBUCKET_TOKEN="$BITBUCKET_API_TOKEN"
          - neo git repo list --json
    ```

=== "Shortcut (Módulo Tasks)"
    ```bash
    export SHORTCUT_API_TOKEN="sh_tok_sua_chave"
    neo --json tasks iterations
    ```

---

## 2. Códigos de Saída Semânticos em Scripts

O Neo retorna códigos de saída de `0` a `5`. Você pode utilizá-los para controlar fluxos de execução:

```bash
#!/usr/bin/env bash
set -e

# Verifica se a autenticação está válida (código 3 se falhar)
if ! neo git auth status --provider github --json > /dev/null 2>&1; then
  echo "Erro: GitHub não autenticado no ambiente de CI!"
  exit 1
fi
```

---

## 3. Receitas com `jq`

### Extraindo apenas nomes e URLs SSH de repositórios
```bash
neo git repo list --json | jq '.[] | {name, ssh: .clone_links[0].href}'
```

### Contando histórias por coluna no Shortcut
```bash
neo --json tasks resume | jq '{
  total_todo: (.todo | length),
  total_doing: (.doing | length),
  total_done: (.done | length)
}'
```

### Extraindo o hash curto dos últimos 5 commits
```bash
neo git commits list --limit 5 --json | jq -r '.[].hash[0:7]'
```

---

## Veja também
- [Conceitos Gerais — Tabela de Códigos de Saída](../cli/index.md#tabela-de-codigos-de-saida)
- [neo git repo](../cli/git/repo.md)
- [neo tasks resume](../cli/tasks/resume.md)
