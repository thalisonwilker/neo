---
name: STATE
description: Memória de trabalho volátil do Neo — onde paramos, próximo passo, bloqueios.
alwaysApply: true
---

# STATE — Memória viva do projeto Neo

> Memória de trabalho entre sessões. É volátil: atualizada o tempo todo. Decisão estrutural → ADR; estado do trabalho → aqui. Atualize ao pausar/encerrar; leia ao retomar. Use a skill `/handoff`.

**Última atualização:** 2026-10-27 por Antigravity

## Em andamento / próximo passo
- **Fase atual:** Onda 1 (MVP). Features concluídas: `0002-fundacao-cli-e-configuracao`, `0003-modulo-bitbucket` e `0004-modulo-shortcut` (46 testes passando, 83.92% de cobertura, gates de ruff e mypy estritos limpos).
- **Próximo passo concreto:** Implementar a feature `specs/0005-analise-cruzada-investigacao-bugs/` (`neo bug investigate <id>`) correlacionando dados do Shortcut com commits e branches do Bitbucket.







## Decisões recentes
- 2026-10-27: Tech stack principal definido como Python >= 3.13, Typer, uv, Rich, httpx e keyring — [ADR-0002](architecture/adr/0002-tech-stack-core.md).
- 2026-10-27: Arquitetura em Monolito Modular (DDD) com isolamento de integrações em `integrations/` (ACL) e lógica em `services/analysis.py` — [ADR-0003](architecture/adr/0003-arquitetura-modular-e-integracoes.md).
- 2026-10-27: Gestão segura de credenciais via Keyring nativo de SO com fallback para arquivo com permissões restritas e variáveis de ambiente — [ADR-0004](architecture/adr/0004-gestao-de-credenciais-e-seguranca.md).
- 2026-10-27: Qualidade e testes com Ruff, Mypy estrito, Pytest e Respx — [ADR-0005](architecture/adr/0005-padroes-de-qualidade-e-testes.md).
- 2026-10-27: UX no terminal com Rich por padrão e flag global `--json` para automações — [ADR-0006](architecture/adr/0006-observabilidade-e-ux-cli.md).

## Bloqueios
- Nenhum bloqueio ativo.

## Ideias adiadas / backlog técnico
- Criação de plugins dinâmicos via entry points Python: reconsiderar quando a Onda 2 (módulos de vida pessoal) for iniciada.
- Integração com LLMs locais (Ollama): planejado para a Onda 3.

## Todos soltos
- [ ] Adicionar dependências core no `pyproject.toml` (`typer`, `rich`, `keyring`, `httpx`, `pydantic`) via `uv add`.
- [ ] Adicionar dependências de desenvolvimento (`ruff`, `mypy`, `pytest`, `pytest-cov`, `respx`) via `uv add --dev`.
