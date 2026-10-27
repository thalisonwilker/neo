---
name: stakeholders
description: Mapa de stakeholders — quem influencia ou é impactado pelo Neo.
alwaysApply: false
---

# Mapa de Stakeholders — Neo

> Quem tem **interesse** ou **influência** no produto (Lean Inception). Define quem engajar de perto vs manter informado.

## Stakeholders

| Stakeholder | Papel | Interesse (o que quer) | Influência | Como engajar |
|---|---|---|---|---|
| **Usuário Principal (Desenvolvedor)** | Usuário final & Criador | Agilidade, autonomia, comandos ergonômicos e zero atrito | Alta | Feedback contínuo a cada ciclo de comandos implementados |
| **Equipe de Desenvolvimento / Squad** | Beneficiários indiretos | Padronização de referências de stories em commits e PRs | Média | Compartilhamento da CLI e documentação das convenções |
| **Administradores de Segurança / Infra** | Guardiões de conformidade | Garantir que tokens e credenciais não vazem ou fiquem expostos | Alta | Validação do uso de Keyring e permissões de arquivos restritas |

## Matriz interesse × influência

```
Influência ▲
     alta │  Administradores de Segurança  │  Usuário Principal (Criador/Dev)
          │────────────────────────────────┼─────────────────────────────────
    baixa │  Comunidade Open Source        │  Equipe de Squad / Colegas
          └────────────────────────────────┴─────────────────────────────────►
                 baixo                   Interesse                  alto
```

## Personas-chave (resumo)
- **Desenvolvedor Focado:** Quer listar demandas atribuídas a si (`neo story list --mine`) e clonar ou abrir branch sem abrir o navegador.
- **Investigador de Bugs:** Quer rodar `neo bug investigate <id>` e receber em segundos o contexto da story, commits relacionados e arquivos modificados.
