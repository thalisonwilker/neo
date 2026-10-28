---
name: glossary
description: Linguagem ubíqua do projeto Neo.
alwaysApply: false
---

# Glossário — Linguagem Ubíqua

> A fonte única do vocabulário do sistema Neo. O mesmo termo aparece aqui, na spec e no código. Sem sinônimos.

| Termo | Definição | NÃO confundir com | Contexto (bounded context) |
|---|---|---|---|
| **Analysis / Análise** | Processo de correlacionar dados de uma demanda ou bug com o histórico de commits e código | Telemetria ou profiling de performance | `Analysis & Correlation` |
| **App Password** | Credencial de aplicação gerada no Bitbucket com escopos restritos para a CLI | Senha pessoal da conta Atlassian | `Bitbucket Integration` |
| **Branch** | Linha independente de desenvolvimento em um repositório Git (`main`, `feature/*`, `bugfix/*`), identificada pelo nome e hash do último commit | Tag estática ou fork de repositório | `Git Integration` |
| **Bug Investigation** | Fluxo automático que busca um card no Shortcut e varre o Bitbucket por commits e PRs relacionados | Debugging interativo de código em IDE | `Analysis & Correlation` |
| **Commit** | Registro imutável de alteração no histórico de um repositório Git no Bitbucket | Task ou subtask de desenvolvimento | `Bitbucket Integration` |
| **Keyring** | Chaveiro seguro nativo do sistema operacional (Keychain no macOS, SecretService no Linux) | Arquivo de texto `.env` | `Configuration & Secrets` |
| **Module / Módulo** | Subcomando ou domínio independente da CLI (ex: `git`, `tasks`, `study`) | Biblioteca Python instalada no `site-packages` | `CLI & Commands` |
| **Pull Request (PR)** | Proposta de integração de branch no Bitbucket submetida a revisão | Merge direto de branch local | `Bitbucket Integration` |
| **Repository (Repo)** | Repositório de código hospedado no Bitbucket | Pasta local no disco | `Bitbucket Integration` |
| **Story / Card** | Unidade de trabalho, bug ou demanda gerenciada no Shortcut | Épico ou milestone global | `Shortcut Integration` |
