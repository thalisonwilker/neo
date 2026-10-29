---
name: spec
description: Contrato e critérios de aceite para contexto ativo de trabalho (Git ↔ Tasks) e nova visualização em seções do neo config show.
alwaysApply: true
---

# Spec — 0017 Contexto Ativo de Trabalho e Config Show por Seções

> **Fonte da verdade.** Status: aprovado
> Contrato de entrega para correlação ativa entre Git e Tasks (detecção de task ativa, contagem de commits) e formatação modular em seções estilizadas para `neo config show`.

## Resumo
Permite que o desenvolvedor correlacione o repositório Git local à demanda ativa do Shortcut (com detecção automática via branch e comandos `neo tasks bind` / `neo tasks unbind`), conte os commits associados à task e exiba uma visão consolidada em seções (`GIT`, `TASKS`, `AGENT`) no comando `neo config show` (tanto no terminal formatado via Rich quanto em `--json`).

## Critérios de Aceite

### AC-1: Resolução e Vínculo de Task Ativa (Git ↔ Tasks)
- **Dado** um repositório Git local,
- **Quando** a branch atual possuir um identificador de história no nome (padrões suportados: `feature/sc-1234-nome`, `sc-1234`, `fix/1234-slug`, `story/1234`),
- **Então** o Neo deve extrair automaticamente o ID da task ativa (ex.: `1234`).
- **E Quando** o comando `neo tasks bind <story_id>` for executado,
- **Então** o ID da história deve ser persistido como task ativa para o repositório local em `.git/neo-context.json` (com precedência sobre a inferência de branch).
- **E Quando** o comando `neo tasks unbind` for executado,
- **Então** a vinculação manual deve ser removida.

### AC-2: Contagem de Commits Vinculados à Task no Repositório Ativo
- **Dado** um repositório Git local e uma task ativa resolvida,
- **Quando** o Neo calcular as métricas da demanda no repositório,
- **Então** deve identificar a quantidade de commits realizados na branch atual em relação à branch base (`default-branch` ou `main`), ou que contenham o ID da task na mensagem do commit, reportando o número inteiro de commits vinculados.

### AC-3: Visualização em Seções Estilizadas em `neo config show`
- **Dado** o comando `neo config show` executado no terminal (modo visual humano),
- **Quando** a saída for renderizada,
- **Então** deve apresentar painéis Rich distintos e bem delineados para:
  1. **`[GIT : STATUS CONFIGURAÇÃO]`**:
     - `PROVEDOR`: nome do provedor (`github` ou `bitbucket`) e camada de resolução (`remote`, `config`, etc.).
     - `WORKSPACE`: slug do workspace ou organização resolvido.
     - `REPOSITÓRIO`: nome/slug do repositório detectado no Git local ou configurado.
     - `BRANCH`: nome da branch atual (com status limpo/sujo se aplicável).
     - `TASK ATIVA`: ID da task vinculada e título resumido (ou `Nenhuma vinculada`).
  2. **`[TASKS : DEMANDA ATIVA]`**:
     - `PROVEDOR`: serviço de tarefas ativo (`Shortcut (API v3)`).
     - `STATUS`: estado de autenticação no Keyring (`Configurado` ou `Não configurado`).
     - `USUÁRIO`: nome e username do membro autenticado (via cache/chamada com fallback gracioso).
     - `WORKSPACE`: nome do workspace/projeto no serviço de tarefas.
     - `REPOSITÓRIO ATIVO`: repositório Git associado à sessão atual.
     - `COMMITS NA TASK`: quantidade de commits contabilizados para a demanda no repositório.
  3. **`[AGENT : AGENTES & SDD]`**:
     - `PROVEDOR`: identidade do adaptador (`antigravity / agy`).
     - `STATUS`: disponibilidade no PATH e versão do executável.
     - `MODELO`: identificador do modelo padrão configurado (`Gemini 3.8 Flash`).
     - `USAGE`: barra gráfica visual proporcional de utilização/cota.
     - `PROVEDOR SDD`: provedor SDD ativo (`spec-driven` ou `spec-kit`).

### AC-4: Payload Estruturado em `neo config show --json`
- **Dado** o comando `neo config show --json`,
- **Quando** for invocado,
- **Então** a saída JSON emitida no `stdout` deve conter os blocos estruturados:
  - `git`: `provider`, `provider_source`, `workspace`, `repo`, `branch`, `active_task` (objeto ou `null`).
  - `tasks`: `service`, `status`, `user` (objeto ou `null`), `workspace`, `active_repo`, `task_commits` (inteiro).
  - `agent`: `adapter`, `command`, `model`, `sdd_provider`, `available`, `version`, `usage` (objeto com métricas/percentual).

### AC-5: Resiliência Fora de Repositório Git e Modo Offline
- **Dado** a execução de `neo config show` fora de uma pasta Git ou sem conectividade com a API do Shortcut,
- **Quando** for executado,
- **Então** os campos dependentes de Git devem exibir `Não detectado (fora de repositório Git)`, a checagem do membro do Shortcut deve falhar graciosamente sem lançar traceback, e o comando deve encerrar com código de saída `0`.

### AC-6: Documentação e Testes Automatizados
- **Dado** a implementação das novas opções e formatos,
- **Quando** a suíte de testes for executada,
- **Então** testes unitários e E2E devem cobrir a inferência de branch, `bind`/`unbind`, contagem de commits e a nova saída visual/JSON, e a documentação deve compilar com `uv run mkdocs build --strict`.

## Casos de Borda e Erros
- Branch sem numeração (ex.: `main` ou `develop`): não detecta task ativa automaticamente e exibe `Nenhuma vinculada`.
- Repositório Git local recém-criado sem nenhum commit: contagem de commits retorna `0` sem falhar.
- Falha na API do Shortcut ao consultar membro: exibe `Conectado (offline / perfil não consultado)` mantendo o status de autenticação do Keyring.

## Fora de Escopo
- Envio de commits para branches remotas.
- Múltiplos agentes com subprocessos concorrentes (escopo da Fase 2 / Feature 0018).

## Rastreabilidade
- Tasks: `./tasks.md`
- Código de comandos: `src/neo/commands/config.py`, `src/neo/commands/tasks.py`
- Serviços de suporte: `src/neo/services/`

