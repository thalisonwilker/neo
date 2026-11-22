---
name: spec
description: Contrato da feature 0040 — criar um Espaço pelo modal do painel (nome, tipo, meta semanal e agentes sugeridos), rota POST /v1/espacos e dashboard vazio do Espaço.
alwaysApply: true
---

# Spec — Criar Espaço

> **Fonte da verdade.** Status: aprovado (22/11/2026) · Tier: arquitetural
> Termos conforme [domain.md](domain.md) e `docs/glossary.md`. Erros da API no corpo `{erro, mensagem, campo?}` (pt-BR), como na 0037.

## Resumo
O Usuário cria um novo Espaço num modal — nome, tipo, Meta semanal e a opção de Agentes sugeridos — e cai no
dashboard vazio desse Espaço, na cor e com os indicadores do tipo.

## Perfil do tipo (vale para o modal, o menu lateral e o dashboard)

| Tipo | Rótulo | Cor | Ícone | Descrição no modal | Meta sugerida | 4º indicador (título · valor vazio · legenda) |
|---|---|---|---|---|---|---|
| `trabalho` | Trabalho | `#00FFB2` | pasta | Trabalho, carreira, clientes e outros projetos | 30 | Deploys no mês · `0` · neste mês |
| `estudos` | Estudos | `#38BDF8` | livro | Faculdade, cursos, leituras, provas e cronogramas | 10 | Sequência de estudo · `0 dias` · neste mês |
| `hobbies` | Hobbies | `#A78BFA` | brilho | Atividades de lazer | 8 | Sessões na semana · `0` · neste mês |
| `pessoal` | Pessoal | `#F472B6` | coração | Coisas da vida pessoal | 8 | Contas a pagar · `0` · neste mês |

## Critérios de aceite

### API

### AC-1: Criar um Espaço
- **Dado** um Usuário com Primeiro acesso concluído
- **Quando** chama `POST /v1/espacos` com `{"nome": "  Faculdade  ", "tipo": "estudos", "meta_semanal": 12, "agentes_sugeridos": true}`
- **Então** recebe 201 com `{id, nome: "Faculdade", tipo: "estudos", meta_semanal: 12, agentes_sugeridos: true, criado_em}`; o Espaço fica gravado e aparece por último em `espacos` no `GET /v1/me`

### AC-2: Meta e agentes omitidos
- **Dado** um Usuário com Primeiro acesso concluído
- **Quando** cria um Espaço só com `nome` e `tipo`
- **Então** o Espaço nasce com a Meta sugerida do tipo (tabela acima) e `agentes_sugeridos: false`

### AC-3: Dados inválidos
- **Dado** um Usuário com Primeiro acesso concluído
- **Quando** envia nome vazio, só com espaços ou com mais de 100 caracteres (após remover os espaços das pontas); tipo fora dos 4 valores; ou `meta_semanal` menor que 1, maior que 168 ou não inteira
- **Então** recebe 422 com `erro: "dados_invalidos"` e `campo` igual a `nome`, `tipo` ou `meta_semanal`; nada é gravado. Campos extras no corpo são ignorados.

### AC-4: Primeiro acesso pendente
- **Dado** um Usuário com Primeiro acesso pendente
- **Quando** chama `POST /v1/espacos`
- **Então** recebe 409 com `erro: "primeiro_acesso_pendente"` e nada é gravado (sem token, token inválido ou e-mail não liberado seguem o 401/403 da 0037)

### AC-5: Espaços existentes e resposta de `/v1/me`
- **Dado** Espaços criados antes desta feature
- **Quando** a migração roda e o Usuário chama `GET /v1/me`
- **Então** cada Espaço vem com `meta_semanal` igual à Meta sugerida do seu tipo e `agentes_sugeridos: false`; os demais campos não mudam

### AC-6: Primeiro acesso com o novo limite
- **Dado** um Usuário com Primeiro acesso pendente
- **Quando** conclui o Primeiro acesso com um nome de Espaço de 41 a 100 caracteres
- **Então** recebe 201 e o Espaço nasce com a Meta sugerida do tipo e `agentes_sugeridos: false`; acima de 100 caracteres recebe 422 `campo: "espaco.nome"` (o formulário do painel aceita até 100)

### Painel

### AC-7: Abrir o modal
- **Dado** o painel aberto
- **Quando** a pessoa clica no "+" ("Novo Espaço") do cartão Espaços da página inicial ou no item "Novo Espaço" do menu lateral
- **Então** abre o modal "Criar Espaço", com o texto "Escolha o tipo. Ele define o calendário, as tarefas, os agentes e as skills sugeridas.", o nome vazio com foco, o tipo Trabalho selecionado, a meta em 30 horas e a opção "Criar agentes e skills sugeridos para este tipo" desligada

### AC-8: Escolher o tipo
- **Dado** o modal aberto
- **Quando** a pessoa escolhe um dos 4 cartões de tipo (por clique ou teclado)
- **Então** só ele fica selecionado (borda e brilho na cor do tipo), cada cartão mostra ícone, rótulo e descrição da tabela, e a meta passa a ser a Meta sugerida desse tipo

### AC-9: Validar antes de enviar
- **Dado** o modal aberto
- **Quando** o nome está vazio (ou só espaços) ou a meta está fora de 1 a 168 ou não é inteira
- **Então** o botão "Criar Espaço" fica desabilitado e o campo mostra a mensagem do problema; o campo nome não aceita mais de 100 caracteres

### AC-10: Criar e abrir o dashboard
- **Dado** o modal preenchido e válido
- **Quando** a pessoa clica em "Criar Espaço"
- **Então** o painel chama `POST /v1/espacos` com nome, tipo, meta e a opção de agentes; enquanto espera, o botão fica desabilitado com "Criando…"; com 201, o modal fecha, o painel vai para `/dashboard/espacos/<id>` e o novo Espaço passa a aparecer no cartão Espaços da página inicial e no menu lateral

### AC-11: Erro ao criar
- **Dado** o modal preenchido
- **Quando** a API responde 422
- **Então** a mensagem aparece junto ao campo indicado e o modal continua aberto com os dados;
- **e quando** a API responde 5xx ou não responde, o modal mostra "Não foi possível criar o Espaço agora. Tente de novo." e mantém os dados

### AC-12: Cancelar
- **Dado** o modal aberto, com ou sem dados
- **Quando** a pessoa clica em "Cancelar", no "×" ou aperta Esc
- **Então** o modal fecha sem chamar a API; ao reabrir, volta ao estado inicial do AC-7

### AC-13: Dashboard vazio do Espaço
- **Dado** um Espaço "Novo Espaço de trabalho" do tipo `trabalho` com meta 30
- **Quando** a pessoa abre `/dashboard/espacos/<id>`
- **Então** vê o nome em destaque na cor do tipo, o subtítulo "Trabalho · visão geral do Espaço", e:
  - 4 indicadores: "Tarefas abertas" `0` · "0 concluídas"; "Horas na semana" `0h` · "meta de 30h"; "Projetos ativos" `0` · "nenhum ainda"; e o 4º indicador do tipo (tabela);
  - os números na cor do tipo;
  - 6 cartões vazios: "Em andamento e para hoje" ("Nenhuma tarefa em andamento."), "Horas por dia" ("0h na semana" e as 7 barras zeradas de dom. a sáb.), "Projetos" ("Nenhum projeto ainda."), "Agenda" ("Nenhum compromisso agendado."), "Sugestões do NEO" (três sugestões em texto: "Crie o primeiro projeto deste Espaço", "Conecte uma integração", "Peça ao NEO um plano para a semana") e "Hábitos" ("Os hábitos deste Espaço aparecem aqui.");
  - o título da página é "<nome do Espaço> | NEO" e a trilha do cabeçalho mostra o nome do Espaço

### AC-14: Espaço inexistente
- **Dado** um Usuário
- **Quando** abre `/dashboard/espacos/<id>` com um id que não é de um Espaço dele
- **Então** vê "Espaço não encontrado" com um link para o Início, sem dados de outro Usuário

### AC-15: Espaços no menu lateral
- **Dado** um Usuário com Espaços
- **Quando** olha o menu lateral
- **Então** vê o grupo "Espaços" com um atalho por Espaço, na ordem de criação, com o ícone e a cor do tipo e o nome cortado com reticências se for longo; o atalho do Espaço aberto fica destacado; o grupo termina com o item "Novo Espaço"

## Casos de borda e erros
- Dois Espaços com o mesmo nome → permitido; cada um tem seu id.
- Meta digitada como "12,5" ou texto → inválida (AC-9); a API recusa decimais (AC-3).
- Trocar o tipo depois de editar a meta → a meta volta para a Meta sugerida do novo tipo (AC-8).
- Clique duplo em "Criar Espaço" → um só pedido (botão desabilitado durante o envio).
- Sessão expira com o modal aberto → a API responde 401 e o painel segue a regra da 0037 (encerra a sessão).

## Fora de escopo
> Vinculante.
- Criar agentes ou skills de verdade (só a preferência é guardada).
- Tarefas, horas, projetos, agenda, hábitos, deploys e contas; ações "Fazer" das sugestões.
- Menu lateral próprio por tipo (Calendário, Tarefas, Reuniões, Projetos, Roadmap, Clientes…).
- Editar, arquivar ou apagar Espaço; alterar a meta depois de criado; limite de quantidade de Espaços.
- Mudar o formulário do Primeiro acesso além do limite de 100 caracteres.
- Cartão de usuário com plano e créditos e o botão flutuante de IA do protótipo.

## Rastreabilidade
- Product: [product.md](product.md) · Design: [design.md](design.md) · Domínio: [domain.md](domain.md)
- Depende de: [0037](../0037-api-fundacao-primeiro-acesso/spec.md), [0038](../0038-home-painel/spec.md), [0039](../0039-limpeza-template-painel/spec.md)
- ADRs: [ADR-0011](../../docs/architecture/adr/0011-api-fastapi-com-postgresql.md)
