---
name: cli-agent-run
description: Manual do comando neo agent run para execução interativa do Antigravity CLI com overrides locais.
alwaysApply: false
---

# neo agent run
> Inicia uma sessão interativa do agente no diretório escolhido com overrides locais.

O comando `neo agent run` inicia uma sessão interativa com o executável oficial do Google Antigravity CLI (`agy`), repassando as configurações do projeto e permitindo aplicar *overrides* temporários de modelo ou provedor SDD para a sessão atual.

---

## Sintaxe

```bash
neo agent run [--opções]
```

---

## Ações

| Ação | Descrição | Exemplo de comando |
|---|---|---|
| *(padrão)* | Inicia o executável do agente no terminal interativo | `neo agent run` |

---

## Opções

As opções abaixo são específicas de `neo agent run`. Para opções globais, consulte os [conceitos gerais](../index.md#opcoes-globais-vs-opcoes-de-recurso).

| Opção | Obrigatório | Padrão | Descrição |
|---|---|---|---|
| `--agent` | Não | *(config)* | Adaptador do agente apenas para esta execução (`antigravity`). |
| `--command` | Não | *(config)* | Executável do agente para esta execução (ex.: `agy`). |
| `--model` | Não | *(config)* | Identificador do modelo repassado ao agente (ex.: `Gemini 3.8 Pro`). |
| `--sdd-provider` | Não | *(config)* | Provedor SDD para esta sessão (`spec-driven` ou `spec-kit`). |
| `--dir` | Não | `.` | Diretório de trabalho onde a sessão do agente será iniciada. |

---

## Exemplos

### 1. Iniciar sessão padrão no diretório atual
```bash
neo agent run
```

### 2. Iniciar com modelo mais potente para tarefa complexa
```bash
neo agent run --model "Gemini 3.8 Pro"
```

### 3. Iniciar em outro diretório de projeto
```bash
neo agent run --dir ~/projetos/core-api
```

---

## Erros comuns e códigos de saída

* **Código 1 (Erro genérico):** O binário do agente (`agy`) não foi encontrado no `PATH` ou a sessão encerrou com erro no processo filho.
* **Código 2 (Uso incorreto):** Parâmetros de comando inválidos ou caminho de diretório inexistente.

---

## Veja também
- [neo agent status](status.md) — Diagnosticar se o executável `agy` está no `PATH`
- [neo config agent](config.md) — Definir o modelo padrão em `config.toml`
- [neo agent setup](setup.md) — Preparar as skills do projeto antes de rodar o agente

