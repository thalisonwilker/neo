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
| **Agent Code / Agente de Codificação** | Ferramenta ou agente de IA executável no terminal responsável por auxiliar na escrita e refatoração de código (ex.: Antigravity CLI via comando `agy`) | Script de automação simples ou chamada direta de API de LLM | `Agent & SDD Orchestration` |
| **Antigravity CLI (agy)** | Interface oficial de linha de comando do Google Antigravity para interação com agentes no terminal | Gemini CLI ou SDKs de modelos puros | `Agent & SDD Orchestration` |
| **Branch** | Linha independente de desenvolvimento em um repositório Git (`main`, `feature/*`, `bugfix/*`), identificada pelo nome e hash do último commit | Tag estática ou fork de repositório | `Git Integration` |
| **Commit** | Registro imutável de alteração no histórico de um repositório Git, identificado por um hash SHA | Task ou story de gerenciamento de projeto | `Git Integration` |
| **Keyring** | Cofre de credenciais nativo do sistema operacional (Keychain no macOS, Secret Service no Linux, Credential Manager no Windows) acessado via biblioteca `keyring` | Arquivo `.env` em texto puro ou `config.toml` | `Configuration & Secrets` |
| **Module / Módulo** | Domínio de primeiro nível da CLI (ex.: `neo git`, `neo tasks`) | Pacote externo instalado via `pip` | `CLI & Commands` |
| **Model / Modelo** | Identificador do modelo de linguagem/raciocínio repassado ao agente de codificação (ex.: `Gemini 3.8 Flash`) | Provedor de Git ou serviço de tarefas | `Agent & SDD Orchestration` |
| **Provider / Provedor** | Plataforma de hospedagem Git suportada pela interface comum do Neo (`github` para GitHub e `bitbucket` para Bitbucket Cloud) | Serviço de gestão de tarefas (`shortcut`) | `Git Integration` |
| **Pull Request (PR)** | Proposta de merge entre duas branches submetida a revisão no provedor Git | Commit isolado ou merge local | `Git Integration` |
| **SDD Provider / Provedor SDD** | Ferramenta ou esteira de desenvolvimento orientado a especificações (ex.: `spec-driven` e `spec-kit`) | Provedor de repositórios Git | `Agent & SDD Orchestration` |
| **Repository (Repo)** | Repositório de código hospedado no provedor Git, identificado por um `slug` dentro de um `workspace` | Diretório qualquer no sistema de arquivos sem Git | `Git Integration` |
| **Story / Card** | Unidade de trabalho, feature, bug ou chore gerenciada no Shortcut | Issue de repositório Git | `Shortcut Integration` |
| **Workspace** | Conceito unificado no Neo para o escopo proprietário dos repositórios: equivale a um **Workspace** no Bitbucket Cloud e a uma **Organization** ou **conta pessoal de usuário** no GitHub | Pasta local de trabalho no computador | `Git Integration` |
