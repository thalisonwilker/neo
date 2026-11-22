---
name: design
description: Design técnico da feature 0040 — rota POST /v1/espacos, migração do Espaço (meta semanal e agentes sugeridos), modal Criar Espaço e dashboard do Espaço no painel.
alwaysApply: false
---

# Technical Design Doc — Criar Espaço

> **Tier:** arquitetural · **Status:** aprovado (22/11/2026)
> **Autor:** Claude · **Revisores:** Thalyson · **Data:** 2026-11-22

## Links e artefatos

| Artefato | Onde | Link |
|---|---|---|
| Spec · Product · Domínio | repositório | `./spec.md` · `./product.md` · `./domain.md` |
| Referência visual | repositório | `neo-command-center.html` (modal "Criar workspace", dashboard do workspace) |

## Contexto da funcionalidade
A 0037 criou a API (FastAPI + PostgreSQL) com o agregado `Usuario` e o primeiro Espaço. A 0038 mostra os
Espaços na página inicial e a 0039 deixou o painel só com o Neo. Falta criar outros Espaços.

## Goals / Non-goals
Ver [product.md](product.md).

## Design proposto

### API (`interfaces/api/`)
- **`POST /v1/espacos`** (autenticado, mesmo `Depends` da 0037)
  - Corpo: `{"nome": str, "tipo": "trabalho|estudos|hobbies|pessoal", "meta_semanal": int, "agentes_sugeridos": bool}`; `meta_semanal` opcional (usa a Meta sugerida); `agentes_sugeridos` opcional (padrão `false`); campos extras ignorados.
  - 201 → `EspacoResponse` do Espaço criado.
  - 422 `dados_invalidos` com `campo` (`nome`, `tipo`, `meta_semanal`); 409 `primeiro_acesso_pendente`; 401/403 como na 0037.
- **`EspacoResponse`** ganha `meta_semanal: int` e `agentes_sugeridos: bool` (aditivo; `GET /v1/me` e `POST /v1/primeiro-acesso` passam a devolvê-los).

### Aplicação (`application/identidade/`)
- Caso de uso **`CriarEspaco`**: obtém o Usuário (como `ObterOuCriarUsuario`), valida os value objects, chama `Usuario.criar_espaco` e persiste com `RepositorioDeUsuarios.adicionar_espaco(usuario_id, espaco)`. Registra `EspacoCriado` em log.
- `ConcluirPrimeiroAcesso` passa a criar o Espaço com a Meta sugerida e `agentes_sugeridos=false` (invariante 8).

### Persistência (`infrastructure/db/`)
- Migração Alembic **`0002_espaco_meta_e_agentes`**:
  - `espacos.nome` → `VARCHAR(100)` (era 40);
  - nova coluna `meta_semanal SMALLINT NOT NULL` com `CHECK (meta_semanal BETWEEN 1 AND 168)`, preenchida nos Espaços existentes pela Meta sugerida do tipo;
  - nova coluna `agentes_sugeridos BOOLEAN NOT NULL DEFAULT false`;
  - `downgrade` remove as colunas e volta o nome a 40 (falha de forma explícita se houver nome maior que 40).
- Repositório: `adicionar_espaco` insere o Espaço numa transação.

### Painel (`web/`)
- **Perfil do tipo** num único lugar (`features/espacos/perfis.ts`), substituindo o de `features/home/home-rules.ts`: rótulo, cor, ícone, descrição, Meta sugerida e o 4º indicador.
- **Modal "Criar Espaço"** (`Dialog` de `components/ui`): abre pelo "+" do cartão Espaços da página inicial e pelo item "Novo Espaço" do menu lateral.
- Cliente `criarEspaco()` em `lib/api/` (mesmo padrão de `fetchMe`), com token do Clerk.
- Depois de criar: recarrega o Usuário (`recarregar()` do `NeoAccessGuard`) e navega para **`/dashboard/espacos/<id>`**.
- **Dashboard do Espaço** (`app/dashboard/espacos/[id]/page.tsx`): lê o Espaço do contexto do Usuário (já carregado por `GET /v1/me`); sem rota nova de leitura na API.
- **Menu lateral:** grupo "Espaços" com um atalho por Espaço (ícone e cor do tipo) e o item "Novo Espaço".

## Cobertura dos 5 eixos

### 1. Tech stack
Sem impacto: FastAPI, SQLAlchemy/Alembic, Next.js e os componentes base já existentes.

### 2. Arquitetura base
Mantém a regra de camadas. O domínio ganha `MetaSemanal` e `criar_espaco`; nenhuma camada nova. Contrato da API muda de forma **aditiva** (campos novos na resposta, rota nova).

### 3. Infra
Uma migração de banco. Reversível pelo `downgrade` (com a ressalva do nome > 40).

### 4. Qualidade
Testes por camada como na 0037 (domínio, casos de uso com repositório em memória, integração com Postgres, e2e da API) e Vitest no painel; um teste por AC.

### 5. Observabilidade
Log `EspacoCriado` com `usuario_id`, `espaco_id` e `tipo` — nunca o nome do Espaço nem o e-mail. Contagem de 422 por campo no log de pedido já existente.

## Alternativas consideradas
- **Rota `GET /v1/espacos/{id}` para o dashboard** — descartada: o painel já tem todos os Espaços em `/v1/me`; uma rota a mais sem ganho.
- **Guardar cor e 4º indicador no Espaço** — descartada: são do tipo; guardar duplicaria e travaria mudanças de visual.
- **Meta em minutos ou decimal** — descartada por ora: horas inteiras bastam para uma meta semanal.

## ADR
Sem ADR novo: estende o [ADR-0011](../../docs/architecture/adr/0011-api-fastapi-com-postgresql.md) (API + PostgreSQL) sem decisão estrutural nova; a migração é reversível.

## Mapa de dependências
- `GET /v1/me` e `NeoAccessGuard` (0037) · página inicial e cartão Espaços (0038) · menu lateral (0039) · Clerk (token).

## Riscos
- Mudar o limite do nome afeta o Primeiro acesso: o formulário e a spec da 0037 passam a dizer 100.
- `recarregar()` do guard mostra "Verificando acesso…" por um instante; aceitável nesta feature.
