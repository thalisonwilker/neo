---
name: adr-0004
description: Decisão sobre armazenamento seguro de credenciais e confirmação de operações.
alwaysApply: false
---

# ADR-0004: Gestão de Credenciais e Segurança Operacional

- **Status:** aceito
- **Data:** 2026-10-27
- **Decisores:** Time do Projeto Neo

## Contexto
O Neo lida com credenciais sensíveis (App Passwords do Bitbucket e tokens da API do Shortcut) com permissões de leitura e criação de código e stories. Além disso, comandos podem executar operações destrutivas ou de alteração (como criação ou exclusão de branches e repositórios).

## Decisão
1. **Armazenamento Seguro de Segredos:**
   - O Neo utilizará a biblioteca `keyring` do Python para delegar o armazenamento de tokens ao chaveiro seguro do sistema operacional (macOS Keychain, Windows Credential Manager, SecretService no Linux).
   - Suporte a variáveis de ambiente (`BITBUCKET_TOKEN`, `SHORTCUT_API_TOKEN`) para ambientes de CI/CD ou servidores headless.
   - Fallback para arquivo `~/.config/neo/config.toml` protegido com permissões restritas do sistema de arquivos (`0600`), caso o keyring não esteja disponível.
2. **Prevenção de Vazamento em Logs:**
   - Logs de depuração (inclusive com `--verbose`) devem mascarar tokens e dados de autorização nos headers HTTP.
3. **Segurança de Ações Relevantes:**
   - Comandos que realizem operações com impacto (criação de repositório, exclusão, etc.) exigem flag `--yes` / `--force` ou prompt interativo explícito de confirmação (`typer.confirm`).

## Consequências
- **+** Segurança de padrão industrial sem tokens expostos em arquivos de texto plano por padrão.
- **+** Automações seguras e sem risco de execução involuntária de comandos com efeito colateral.
- **−** Em ambientes Linux sem daemon de keyring (ex: containers Docker mínimos), o usuário precisará usar variáveis de ambiente ou arquivo de configuração local protegido.
