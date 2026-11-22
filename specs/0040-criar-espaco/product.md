---
name: product
description: Por quê e para quem da feature 0040 — criar um novo Espaço pelo painel e abrir o seu dashboard vazio.
alwaysApply: false
---

# Product — Criar Espaço

> **Tier:** arquitetural · **Status:** aprovado (22/11/2026) · **Dono:** Thalyson
> Referência: jornada "criação de um novo workspace" (22/11/2026) e protótipo `neo-command-center.html`
> (modal "Criar workspace" e dashboard do workspace). No Neo o termo é **Espaço** (glossário).

## Problema
Hoje o Usuário só tem o Espaço criado no Primeiro acesso. A vida dele tem várias frentes (trabalho,
estudos, hobbies, vida pessoal) e o painel não deixa separar cada uma num Espaço próprio, com o tempo que
ele quer dedicar a ela.

## Para quem
O Usuário do painel do Neo (hoje, o mantenedor), já com Primeiro acesso concluído.

## Resultado esperado / métrica de sucesso
- O Usuário cria um Espaço em menos de 30 segundos, sem sair da página onde está.
- Cada Espaço guarda o tipo, a meta semanal de horas e se quer agentes e skills sugeridos — dados que as
  próximas features (tarefas, horas, agentes) vão ler.
- Depois de criar, o Usuário cai no dashboard do Espaço, na cor e com os indicadores do tipo.

## Goals
- Modal "Criar Espaço" aberto pelo botão "+" do cartão Espaços na página inicial e pelo item "Novo Espaço" do menu lateral.
- Campos: nome (até 100 caracteres), tipo (4 cartões com cor, ícone e descrição), meta semanal em horas
  (sugerida pelo tipo) e a opção "Criar agentes e skills sugeridos para este tipo".
- API para criar o Espaço e banco guardando os novos dados.
- Dashboard vazio do Espaço: nome na cor do tipo, 4 indicadores do tipo e os cartões vazios.
- Os Espaços aparecem no menu lateral, como atalho para o dashboard de cada um.

## Non-goals
- Criar de fato agentes ou skills (só a preferência é guardada).
- Tarefas, horas lançadas, projetos, agenda, hábitos, deploys e sugestões funcionais (os cartões ficam vazios).
- Menu lateral próprio por tipo (Calendário, Projetos, Clientes…).
- Editar, arquivar ou apagar um Espaço; mudar a meta depois de criado.
- Mudar o formulário do Primeiro acesso (ele segue sem meta e sem a opção de agentes).

## Riscos / premissas
- Premissa: os 4 tipos continuam fixos; a cor, o ícone, a descrição, a meta sugerida e o 4º indicador
  são do tipo, não do Espaço.
- Risco: o limite do nome muda de 40 para 100 caracteres, uma regra do domínio da 0037 — vale também para
  o Primeiro acesso (atualização consciente da spec 0037).
- Risco: Espaços já criados não têm meta; a migração preenche com a meta sugerida do tipo.
