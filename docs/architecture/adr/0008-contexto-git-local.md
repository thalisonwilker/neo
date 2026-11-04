---
name: adr-0008
description: Seleção persistente de repositório local para comandos Git do Neo.
alwaysApply: false
---

# ADR-0008 — Contexto Git por repositório local

**Status:** Aceito · **Data:** 2026-11-04

## Contexto

O usuário precisa selecionar um repositório uma vez e usá-lo em comandos subsequentes, mesmo fora de seu diretório. Tasks distintas devem permanecer associadas a cada repositório. Uma busca indiscriminada no sistema não é desejada.

## Decisão

Manter um registro local explícito de caminhos absolutos de repositórios conhecidos, a seleção atual e um ID de task por repositório. Com seleção presente, as operações Git locais e a detecção de `origin` usam esse caminho; sem seleção, preserva-se a detecção pelo diretório corrente. Selecionar uma branch executa checkout Git no repositório selecionado.

O fluxo de criação preserva recursos locais e remotos em falhas parciais. Credenciais permanecem no mecanismo de armazenamento existente, conforme [ADR-0004](0004-gestao-de-credenciais-e-seguranca.md), e a validação antecede a substituição da credencial armazenada.

## Consequências

O contexto persiste entre invocações sem mudar o diretório do terminal. Apenas repositórios explicitamente criados ou selecionados aparecem na listagem, e caminhos movidos precisam ser selecionados novamente. A preferência global por um repositório selecionado altera o comportamento de comandos executados dentro de outro repositório; opções explícitas continuam tendo precedência quando aplicáveis.
