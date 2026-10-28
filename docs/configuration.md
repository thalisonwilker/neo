---
name: configuration
description: Guia detalhado de configuração de credenciais, provedores Git e segurança no Neo.
alwaysApply: false
---

# Configuração & Credenciais

O Neo adota princípios de **Segurança por Padrão** (*Security by Default*). Suas credenciais e preferências de trabalho nunca ficam desprotegidas no disco.

---

## Modelo de Precedência de Credenciais

Ao buscar um token de API para qualquer serviço (`bitbucket`, `github` ou `shortcut`), o Neo consulta as seguintes fontes em ordem estrita de prioridade:

```mermaid
graph TD
    A["Chamada de API"] --> B{"1. Variável de Ambiente?"}
    B -- "Sim" --> C["Utiliza Token da Env Var"]
    B -- "Não" --> D{"2. Keyring Seguro do SO?"}
    D -- "Sim" --> E["Recupera Segredo do Keyring"]
    D -- "Não" --> F{"3. Arquivo ~/.config/neo/credentials.toml?"}
    F -- "Sim" --> G["Recupera Segredo do Arquivo 0600"]
    F -- "Não" --> H["Erro: Credenciais Não Encontradas"]
```

1. **Variáveis de Ambiente:**
   - `BITBUCKET_TOKEN`
   - `GITHUB_TOKEN`
   - `SHORTCUT_TOKEN`
2. **Keyring Seguro do Sistema Operacional:**
   - macOS: *Keychain Access*
   - Linux: *Secret Service API / Freedesktop*
   - Windows: *Windows Credential Locker*
3. **Arquivo Local Criptografado/Protegido:**
   - Localização: `~/.config/neo/credentials.toml`
   - Permissão estrita: `0600` (leitura e escrita apenas pelo proprietário).

---

## Comandos de Gerenciamento

Cada categoria de serviço configura as próprias credenciais: **`neo git config`** (Bitbucket/GitHub) e **`neo tasks config`** (Shortcut). O `neo config` serve apenas como visão geral.

### Visualizar Status das Integrações (`neo config`)
```bash
neo config show
```

### Credenciais Git (`neo git config auth`)
=== "Interativo (Oculto)"
    ```bash
    neo git config auth set github
    # O terminal solicitará o token com digitação oculta
    ```

=== "Via Flag Direta"
    ```bash
    neo git config auth set github --token "ghp_meu_token"
    ```

=== "Consultar Token Mascarado"
    ```bash
    neo git config auth get github
    ```

=== "Remover Credencial"
    ```bash
    neo git config auth delete bitbucket
    ```

### Credenciais de Tasks (`neo tasks config`)
=== "Interativo (Oculto)"
    ```bash
    neo tasks config set
    ```

=== "Via Flag Direta"
    ```bash
    neo tasks config set --service shortcut --token "seu_token"
    ```

=== "Consultar Token Mascarado"
    ```bash
    neo tasks config get
    ```

=== "Remover Credencial"
    ```bash
    neo tasks config delete
    ```

=== "Mapear Colunas do Board"
    ```bash
    # Assistente interativo (busca colunas na API do serviço)
    neo tasks config columns

    # Ou diretamente via flags (suporta múltiplas colunas separadas por vírgula)
    neo tasks config columns \
      --todo "📝 - Backlog de Sprint, 🚨 - Bug" \
      --doing "🚧 - Em Progresso" \
      --done "✅ - Finalizado"
    ```

!!! warning "Mudança de comandos"
    Os comandos antigos (`neo config auth`, `neo repo`, `neo workspace`, `neo commits`, `neo story`) foram removidos. Use `neo git ...` e `neo tasks ...`.

---

## Configuração das Colunas do Board (`A fazer`, `Fazendo`, `Feito`)

Para organizar o quadro do comando `neo tasks resume`, o Neo armazena quais colunas (estados do workflow) do serviço correspondem às três etapas do quadro:

- **A fazer (`todo_columns`)**: ex.: `📝 - Backlog de Sprint`, `🚨 - Bug`
- **Fazendo (`doing_columns`)**: ex.: `🚧 - Em Progresso`
- **Feito (`done_columns`)**: ex.: `✅ - Finalizado`

Se você executar `neo tasks resume` e as colunas ainda não estiverem configuradas para o serviço ativo, o próprio comando consultará a API do serviço e abrirá o assistente interativo automaticamente, gravando a escolha em `~/.config/neo/config.toml`:

```toml
[shortcut]
todo_columns = ["📝 - Backlog de Sprint", "🚨 - Bug"]
doing_columns = ["🚧 - Em Progresso"]
done_columns = ["✅ - Finalizado"]
```

---

## Configuração do Provedor Git Padrão

Se você trabalha simultaneamente com repositórios no **GitHub** e no **Bitbucket**, pode definir qual deles é o padrão global quando uma flag explícita não for fornecida:

```bash
# Definir GitHub como padrão
neo git config set-provider github

# Definir Bitbucket como padrão
neo git config set-provider bitbucket

# Consultar provedor padrão atual
neo git config get-provider
```

Essa configuração é salva no arquivo `~/.config/neo/config.toml`.
