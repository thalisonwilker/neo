---
name: spec
description: Contrato e critérios de aceite para agentes especializados multi-role (codificação, refinamento de tarefas, revisão de PR e auditoria de DoD).
alwaysApply: true
---

# Spec — 0018 Agentes Especializados Multi-Role

> **Fonte da verdade.** Status: rascunho / em aprovação
> Contrato de entrega para expansão do módulo `neo agent` com papéis de atuação especializados (`code`, `refine`, `review-pr`, `review-task`), injeção de contexto ativo e configuração modular de modelos.

## Resumo
Permite que o desenvolvedor execute agentes com responsabilidades bem definidas além da codificação tradicional: refinamento de tarefas do Shortcut antes de iniciar o desenvolvimento, revisão técnica de Pull Requests em relação à spec, e auditoria de Definition of Done e critérios de aceite para encerramento de demandas.

## Papéis de Atuação (Roles)

| Identificador | Papel | Objetivo Principal | Edita código de produção? | Contexto Injetado |
|---|---|---|---|---|
| `code` | Codificador | Implementação técnica de specs e correção de bugs | Sim | Spec ativa, arquivos do projeto |
| `refine` | Refinador de Demandas | Decomposição de histórias, critérios de aceite e Definition of Ready | Não | Demanda ativa do Shortcut (ID, título, descrição) |
| `review-pr` | Revisor de PR | Análise de diffs, conformidade com a spec, segurança e boas práticas | Não | Commits da branch, `git diff` vs branch base |
| `review-task` | Auditor de DoD | Validação de critérios de aceite (AC-N), suíte de testes e Definition of Done | Não | Status de testes, cobertura, spec e tasks |

---

## Critérios de Aceite

### AC-1: Catálogo de Papéis Especializados (`neo agent roles`)
- **Dado** a execução do comando `neo agent roles`,
- **Quando** executado no terminal,
- **Então** deve exibir uma tabela ou painel com os papéis suportados (`code`, `refine`, `review-pr`, `review-task`), suas descrições e o modelo configurado para cada um.
- **E Quando** executado com `--json`,
- **Então** deve emitir no `stdout` um JSON estruturado com a lista de papéis e metadados.

### AC-2: Execução com Seleção de Papel (`neo agent run --role <papel>`)
- **Dado** o comando `neo agent run`,
- **Quando** o argumento `--role <papel>` (ou `-r <papel>`) for informado com um papel válido,
- **Então** o Neo deve iniciar a sessão interativa do agente aplicando o perfil e instruções correspondentes àquele papel.
- **E Quando** a opção `--role` for omitida,
- **Então** deve assumir o papel padrão `code` (retrocompatibilidade).
- **E Quando** for fornecido um papel não suportado (ex.: `--role deploy`),
- **Então** deve falhar com código de saída `2` (`ExitCode.USAGE_ERROR`) e mensagem indicando os papéis válidos.

### AC-3: Injeção de Contexto Ativo da Demanda e Git
- **Dado** uma sessão iniciada com `--role refine` em um repositório com task ativa resolvida (via branch ou `neo tasks bind`),
- **Quando** o agente for invocado,
- **Então** o Neo deve formular o prompt interativo inicial repassando os dados da história (ID, título) e as diretrizes de refinamento de demandas sem alteração de código.
- **E Dado** uma sessão iniciada com `--role review-pr`,
- **Quando** o agente for invocado,
- **Então** o prompt inicial deve conter a lista de commits da branch e instruções para revisão técnica contra a spec.

### AC-4: Configuração de Modelo por Papel (`neo config agent`)
- **Dado** o comando `neo config agent set model.<papel> <nome_modelo>` (ex.: `model.refine` ou `model.review-pr`),
- **Quando** executado,
- **Então** persiste a preferência de modelo na seção `[agent]` do `config.toml`.
- **E Quando** `neo agent run --role <papel>` for executado,
- **Então** deve utilizar o modelo configurado para o papel (com fallback para o `model` geral se o específico não estiver definido).

### AC-5: Exibição no Diagnóstico `neo config show`
- **Dado** o comando `neo config show`,
- **Quando** o painel `AGENT : AGENTES & SDD` for exibido,
- **Então** deve listar os papéis suportados e indicar o modelo padrão/específico de cada um.

### AC-6: Documentação e Testes Automatizados
- **Dado** a entrega dos papéis especializados,
- **Quando** a suíte de testes for executada,
- **Então** testes unitários e E2E devem validar o catálogo de papéis, a injeção de contexto, resolução de modelos e os comandos da CLI, e a documentação deve compilar com `uv run mkdocs build --strict`.

---

## Casos de Borda e Erros
- Execução de `--role refine` fora de um repositório Git ou sem task ativa: o agente deve iniciar informando que nenhuma demanda ativa foi detectada e solicitar o ID ou tema a ser refinado.
- Execução de `--role review-pr` na branch padrão (`main`/`master`): deve avisar que a branch atual é a base e focar em commits recentes locais.

## Rastreabilidade
- Tasks: `./tasks.md`
- Módulo de agente: `src/neo/commands/agent.py`
- Adaptadores de agente: `src/neo/integrations/agents/`

