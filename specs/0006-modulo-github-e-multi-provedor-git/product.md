---
name: product
description: Visão de produto para integração com GitHub e suporte a múltiplos provedores Git na CLI Neo.
alwaysApply: false
---

# Product — Módulo GitHub e Suporte a Múltiplos Provedores Git

> **Tier:** arquitetural · **Status:** aprovado · **Dono:** Thalyson Wilker

## Problema
Desenvolvedores e equipes frequentemente utilizam múltiplos provedores de código Git simultaneamente (ex.: Bitbucket para sistemas corporativos/legados e GitHub para microsserviços modernos, projetos open-source ou bibliotecas internas). Atualmente, a CLI Neo possui acoplamento rígido aos endpoints do Bitbucket nos comandos `repo`, `commits` e `workspace`, exigindo que o usuário alterne manualmente ou não consiga operar sobre repositórios hospedados no GitHub com a mesma ergonomia e eficiência.

## Para quem
- Engenheiros de software e tech leads que atuam em ecossistemas híbridos (Bitbucket + GitHub).
- Usuários da CLI Neo que precisam criar, listar, clonar e inspecionar commits em ambos os serviços sem fricção.

## Resultado esperado / métrica de sucesso
- **Flexibilidade total de provedor:** O usuário consegue listar e clonar repositórios tanto do Bitbucket quanto do GitHub usando os mesmos comandos da CLI (`neo repo`, `neo commits`, `neo workspace`).
- **Zero atrito de contexto:** O Neo detecta automaticamente o provedor certo a partir do remote Git do diretório de trabalho atual em 100% dos repositórios locais.
- **Configuração simples:** Gerenciamento seguro de token do GitHub via Keyring nativo (`neo config auth set github`) e definição de provedor padrão.

## Goals
- Adicionar o serviço `github` ao gerenciador seguro de credenciais do Neo (`Keyring`, `config.toml` e variável `GITHUB_TOKEN`).
- Implementar cliente HTTP REST para a API oficial do GitHub (`https://api.github.com`).
- Introduzir abstração unificada de provedor Git (`GitProvider`) para desacoplar a camada de comandos das integrações de transporte específicas.
- Permitir configurar o provedor Git padrão (`neo config set-provider <github|bitbucket>`) e forçar pontualmente com a flag `--provider / -p`.
- Implementar auto-detecção do provedor Git a partir da URL do remote `origin` local (`github.com` vs `bitbucket.org`).
- Suportar listagem e seleção de owners/organizações no GitHub através de `neo workspace`.

## Non-goals
- Implementar suporte a GitLab nesta feature (arquitetura ficará aberta para isso em onda futura).
- Substituir a CLI oficial `gh` em funcionalidades administrativas complexas (Actions secrets, releases, etc.).

## Riscos / premissas
- Premissa: O usuário possui um Personal Access Token (PAT) do GitHub com permissões `repo` e `read:org`.
- Risco: Diferenças conceituais entre o modelo de dados do GitHub (repositórios pertencem a usuários ou organizações) e do Bitbucket (pertencem a workspaces/projetos).
  - Mitigação: Unificação conceitual via DTOs neutros de domínio (`GitRepo`, `GitCommit`, `GitWorkspace`).
