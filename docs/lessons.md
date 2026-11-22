---
name: lessons
description: Aprendizados transversais e gotchas descobertos durante o trabalho — quirks de lib, armadilhas de setup, suposições que se provaram erradas. Área de staging volátil que se auto-poda (o que estabiliza vira ADR/glossary/CLAUDE.md/TESTING e sai daqui). Puxe quando for mexer numa área com histórico de armadilha, ou antes de tomar uma decisão que já esbarrou num gotcha registrado.
alwaysApply: false
---

# LESSONS — Aprendizados & gotchas

- Rich respeita `NO_COLOR` mesmo com `force_terminal=True`; testes de cores precisam definir `no_color=False` explicitamente.
- O `.gitignore` da raiz ignora qualquer `lib/` (empacotamento Python) e engolia `web/src/lib/` do painel: ao criar pastas novas em `web/`, confira com `git check-ignore -v <caminho>` antes de commitar.
- O Clerk gera `redirect_url` **absoluto** (ex.: `http://localhost:3100/dashboard/overview`); a validação do destino pós-login precisa aceitar URL absoluta da mesma origem e reduzi-la a caminho + consulta.

> **Área de staging, não cemitério.** Registra o que se aprende na marra: quirks de biblioteca,
> armadilhas de ambiente, suposições que quebraram. É **volátil** — diferente do **ADR** (decisão
> durável) e do **STATE** (o que estamos fazendo agora). A lição que **estabiliza** é **promovida**
> e **removida** daqui (ver poda abaixo). Se este arquivo cresce sem parar, a poda não está rolando.

## Como usar
- **Captura inline (na hora):** ao corrigir um erro não-óbvio, quebrar uma suposição ou descobrir
  um gotcha, adicione **1 linha aqui na hora** — não espere o handoff (o detalhe some).
- **Consolidação (no `/handoff`):** ao pausar, revise as lições da sessão: alguma duplicada?
  alguma já estabilizou → **promova e remova**.

### Poda — para onde a lição vai quando amadurece
| A lição virou… | Vai para | Sai daqui |
|---|---|---|
| Decisão difícil de reverter | ADR (`docs/architecture/adr/`) | ✅ |
| Termo/conceito de negócio | `docs/glossary.md` | ✅ |
| Convenção de código/agente | `CLAUDE.md` | ✅ |
| Padrão de teste/quality gate | `docs/engineering/TESTING.md` | ✅ |
| Gotcha que ainda não estabilizou | **fica aqui** | — |

## Aprendizados ativos
> Formato: `- <YYYY-MM-DD> · <área/arquivo> · o gotcha em 1 linha · como evitar/mitigar`.
> Mantenha acionável e curto. Se não é acionável, não é uma lição — é desabafo.

- 2026-11-04 · `tests/unit/test_github_client.py` · Clientes Git também consultam o workspace configurado na máquina durante testes unitários · Isolar configuração e variável `NEO_GIT_WORKSPACE` nas fixtures.

- 2026-11-04 · `tests/e2e/` · O Rich pode intercalar escapes ANSI dentro de opções como `--path` no CI · Remover ANSI antes de comparar texto e testar com e sem cores.

- 2026-10-28 · `tests/e2e/` · Testes E2E de Git que não isolam `neo.config.DEFAULT_CONFIG_DIR` e `DEFAULT_CONFIG_FILE` leem o `~/.config/neo/config.toml` real da máquina host · Sempre usar `patch("neo.config.DEFAULT_CONFIG_DIR", tmp_path)` e `patch("neo.config.DEFAULT_CONFIG_FILE", tmp_path / "config.toml")` em fixtures de testes E2E.
- 2026-11-04 · Bitbucket Cloud · `PUT /repositories/{workspace}/{repo_slug}` também pode criar um repositório · Consultar a existência antes de editar e considerar a corrida entre consulta e atualização.

## Promovidas (histórico curto)
> Rastro de para onde foram as lições podadas — só o link, sem reexplicar. Poda este histórico também.
- <YYYY-MM-DD: "<lição>" → [ADR-NNNN](architecture/adr/NNNN-*.md) / glossary / CLAUDE.md>

- Em sandbox sem escrita em `~/.cache/uv`, execute os gates com `UV_CACHE_DIR=/tmp/neo-uv-cache`.

- 2026-11-05 · Bitbucket Cloud · A criação de repositórios no Bitbucket requer a propriedade `key` do projeto no payload (`{"project": {"key": "<KEY>"}}`); enviar o UUID `{...}` causa erro 400 da API · Usar e persistir sempre a `key` do projeto retornada pela API.
