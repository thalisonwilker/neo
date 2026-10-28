# Neo — Trabalho, estudos, lazer e finanças. Sua vida organizada, a um comando de distância.

> **Compreenda seus sistemas. Seja dono das suas escolhas.**

<p align="center">
  <img src="https://raw.githubusercontent.com/thalisonwilker/neo/main/docs/assets/neo-logo.jpg" alt="Neo CLI Logo" width="240" style="border-radius: 20px;" />
</p>

<p align="center">
  <em>Um assistente pessoal para quem prefere o terminal à interface gráfica. Comece hoje pelo fluxo de desenvolvimento e escale suas automações em uma linha.</em>
</p>

<p align="center">
  <a href="https://github.com/thalisonwilker/neo/actions/workflows/ci.yml?query=branch%3Amain"><img src="https://github.com/thalisonwilker/neo/actions/workflows/ci.yml/badge.svg?event=push&branch=main" alt="CI & Deploy" /></a>
  <a href="https://thalisonwilker.github.io/neo/"><img src="https://img.shields.io/endpoint?url=https://thalisonwilker.github.io/neo/coverage-badge.json" alt="Coverage" /></a>
  <a href="https://pypi.org/project/neo-cmd/"><img src="https://img.shields.io/badge/pypi%20package-v0.1.1-34D058" alt="PyPI Package" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.13+-34D058" alt="Python 3.13+" /></a>
  <a href="https://github.com/thalisonwilker/neo/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-34D058" alt="License: MIT" /></a>
</p>

O **Neo** (`neo-cmd`) é um assistente pessoal de linha de comando feito por dev, para devs que resolvem tudo pelo teclado. Desenvolvido em **Python 3.13** com **Typer** e **Rich**:

- **Disponível hoje:** integração unificada com **GitHub**, **Bitbucket Cloud** e **Shortcut** (`neo git` e `neo tasks`), quadros Kanban no terminal, saída estruturada via `--json` e credenciais protegidas no Keyring do SO.
- **No roadmap:** módulos para estudos, hobbies, lazer, finanças pessoais (receitas e despesas) e uma API para conectar qualquer ferramenta ao seu fluxo.

📚 **Documentação Completa:** **[thalisonwilker.github.io/neo](https://thalisonwilker.github.io/neo/)**

---

## Instalação

```bash
# Recomendado: instalar globalmente em ambiente isolado com uv ou pipx
uv tool install neo-cmd
# ou: pipx install neo-cmd
```

### Desenvolvimento Local

```bash
git clone https://github.com/thalisonwilker/neo.git
cd neo
uv sync
uv run neo --help
```

---

## Veja na Prática

```bash
# 1. Autentique seus provedores no Keyring do sistema operacional (entrada oculta)
neo git auth login --provider github
neo git config set provider github
neo git config set workspace minha-organizacao

# 2. Confira o diagnóstico do repositório local e das integrações
neo git status
neo git auth status

# 3. Navegue por workspaces, repositórios e commits (GitHub ou Bitbucket Cloud)
neo git workspace list
neo git repo list --limit 10
neo git commits search --query "fix" --limit 5

# 4. Veja o quadro Kanban (A fazer | Fazendo | Feito) e analise tasks no Shortcut
neo tasks resume
neo tasks analyze 2108

# 5. Configure e inicie o agente de codificação (Google Antigravity CLI) e provedores SDD
neo config agent set command agy
neo config agent set model "Gemini 3.8 Flash"
neo config agent set sdd-provider spec-driven
neo agent status
neo agent setup --yes
neo agent run

# 6. Combine com --json e jq para criar scripts e automações
neo git repo list --json | jq '.[] | {slug, main_branch}'
```

---

## Qualidade & Testes

```bash
uv run pytest --cov=neo     # Testes unitários e E2E (cobertura >= 80%)
uv run ruff check .         # Linter e formatação
uv run mypy src             # Checagem estática de tipos (strict)
```

---

## Licença

Distribuído sob a licença livre **MIT**. Consulte o arquivo [LICENSE](https://github.com/thalisonwilker/neo/blob/main/LICENSE) para mais detalhes.
