---
name: adr-0006
description: Decisão sobre UX no terminal, formatação visual e observabilidade de erros.
alwaysApply: false
---

# ADR-0006: Observabilidade e UX Visual no Terminal

- **Status:** aceito
- **Data:** 2026-10-27
- **Decisores:** Time do Projeto Neo

## Contexto
A experiência de uso do Neo precisa ser elegante, clara e não intimidadora. Falhas de conexão, tokens inválidos ou comandos com saída bruta em JSON podem prejudicar a ergonomia diária. Por outro lado, scripts de automação Unix (como pipes com `jq`) exigem saída limpa e estruturada.

## Decisão
1. **Modo Humano (Padrão):**
   - Respostas renderizadas com Rich: tabelas com cabeçalhos nítidos, cards com bordas arredondadas e badges de status coloridos.
   - Operações assíncronas ou de rede exibem spinners informativos (`rich.status`).
2. **Modo Máquina (Automação):**
   - Todo comando suportará a flag universal `--json`. Quando ativada, a saída no stdout será estritamente JSON válido sem cabeçalhos ou cores, enviando mensagens de progresso para o stderr.
3. **Tratamento de Erros:**
   - Erros comuns (como 401 Unauthorized, recurso não encontrado 404, falha de rede) serão interceptados e renderizados como mensagens amigáveis de instrução (ex: "Token expirado. Execute `neo config auth shortcut` para atualizar").
   - Tracebacks completos de exceção só serão impressos quando o usuário passar explicitamente a flag `--verbose` ou `--debug`.

## Consequências
- **+** Experiência de uso premium no terminal com máxima legibilidade e clareza.
- **+** Total compatibilidade com pipes Unix e ferramentas como `jq` e `fzf`.
- **−** Necessidade de implementar dupla rota de formatação (Rich vs JSON) nos controladores de comando.
