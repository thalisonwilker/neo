---
name: spec
description: Remoção dos grupos Git auth e workspace da interface da CLI.
alwaysApply: true
---

# Spec — Remover grupos Git auth e workspace

> **Fonte da verdade.** Status: implementado · Tier: pequeno

## Resumo

Remove os grupos `neo git auth` e `neo git workspace`; a configuração de credenciais e workspace permanece no grupo `neo git config`. Este contrato substitui os trechos correspondentes das specs 0014 e 0023.

## Critérios de aceite

### AC-1: Remoção dos grupos
- **Dado** `neo git --help`, **quando** o usuário consulta os comandos ou tenta executar `neo git auth` ou `neo git workspace`, **então** os grupos não aparecem na ajuda e são rejeitados como comandos desconhecidos com código 2.

### AC-2: Configuração preservada
- **Dado** um provedor Git configurado, **quando** usa `neo git config set|get|list|unset api-key`, **então** mantém o fluxo de validação, armazenamento e consulta sem expor credenciais definido na spec 0023.
- **E** `neo git config set|get|list|unset workspace` continua funcional, assim como a resolução de workspace, `--workspace` nos comandos restantes e `neo git status`.

### AC-3: Documentação atualizada
- **Dado** o README e a documentação da CLI, **quando** o usuário consulta instruções atuais, **então** encontra `neo git config` para credenciais e workspace, sem instruções para executar os grupos removidos; a documentação de migração pode mencioná-los como históricos.

## Fora de escopo
- Remover o conceito de workspace, os métodos de integração de provedores ou o armazenamento de credenciais.

## Rastreabilidade
- [Tasks](tasks.md) · [Spec 0023](../0023-atualizacao-comandos-git/spec.md)
