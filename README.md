# Neo — Personal Command Assistant

> **Compreenda seus sistemas. Seja dono das suas escolhas.**

<p align="center">
  <img src="https://raw.githubusercontent.com/thalisonwilker/neo/main/docs/assets/neo-logo.jpg" alt="Neo CLI Logo" width="240" style="border-radius: 20px;" />
</p>

<p align="center">
  <em>Assistente pessoal de linha de comando, alta produtividade, modular, seguro e pronto para automação</em>
</p>

<p align="center">
  <a href="https://github.com/thalisonwilker/neo/actions/workflows/ci.yml?query=branch%3Amain"><img src="https://github.com/thalisonwilker/neo/actions/workflows/ci.yml/badge.svg?event=push&branch=main" alt="CI & Deploy" /></a>
  <a href="https://thalisonwilker.github.io/neo/"><img src="https://img.shields.io/endpoint?url=https://thalisonwilker.github.io/neo/coverage-badge.json" alt="Coverage" /></a>
  <a href="https://pypi.org/project/neo-cmd/"><img src="https://img.shields.io/badge/pypi%20package-v0.1.0-34D058" alt="PyPI Package" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.13+-34D058" alt="Python 3.13+" /></a>
  <a href="https://github.com/thalisonwilker/neo/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-34D058" alt="License: MIT" /></a>
</p>

**Neo** (`neo-cmd`) é um assistente pessoal extensível de linha de comando desenvolvido em **Python 3.13** com **Typer** e **Rich**. Ele centraliza operações de repositórios Git (**GitHub** e **Bitbucket Cloud**) e gestão de demandas (**Shortcut**), oferecendo quadros Kanban no terminal, análise de contexto, segurança nativa via Keyring do SO e suporte a `--json`.

📚 **Documentação Completa:** **[thalisonwilker.github.io/neo](https://thalisonwilker.github.io/neo/)**

---

## 🚀 Instalação

### Via PyPI (`uv` ou `pip`)

```bash
# Recomendado: instalar globalmente como ferramenta isolada com uv
uv tool install neo-cmd

# Ou via pip
pip install neo-cmd
```

### Desenvolvimento Local

```bash
git clone https://github.com/thalisonwilker/neo.git
cd neo
uv sync
uv run neo --help
```

---

## ⚡ Uso Rápido

```bash
# 1. Configurar credenciais com segurança no Keyring do SO
neo git config auth set github
neo tasks config set

# 2. Quadro Kanban no terminal (A fazer | Fazendo | Feito) da iteração atual
neo tasks resume

# 3. Consultar e analisar stories / chamados
neo tasks list --mine
neo tasks analyze 2108

# 4. Gerenciar workspaces, repositórios e histórico Git (GitHub / Bitbucket)
neo git workspace select
neo git repo list
neo git commits search --query "fix" --limit 5

# 5. Status geral de todas as integrações
neo config show
```

> Todos os comandos aceitam a flag global `--json` (ex.: `neo --json tasks resume`) para integração com `jq` e pipelines de automação.

---

## 🛠️ Qualidade & Testes

```bash
uv run pytest --cov=neo     # Testes unitários e E2E (cobertura >= 80%)
uv run ruff check .         # Linter e formatação
uv run mypy src             # Checagem estática de tipos (strict)
```

---

## 📄 Licença

Distribuído sob a licença livre **MIT**. Consulte o arquivo [LICENSE](https://github.com/thalisonwilker/neo/blob/main/LICENSE) para mais detalhes.
