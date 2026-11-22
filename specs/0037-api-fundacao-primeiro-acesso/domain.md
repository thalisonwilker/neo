---
name: domain
description: Modelo DDD da feature 0037 — contexto Identidade (Usuário, Espaço, Lista de permissão, Primeiro acesso).
alwaysApply: false
---

# Domain Model (DDD) — Fundação da API e primeiro acesso

> **Status:** aprovado (22/11/2026). Termos aqui aparecem iguais no código (`domain/identidade/`).

## Bounded Context
**Identidade** — subdomínio **supporting**. Sabe *quem* é o Usuário do Neo, se ele pode entrar e como organiza a vida em Espaços. A prova de identidade (senha, Google, link mágico) é **generic** e fica no Clerk.

## Linguagem ubíqua

| Termo | Definição | NÃO confundir com |
|---|---|---|
| **Usuário** | Pessoa registrada no Neo, ligada a uma única identidade do Clerk | Conta do Clerk (pode existir sem Usuário) · Account financeira |
| **Identidade externa** | Identificador do Clerk (`clerk_user_id`) que o Usuário referencia | Token de sessão |
| **E-mail autorizado** | E-mail presente na Lista de permissão | Qualquer e-mail cadastrado no Clerk |
| **Lista de permissão** | Conjunto de E-mails autorizados a virar Usuário; editada por `neo api permitir` | Lista de permissão do Clerk (configuração manual externa, complementar) |
| **Primeiro acesso** | Etapa única em que o Usuário informa o Nome de exibição e cria o primeiro Espaço | Primeiro login no Clerk |
| **Nome de exibição** | Como o Neo chama o Usuário nas telas | E-mail ou nome no Clerk |
| **Espaço** | Agrupador da vida do Usuário no painel, de um Tipo de espaço | **Workspace** (escopo de repositórios no provedor Git) |
| **Tipo de espaço** | Um de 4 valores fixos: `trabalho`, `estudos`, `hobbies`, `pessoal` | Categoria financeira |
| **Boas-vindas** | Tela mostrada uma vez, logo após concluir o Primeiro acesso | Tela inicial do painel |

## Agregados, entidades e value objects
- **Agregado `Usuario`** (raiz: `Usuario`)
  - Entidades: `Espaco`
  - Value objects: `Email` (normalizado em minúsculas, formato válido), `NomeDeExibicao` (1 a 60 caracteres, sem espaços nas pontas), `NomeDoEspaco` (1 a 40 caracteres), `TipoEspaco` (enum dos 4 valores), `IdentidadeExterna`
  - **Invariantes:**
    1. Um Usuário só nasce se o `Email` estiver na Lista de permissão.
    2. Uma `IdentidadeExterna` corresponde a no máximo um Usuário.
    3. O Primeiro acesso é concluído **uma única vez**; concluir de novo é erro.
    4. Concluir o Primeiro acesso exige Nome de exibição **e** cria exatamente um Espaço.
    5. Com o Primeiro acesso concluído, o Usuário tem pelo menos um Espaço.
  - Fronteira de consistência: atualizar o Usuário e criar o primeiro Espaço na **mesma transação**.
- **Agregado `ListaDePermissao`** (raiz: `EmailAutorizado`)
  - Invariante: um e-mail aparece uma vez (comparação sem diferenciar maiúsculas).
  - Remover um e-mail **não** apaga nem bloqueia Usuários existentes; só impede novos (aprovado em 22/11/2026).

## Eventos de domínio
| Evento | Disparado quando | Quem reage |
|---|---|---|
| `UsuarioRegistrado` | Usuário criado no primeiro pedido autorizado | log de auditoria |
| `AcessoRecusado` | identidade válida com e-mail fora da Lista de permissão | log e contagem de recusas |
| `PrimeiroAcessoConcluido` | Nome de exibição definido e primeiro Espaço criado | painel exibe Boas-vindas |

> Nesta feature os eventos são só registros em log; não há barramento.

## Relações com outros contextos
- **Clerk (SaaS) → Identidade:** **Anti-Corruption Layer**. A porta `VerificadorDeToken` traduz o token e os dados do Clerk em `IdentidadeExterna` e `Email`; o domínio não conhece o Clerk.
- **Identidade → Painel Web (Acesso):** **Open Host Service** pela API v1 (`/v1/me`, `/v1/primeiro-acesso`).
- **Identidade × Git Integration:** sem relação. **Espaço ≠ Workspace.** Uma ligação futura (Espaço com repositórios) terá decisão própria.
- **CLI & Commands → Identidade:** o comando `neo api permitir` usa o caso de uso da Lista de permissão (mesma camada `application`).
