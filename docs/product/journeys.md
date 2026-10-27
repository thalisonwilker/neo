---
name: journeys
description: Resumo das jornadas do usuário com o Neo — etapas, dores e oportunidades.
alwaysApply: false
---

# Jornadas do Produto — Neo

> As jornadas que o produto precisa cobrir ponta a ponta, do ponto de vista da persona (Lean Inception).

## Jornada 1: Início do dia e seleção de demanda (Shortcut)
- **Persona:** Desenvolvedor Focado · **Objetivo:** Descobrir a próxima prioridade de trabalho e preparar o ambiente local.
- **Etapas:**
  1. Abre o terminal no início da jornada de trabalho.
  2. Executa `neo story list --mine` para visualizar stories em andamento ou prontas para desenvolvimento.
  3. Identifica a story e executa `neo story show <id>` para ler descrição, critérios de aceite e links.
  4. Executa `neo repo clone <repo>` ou navega ao repositório correspondente e cria a branch de trabalho associada.
- **Dores / atritos atuais:** Abrir o browser, autenticar no Shortcut, buscar filtros, copiar ID do card, abrir Bitbucket e clonar manualmente.
- **Oportunidades com o Neo:** Resumo visual direto no terminal em menos de 3 segundos, com comandos encadeáveis.

## Jornada 2: Investigação de Bug ou Regressão (Shortcut + Bitbucket)
- **Persona:** Tech Lead / Investigador de Incidentes · **Objetivo:** Identificar o commit e branch que introduziram uma regressão reportada em um card de bug.
- **Etapas:**
  1. Recebe o alerta de incidente ou número do card no Shortcut (ex: 5678).
  2. Executa `neo bug investigate 5678`.
  3. O Neo busca o card no Shortcut, extrai palavras-chave, componentes afetados e IDs de branches/PRs mencionadas.
  4. O Neo consulta o Bitbucket em busca de commits e pull requests que referenciam o card ou termos correlatos.
  5. O Neo exibe um relatório consolidado com: histórico do card, commits suspeitos, autores e diffs relevantes.
- **Dores / atritos atuais:** Ler o card na web, abrir o Bitbucket, vasculhar histórico de git log ou PRs fechados, cruzar datas manualmente.
- **Oportunidades com o Neo:** Análise cruzada automatizada (`neo/services/analysis.py`), poupando minutos preciosos em momentos de crise.

## Jornada 3: Gestão e Exploração de Repositórios (Bitbucket)
- **Persona:** Desenvolvedor Focado · **Objetivo:** Localizar rapidamente um serviço da organização, inspecionar branches e clonar para a máquina.
- **Etapas:**
  1. Executa `neo repo list` ou `neo repo search <termo>`.
  2. Encontra o repositório correto entre dezenas de microsserviços da empresa.
  3. Executa `neo repo clone <projeto>` (que já configura remotes e diretório padrão).
  4. Consulta commits recentes ou branches ativas com `neo commits search --author <usuario>` ou `neo repo branches <repo>`.
- **Dores / atritos atuais:** Pesquisa lenta na interface web do Bitbucket, copiar URLs SSH, criar pastas locais manualmente.
- **Oportunidades com o Neo:** Fluxo contínuo sem sair da linha de comando.
