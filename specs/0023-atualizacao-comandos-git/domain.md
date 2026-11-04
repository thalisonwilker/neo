---
name: domain
description: Modelo do contexto Git selecionado e das credenciais na feature 0023.
alwaysApply: false
---

# Domain Model — Atualização dos comandos Git

## Bounded Context

`Git Integration` mantém o repositório local selecionado e a task associada; `Configuration & Secrets` mantém as credenciais por provedor. Não há nova fronteira de domínio.

## Linguagem ubíqua

| Termo | Definição | Não confundir com |
|---|---|---|
| Repositório local | Diretório que contém um repositório Git conhecido pelo Neo. | Workspace remoto |
| Repositório selecionado | Repositório local usado como contexto persistente dos comandos Git. | Diretório corrente do terminal |
| Task | ID de uma tarefa associado a um repositório local. | Branch ou commit |
| Branch | Linha de desenvolvimento local do repositório selecionado. | Pull request |
| API Token / Personal Access Token | Credencial de um provedor; a interface a chama de `api-key`. | Chave SSH |

## Estado e invariantes

- O registro de repositórios contém caminhos absolutos únicos, seleção opcional e um ID de task opcional por caminho.
- A seleção exige repositório Git local válido; um caminho inválido não muda a seleção.
- A seleção de branch faz checkout no repositório selecionado; a branch ativa não pode ser excluída.
- Uma credencial submetida só substitui a armazenada depois da validação no provedor configurado.

## Relações com outros contextos

`Git Integration` usa `Configuration & Secrets` para autenticação e integra Git local e APIs do provedor. A task é referenciada por ID, sem alterar o contexto `Shortcut Integration`. Nenhum evento de domínio persistido é introduzido.
