---
name: mvp-canvas
description: Canvas do MVP do Neo — proposta, personas, jornadas, funcionalidades e métricas.
alwaysApply: false
---

# MVP Canvas — Neo (Personal Command Assistant)

> Lean Inception (Paulo Caroli). O MVP é a menor coisa que gera aprendizado validado, não a versão "pequena" do produto final.

## 1. Proposta do MVP (visão)
Entregar uma CLI unificada em Python/Typer que permita ao desenvolvedor consultar e investigar repositórios no Bitbucket e stories no Shortcut em segundos, correlacionando dados de bugs com histórico de commits sem sair do terminal.

## 2. Personas e segmentos do MVP
- Desenvolvedor de software focado em entregas.
- Tech Lead / Engenheiro responsável por triagem e investigação de incidentes.

## 3. Jornadas cobertas no MVP
1. **Início do dia:** Listagem de demandas prioritárias atribuídas ao usuário no Shortcut (`neo story list --mine`).
2. **Navegação de código:** Busca, listagem e clone de repositórios do Bitbucket (`neo repo list/clone`).
3. **Investigação de bugs:** Correlação automática entre card de bug e histórico de commits/PRs (`neo bug investigate <id>`).

## 4. Funcionalidades do MVP (sequenciadas)

| # | Funcionalidade | Valor | Esforço | Entra no MVP? |
|---|----------------|-------|---------|---------------|
| 1 | Fundação CLI + Configuração segura via Keyring/config.toml | Alto | Baixo | Sim |
| 2 | Integração Bitbucket (repositórios, clone, commits) | Alto | Baixo | Sim |
| 3 | Integração Shortcut (stories list, show, analyze) | Alto | Médio | Sim |
| 4 | Serviço de Análise Cruzada (`neo bug investigate <id>`) | Alto | Médio | Sim |
| 5 | Output Rich (tabelas e cards) + flag `--json` universal | Alto | Baixo | Sim |
| 6 | Módulos de vida pessoal (`fitness`, `cycling`, `study`) | Médio | Alto | Depois (Onda 2) |
| 7 | Assistente em linguagem natural (`neo ask`) | Alto | Alto | Depois (Onda 3) |

## 5. Resultado esperado / como validar
- O desenvolvedor consegue resolver uma triagem de bug ou verificar seus cards diários em menos de 10 segundos diretamente pelo terminal.
- 100% das operações destrutivas ou de criação exigem confirmação explícita.
- Zero vazamentos de credenciais no terminal ou em logs de debug.

## 6. Custo e cronograma
- Greenfield, desenvolvimento focado em Python 3.13 com Typer e uv.
- MVP entregue em ciclos pequenos com cobertura de testes unitários e mocks de borda.

## 7. Hipóteses e aprendizados

| Hipótese | Como medir | Resultado |
|----------|------------|-----------|
| A consulta cruzada Shortcut + Bitbucket via terminal poupa mais de 5 minutos por incidente analisado | Tempo de investigação medido em casos reais de bugs | A validar no MVP |
| O armazenamento de tokens via Keyring atende desenvolvedores em macOS e Linux sem atrito | Ausência de erros de setup de credenciais no onboarding | A validar no MVP |
