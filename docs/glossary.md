---
name: glossary
description: Linguagem ubíqua do projeto Neo.
alwaysApply: false
---

# Glossário — Linguagem Ubíqua

> Vocabulário oficial do sistema Neo. O mesmo termo aparece aqui, nas especificações (`specs/`), no código e na interface de linha de comando.

| Termo | Definição | NÃO confundir com | Contexto (bounded context) |
|---|---|---|---|
| **API Token / Personal Access Token** | Credencial de autenticação gerada no provedor Git (Personal Access Token no GitHub; API Token combinado com e-mail no Bitbucket Cloud, onde *App Passwords* foram descontinuadas) | Senha de login da conta web ou chave SSH | `Configuration & Secrets` |
| **Analysis / Análise** | Processo de inspecionar uma demanda e correlacioná-la com branches, commits e critérios de aceite | Telemetria ou profiling de performance | `Analysis & Correlation` |
| **Branch** | Linha independente de desenvolvimento em um repositório Git (`main`, `feature/*`, `bugfix/*`), identificada pelo nome e hash do último commit | Tag estática ou fork de repositório | `Git Integration` |
| **Commit** | Registro imutável de alteração no histórico de um repositório Git, identificado por um hash SHA | Task ou story de gerenciamento de projeto | `Git Integration` |
| **Keyring** | Cofre de credenciais nativo do sistema operacional (Keychain no macOS, Secret Service no Linux, Credential Manager no Windows) acessado via biblioteca `keyring` | Arquivo `.env` em texto puro ou `config.toml` | `Configuration & Secrets` |
| **Module / Módulo** | Domínio de primeiro nível da CLI (ex.: `neo git`, `neo tasks`) | Pacote externo instalado via `pip` | `CLI & Commands` |
| **Provider / Provedor** | Plataforma de hospedagem Git suportada pela interface comum do Neo (`github` para GitHub e `bitbucket` para Bitbucket Cloud) | Serviço de gestão de tarefas (`shortcut`) | `Git Integration` |
| **Pull Request (PR)** | Proposta de merge entre duas branches submetida a revisão no provedor Git | Commit isolado ou merge local | `Git Integration` |
| **Repository (Repo)** | Repositório de código hospedado no provedor Git, identificado por um `slug` dentro de um `workspace` | Diretório qualquer no sistema de arquivos sem Git | `Git Integration` |
| **Story / Card** | Unidade de trabalho, feature, bug ou chore gerenciada no Shortcut | Issue de repositório Git | `Shortcut Integration` |
| **Workspace** | Conceito unificado no Neo para o escopo proprietário dos repositórios: equivale a um **Workspace** no Bitbucket Cloud e a uma **Organization** ou **conta pessoal de usuário** no GitHub | Pasta local de trabalho no computador | `Git Integration` |
