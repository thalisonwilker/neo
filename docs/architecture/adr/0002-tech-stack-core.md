---
name: adr-0002
description: Decisão sobre Tech Stack principal do Neo.
alwaysApply: false
---

# ADR-0002: Tech Stack Principal (Python, Typer, uv, Rich, httpx)

- **Status:** aceito
- **Data:** 2026-10-27
- **Decisores:** Time do Projeto Neo

## Contexto
O Neo precisa ser uma CLI moderna, de alta velocidade de desenvolvimento, com suporte a tipagem estática, excelente tratamento de argumentos e subcomandos, saída visual rica no terminal e consumo eficiente de APIs HTTP.

## Decisão
Vamos utilizar:
1. **Linguagem & Runtime:** Python >= 3.13.
2. **Framework de CLI:** Typer (baseado em Click e type hints nativos de Python).
3. **Gerenciador de Pacotes e Ambiente:** `uv` (rápido, determinístico, gerenciamento de lockfile moderno).
4. **UX de Terminal:** Rich (renderização de tabelas, formatação com cores, status/spinners e Markdown).
5. **Cliente HTTP:** `httpx` para comunicação com APIs REST do Bitbucket e Shortcut (suporte a sync/async e tipagem).

Alternativas descartadas:
- *Go / Rust:* Maior complexidade para prototipagem rápida de regras de negócio e futuras integrações de IA e plugins dinâmicos em Python.
- *Argparse / Click puro:* Typer oferece melhor ergonomia com tipagem moderna de Python e geração automática de help e validações.
- *Poetry / Pipenv:* `uv` é exponencialmente mais rápido e integra-se perfeitamente ao ecossistema Python moderno.

## Consequências
- **+** Desenvolvimento ágil, tipado e com validação automática de parâmetros.
- **+** Facilidade no empacotamento e execução local via `uv run` ou distribuição via PyPI / `uv tool install`.
- **−** Necessidade de garantir que o ambiente Python >= 3.13 esteja acessível na máquina do usuário.
