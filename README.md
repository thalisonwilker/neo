# Neo — Personal Command Assistant

> **Compreenda seus sistemas. Seja dono das suas escolhas.**

**Neo** é um assistente pessoal extensível, executado pela linha de comando, desenvolvido em **Python com Typer**. Seu objetivo é reduzir tarefas manuais, organizar informações e ajudar o usuário a tomar decisões com mais contexto e autonomia.

Inspirado filosoficamente no personagem Neo, de *Matrix*, o projeto parte de três princípios: **compreender antes de executar**, **preservar as escolhas do usuário** e **evoluir por meio de módulos independentes**.

---

## 🧭 Esteira Spec-Driven Development (SDD)
O desenvolvimento do Neo segue rigorosamente **Spec-Driven Development (SDD)**, combinando **Lean Inception**, **DDD** e **Technical Design Docs**.
- **Mapa Geral do Projeto:** [docs/README.md](docs/README.md)
- **Estado de Trabalho Vivo:** [docs/STATE.md](docs/STATE.md)
- **Roadmap (Now / Next / Later):** [docs/product/roadmap.md](docs/product/roadmap.md)
- **Convenções e Instruções para Agentes:** [AGENTS.md](AGENTS.md)
- **Quality Gates e DoD:** [docs/engineering/TESTING.md](docs/engineering/TESTING.md)

---

## Objetivos

- Automatizar tarefas repetitivas do trabalho e da vida pessoal.
- Centralizar operações de diferentes serviços em uma única CLI.
- Investigar dados, relacionar informações e apoiar decisões.
- Permitir integrações e novas funcionalidades sem acoplar os módulos.
- Incorporar, futuramente, agentes de IA e comandos em linguagem natural.

## MVP — Desenvolvimento e trabalho

### Bitbucket
- Criar, pesquisar, listar e clonar repositórios.
- Consultar commits, branches e pull requests.
- Analisar histórico de alterações e apoiar a investigação de bugs.

### Shortcut (`app.shortcut.com`)
- Pesquisar, listar e consultar stories/cards.
- Acompanhar demandas e bugs.
- Analisar descrições, histórico e contexto de chamados.
- Relacionar demandas a repositórios, commits e pull requests.

### Exemplos de comandos propostos

```bash
# Repositórios (Bitbucket)
neo repo list
neo repo create meu-projeto
neo repo clone meu-projeto
neo commits search --author usuario

# Demandas & Stories (Shortcut)
neo story list --mine
neo story show 1234
neo story analyze 1234

# Investigação Cruzada (Shortcut + Bitbucket)
neo bug investigate 5678
```

## Evolução futura

| Módulo | Possibilidades |
| --- | --- |
| `work` | Planejamento de atividades e acompanhamento de demandas |
| `study` | Planos de estudo, cursos e revisões |
| `fitness` | Treinos, metas e acompanhamento de progresso |
| `cycling` | Pedais, rotas e histórico de atividades |
| `fishing` | Marés, planejamento e registros de pescarias |
| `agenda` | Compromissos, prioridades e organização semanal |
| `ask` | Assistente de IA para consultas e automações em linguagem natural |

Exemplo futuro:
```bash
neo ask "Organize minha semana considerando trabalho, estudos e treinos"
```

## Arquitetura proposta

- **CLI:** Python 3.13 + Typer + Rich.
- **Integrações:** Clientes isolados para APIs do Bitbucket, Shortcut e futuros serviços com Anti-Corruption Layer (ACL).
- **Módulos:** Comandos por domínio (`repo`, `commits`, `story`, `bug`, etc.).
- **Configuração:** Perfis, tokens e preferências por ambiente com armazenamento seguro via **Keyring do SO**.
- **Camada de IA (futura):** Interface intercambiável para modelos locais (Ollama) ou serviços externos.
- **Segurança:** Operações destrutivas ou de alteração relevante exigem confirmação explícita.

Estrutura inicial do código:

```text
neo/
├── pyproject.toml
├── README.md
├── AGENTS.md
├── docs/                      # Documentação viva e esteira SDD
└── src/
    └── neo/
        ├── cli.py
        ├── config.py
        ├── commands/
        │   ├── repo.py
        │   ├── commits.py
        │   └── story.py
        ├── integrations/
        │   ├── bitbucket.py
        │   └── shortcut.py
        └── services/
            └── analysis.py
```

## Roadmap

1. **Fundação:** Estrutura Python, Typer, Rich, configuração, autenticação Keyring e testes.
2. **Bitbucket:** Listar, pesquisar, criar e clonar repositórios; consultar commits.
3. **Shortcut:** Listar demandas, analisar stories e investigar bugs.
4. **Análise cruzada:** Relacionar cards, branches, commits e pull requests.
5. **Extensibilidade:** Ampliar para estudos, treinos, pedal, pesca e agenda.
6. **IA:** Consultas em linguagem natural e automações com aprovação do usuário.

**Neo não deve tomar o controle da vida do usuário: deve devolver tempo, clareza e autonomia a ele.**
