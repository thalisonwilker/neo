---
name: domain
description: Modelo DDD da feature 0040 — Espaço ganha meta semanal e preferência de agentes sugeridos; regras de criação de Espaço no contexto Identidade.
alwaysApply: false
---

# Domain Model (DDD) — Criar Espaço

> **Status:** aprovado (22/11/2026). Estende o modelo da [0037](../0037-api-fundacao-primeiro-acesso/domain.md).
> Termos iguais no código (`domain/identidade/`).

## Bounded Context
**Identidade** (o mesmo da 0037). Criar um Espaço é mudar o agregado `Usuario`; não nasce contexto novo.

## Linguagem ubíqua (termos novos ou alterados)

| Termo | Definição | NÃO confundir com |
|---|---|---|
| **Espaço** | Agrupador da vida do Usuário no painel, de um Tipo de espaço, com nome, Meta semanal e a preferência de Agentes sugeridos | **Workspace** (escopo de repositórios no provedor Git) |
| **Meta semanal** | Quantas horas por semana o Usuário quer dedicar a um Espaço; número inteiro de 1 a 168 | Horas lançadas (ainda não existem) |
| **Meta sugerida** | Meta semanal proposta pelo Tipo de espaço: trabalho 30 h, estudos 10 h, hobbies 8 h, pessoal 8 h | Meta semanal escolhida |
| **Agentes sugeridos** | Preferência do Espaço: quer (ou não) que o Neo crie os agentes e skills sugeridos para o tipo. Nesta feature só é guardada | Agente de Codificação (CLI) · agentes já criados |
| **Perfil do tipo** | O que vem do Tipo de espaço: rótulo, cor, ícone, descrição, Meta sugerida e o 4º indicador do dashboard | Dados do Espaço |

## Agregados, entidades e value objects
- **Agregado `Usuario`** (raiz: `Usuario`)
  - Entidade `Espaco`: ganha `meta_semanal: MetaSemanal` e `agentes_sugeridos: bool`.
  - Value objects:
    - `NomeDoEspaco`: **1 a 100** caracteres após remover espaços nas pontas (era 1 a 40).
    - `MetaSemanal` (novo): inteiro de 1 a 168.
    - `TipoEspaco`: ganha `meta_sugerida` (30, 10, 8, 8).
  - **Invariantes** (somam-se às 5 da 0037):
    6. Só cria Espaço quem já concluiu o Primeiro acesso.
    7. Todo Espaço tem Meta semanal válida; se ela não for informada, vale a Meta sugerida do tipo.
    8. O Espaço do Primeiro acesso nasce com a Meta sugerida do tipo e sem Agentes sugeridos.
  - Comportamento novo: `Usuario.criar_espaco(nome, tipo, meta_semanal, agentes_sugeridos, agora)` → `Espaco`.
  - Nomes repetidos entre Espaços do mesmo Usuário são permitidos (não há regra de unicidade).

## Eventos de domínio

| Evento | Disparado quando | Quem reage |
|---|---|---|
| `EspacoCriado` | Usuário cria um Espaço fora do Primeiro acesso | log (sem barramento, como na 0037) |

## Relações com outros contextos
- **Identidade → Painel Web:** Open Host Service pela API v1; nova rota `POST /v1/espacos`; `GET /v1/me` passa a devolver `meta_semanal` e `agentes_sugeridos` em cada Espaço.
- **Identidade → (futuro) Agentes:** a preferência `agentes_sugeridos` é lida por uma feature futura de agentes. Sem integração agora.
- **Identidade × Git Integration:** continua sem relação. **Espaço ≠ Workspace.**
