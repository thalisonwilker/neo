---
name: spec
description: Contrato da feature (critérios de aceite). Base enquanto a feature está ativa.
alwaysApply: true
---

# Spec — 0029 Refactor git config provider e api-key

> **Fonte da verdade.** Status: implementado
> Os critérios de aceite são (a) o contrato com o negócio, (b) o oráculo de teste,
> (c) o prompt para o agente de IA implementar. Escreva-os para serem executáveis.

## Resumo
Refatora os comandos `neo git config set provider` e `neo git config set api-key`. Ao definir um novo provedor (`github` ou `bitbucket`), todas as configurações anteriores da seção `[git]` em `config.toml` são resetadas, preservando unicamente o novo provedor. O comando `neo git config set api-key` recebe a chave de API via prompt interativo oculto sem solicitar e-mail para o Bitbucket (autenticação Bearer REST API conforme documentação Atlassian), testa a conexão com o provedor (GitHub ou Bitbucket) e exibe "Conexão efetuada" em caso de sucesso ou "Conexão recusada" (código de saída `3` - `AUTH_ERROR`) caso a chave seja inválida.

## Critérios de aceite

### AC-1: Reset das configurações Git ao definir novo provedor
- **Dado** um arquivo `config.toml` contendo configurações na seção `[git]` (como `workspace`, etc.).
- **Quando** o usuário executa `neo git config set provider <github|bitbucket>`.
- **Então** o Neo valida o provedor informado.
- **E** todas as outras chaves da seção `[git]` são removidas, mantendo apenas `provider = "<provedor>"`.
- **E** emite mensagem de sucesso confirmando a configuração atualizada.

### AC-2: Validação de chave de API do Bitbucket via Bearer Token (sem e-mail)
- **Dado** o provedor configurado como `bitbucket`.
- **Quando** o usuário executa `neo git config set api-key`.
- **Então** o Neo solicita apenas a chave de API com entrada oculta (`typer.prompt(..., hide_input=True)`), sem solicitar e-mail.
- **E** testa a autenticação chamando a API REST do Bitbucket com cabeçalho `Authorization: Bearer <token>`.
- **Se** a API responder com sucesso (HTTP 200), o Neo salva a credencial e exibe a mensagem de sucesso: `Conexão efetuada`.
- **Se** a API recusar a chave (HTTP 401/403/erro de autenticação), o Neo não substitui a credencial anterior, exibe a mensagem de erro `Conexão recusada` e encerra com código `3` (`AUTH_ERROR`).

### AC-3: Validação de chave de API do GitHub
- **Dado** o provedor configurado como `github`.
- **Quando** o usuário executa `neo git config set api-key`.
- **Então** o Neo solicita a chave de API com entrada oculta.
- **E** testa a autenticação chamando o endpoint `/user` da API REST do GitHub (conforme documentação da API).
- **Se** a autenticação tiver sucesso (HTTP 200), o Neo salva a credencial e exibe a mensagem de sucesso: `Conexão efetuada`.
- **Se** a chave for inválida ou a conexão for recusada (HTTP 401/403), o Neo exibe `Conexão recusada` e encerra com código `3` (`AUTH_ERROR`).

### AC-4: Rejeição de chave de API vazia ou passada como argumento
- **Dado** o comando `neo git config set api-key`.
- **Quando** o usuário informa um valor diretamente como argumento na linha de comando (`neo git config set api-key <chave>`).
- **Então** o Neo rejeita a execução com código `2` (`USAGE_ERROR`), instruindo que a chave deve ser fornecida via prompt oculto.
- **Quando** o usuário submete um valor vazio no prompt.
- **Então** o Neo rejeita com código `2` (`USAGE_ERROR`) informando que a chave não pode ser vazia.

## Matriz de decisão

| Comando | Provedor | Entrada | Conexão API | Resultado esperado | Código de saída | AC |
|---|---|---|---|---|---|---|
| `config set provider` | `github` ou `bitbucket` | Argumento válido | N/A | Seção `[git]` resetada com apenas `provider = <valor>` | `0` | AC-1 |
| `config set provider` | outro | Argumento inválido | N/A | Erro de provedor não suportado | `2` | AC-1 |
| `config set api-key` | `bitbucket` | Token no prompt | 200 OK | Credencial salva + "Conexão efetuada" (sem pedir email) | `0` | AC-2 |
| `config set api-key` | `bitbucket` | Token no prompt | 401/403 | Credencial preservada + "Conexão recusada" | `3` | AC-2 |
| `config set api-key` | `github` | Token no prompt | 200 OK | Credencial salva + "Conexão efetuada" | `0` | AC-3 |
| `config set api-key` | `github` | Token no prompt | 401/403 | Credencial preservada + "Conexão recusada" | `3` | AC-3 |
| `config set api-key` | Qualquer | Argumento via CLI | N/A | Erro de uso (requer prompt oculto) | `2` | AC-4 |
| `config set api-key` | Qualquer | String vazia no prompt | N/A | Erro de uso (chave não pode ser vazia) | `2` | AC-4 |

## Casos de borda e erros
- Tentativa de configurar api-key sem provedor configurado → erro com código `2` (`USAGE_ERROR`) solicitando configuração prévia do provedor.
- Falha no backend de keyring ao armazenar credencial → fallback para arquivo seguro de credenciais ou emissão de erro sem quebrar com traceback.

## Fora de escopo
- Alteração na estrutura de armazenamento de credenciais no keyring.
- Suporte a provedores Git adicionais além de GitHub e Bitbucket Cloud.

## Rastreabilidade
- Documentação Bitbucket Auth: https://developer.atlassian.com/cloud/bitbucket/rest/intro/#authentication
- Documentação GitHub REST: https://docs.github.com/en/rest?apiVersion=2026-03-10
- ADRs relacionados:
  - `docs/architecture/adr/0004-gestao-de-credenciais-e-seguranca.md`

