"""Guarda-chuva dos comandos Git (`neo git`): `config`, `auth`, `workspace`, `repo`, `commits` e `status`."""

from __future__ import annotations

import subprocess
from typing import NoReturn

import typer
from keyring.errors import KeyringError
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.commits import commits_app
from neo.commands.repo import repo_app
from neo.commands.workspace import workspace_app
from neo.config import (
    SUPPORTED_GIT_CONFIG_KEYS,
    SUPPORTED_GIT_PROVIDERS,
    SUPPORTED_TASK_SERVICES,
    ExitCode,
    GitProviderType,
    delete_credential,
    get_bitbucket_email,
    get_credential_source,
    get_git_config_value,
    list_git_config_values,
    set_credential,
    set_git_config_value,
    unset_git_config_value,
    validate_git_config_key,
    validate_git_provider,
)
from neo.integrations.resolver import (
    detect_git_remote_details,
    resolve_git_provider_and_source,
    resolve_git_workspace_and_source,
)
from neo.output import console, print_error, print_json, print_panel, print_success, print_table

git_app = typer.Typer(
    name="git",
    help="Comandos Git unificados para GitHub e Bitbucket Cloud (config, auth, workspace, repo, commits, status).",
    no_args_is_help=True,
)

git_config_app = typer.Typer(
    name="config",
    help="Gerencia preferências do módulo Git na seção [git] de config.toml (set, get, list, unset).",
    no_args_is_help=True,
)

git_auth_app = typer.Typer(
    name="auth",
    help="Gerencia autenticação segura dos provedores Git (login, status, logout).",
    no_args_is_help=True,
)

git_app.add_typer(git_config_app, name="config")
git_app.add_typer(git_auth_app, name="auth")
git_app.add_typer(workspace_app, name="workspace")
git_app.add_typer(repo_app, name="repo")
git_app.add_typer(commits_app, name="commits")


def _fail_usage(message: str, as_json: bool) -> NoReturn:
    print_error(message, as_json=as_json, code=int(ExitCode.USAGE_ERROR))
    raise typer.Exit(code=int(ExitCode.USAGE_ERROR))


def _validate_provider_option(
    ctx: typer.Context, provider: str, json_flag: bool = False
) -> GitProviderType:
    as_json = is_json_mode(ctx, json_flag)
    if provider.strip().lower() in SUPPORTED_TASK_SERVICES:
        _fail_usage(
            f"'{provider}' é um serviço de tasks, não um provedor Git. "
            "Use `neo tasks config` para configurá-lo.",
            as_json=as_json,
        )
    try:
        return validate_git_provider(provider)
    except ValueError as e:
        _fail_usage(str(e), as_json=as_json)


# ============================================================================
# neo git config (set | get | list | unset)
# ============================================================================


@git_config_app.command("set")
def git_config_set(
    ctx: typer.Context,
    key: str = Argument(
        ...,
        help=f"Chave de configuração ({', '.join(SUPPORTED_GIT_CONFIG_KEYS)}).",
    ),
    value: str = Argument(..., help="Valor a ser atribuído à chave."),
) -> None:
    """Define o valor de uma chave na seção [git] do config.toml."""
    as_json = is_json_mode(ctx)
    try:
        valid_key, clean_val = set_git_config_value(key, value)
    except ValueError as e:
        _fail_usage(str(e), as_json=as_json)

    print_success(
        f"Configuração Git atualizada: [bold]{valid_key}[/bold] = [cyan]{clean_val}[/cyan]",
        as_json=as_json,
        json_payload={"status": "success", "key": valid_key, "value": clean_val},
    )


@git_config_app.command("get")
def git_config_get(
    ctx: typer.Context,
    key: str = Argument(
        ...,
        help=f"Chave de configuração ({', '.join(SUPPORTED_GIT_CONFIG_KEYS)}).",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Exibe o valor atual e a origem de uma chave de configuração Git."""
    as_json = is_json_mode(ctx, json_output)
    try:
        valid_key, val, source = get_git_config_value(key)
    except ValueError as e:
        _fail_usage(str(e), as_json=as_json)

    if as_json:
        print_json({"key": valid_key, "value": val, "source": source})
    else:
        display_val = f"[cyan]{val}[/cyan]" if val is not None else "[dim]não definido[/dim]"
        print_panel(
            f"Configuração Git: {valid_key}",
            f"[bold]Chave:[/bold] {valid_key}\n"
            f"[bold]Valor:[/bold] {display_val}\n"
            f"[bold]Origem:[/bold] {source}",
        )


@git_config_app.command("list")
def git_config_list(
    ctx: typer.Context,
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Lista todas as chaves da seção [git] com seus valores e origens."""
    as_json = is_json_mode(ctx, json_output)
    values = list_git_config_values()

    if as_json:
        print_json(values)
    else:
        columns = ["Chave", "Valor", "Origem"]
        rows: list[list[str]] = []
        for k, info in values.items():
            val = info["value"]
            val_str = f"[cyan]{val}[/cyan]" if val is not None else "[dim]-[/dim]"
            rows.append([k, val_str, str(info["source"] or "default")])
        print_table("Configurações Git ([git])", columns, rows)


@git_config_app.command("unset")
def git_config_unset(
    ctx: typer.Context,
    key: str = Argument(
        ...,
        help=f"Chave de configuração a remover ({', '.join(SUPPORTED_GIT_CONFIG_KEYS)}).",
    ),
) -> None:
    """Remove uma chave personalizada da seção [git] do config.toml."""
    as_json = is_json_mode(ctx)
    try:
        valid_key = validate_git_config_key(key)
    except ValueError as e:
        _fail_usage(str(e), as_json=as_json)

    existed = unset_git_config_value(valid_key)
    print_success(
        f"Chave [bold]{valid_key}[/bold] removida de config.toml (restaurada para o padrão).",
        as_json=as_json,
        json_payload={"status": "success", "key": valid_key, "unset": True, "existed": existed},
    )


# Bloqueios orientativos para subcomandos legados em `neo git config`
@git_config_app.command(
    "auth",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def _legacy_config_auth(ctx: typer.Context) -> None:
    _fail_usage(
        "O comando `neo git config auth` foi removido. "
        "Use `neo git auth login --provider <github|bitbucket>`, "
        "`neo git auth status` ou `neo git auth logout --provider <github|bitbucket>`.",
        as_json=is_json_mode(ctx),
    )


@git_config_app.command(
    "set-provider",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def _legacy_config_set_provider(ctx: typer.Context) -> None:
    _fail_usage(
        "O comando `neo git config set-provider` foi removido. "
        "Use `neo git config set provider <github|bitbucket>`.",
        as_json=is_json_mode(ctx),
    )


@git_config_app.command(
    "get-provider",
    hidden=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def _legacy_config_get_provider(ctx: typer.Context) -> None:
    _fail_usage(
        "O comando `neo git config get-provider` foi removido. Use `neo git config get provider`.",
        as_json=is_json_mode(ctx),
    )


# ============================================================================
# neo git auth (login | status | logout)
# ============================================================================


@git_auth_app.command("login")
def git_auth_login(
    ctx: typer.Context,
    provider: str = Option(
        ...,
        "--provider",
        help=f"Provedor Git para autenticar: {', '.join(SUPPORTED_GIT_PROVIDERS)}.",
    ),
) -> None:
    """Autentica um provedor Git solicitando o token com entrada oculta."""
    as_json = is_json_mode(ctx)
    prov = _validate_provider_option(ctx, provider)

    if as_json:
        _fail_usage(
            "O comando `neo git auth login` exige entrada interativa oculta e não pode ser usado com `--json`. "
            "Para automação, defina `NEO_GITHUB_TOKEN` ou `NEO_BITBUCKET_EMAIL` e `NEO_BITBUCKET_TOKEN`.",
            as_json=True,
        )

    email: str | None = None
    if prov == "bitbucket":
        console.print(
            "[yellow]Aviso:[/yellow] App Passwords do Bitbucket Cloud foram descontinuadas. "
            "Informe o e-mail da sua conta Atlassian e um API Token."
        )
        email = typer.prompt("E-mail da conta Bitbucket").strip()
        if not email:
            _fail_usage("O e-mail da conta Bitbucket não pode ser vazio.", as_json=False)
        token = typer.prompt("API Token do Bitbucket", hide_input=True)
    else:
        token = typer.prompt("Personal Access Token do GitHub", hide_input=True)

    try:
        set_credential(prov, token, email=email)
        source = get_credential_source(prov) or "keyring"
        prov_label = "GitHub" if prov == "github" else "Bitbucket Cloud"
        print_success(
            f"Credencial de {prov_label} salva com segurança (origem: {source}).",
            as_json=False,
        )
    except (KeyringError, OSError, RuntimeError, ValueError) as e:
        print_error(f"Falha ao salvar credencial: {e}", as_json=False, code=int(ExitCode.ERROR))
        raise typer.Exit(code=int(ExitCode.ERROR)) from e


@git_auth_app.command("status")
def git_auth_status(
    ctx: typer.Context,
    provider: str | None = Option(
        None,
        "--provider",
        help="Filtra o status por provedor ('github' ou 'bitbucket').",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Exibe o estado de autenticação dos provedores Git sem expor tokens."""
    as_json = is_json_mode(ctx, json_output)
    providers_to_check: tuple[GitProviderType, ...]
    if provider is not None:
        providers_to_check = (_validate_provider_option(ctx, provider, json_output),)
    else:
        providers_to_check = ("github", "bitbucket")

    items: list[dict[str, object]] = []
    for prov in providers_to_check:
        source = get_credential_source(prov)
        entry: dict[str, object] = {
            "provider": prov,
            "authenticated": source is not None,
            "source": source or "none",
        }
        if prov == "bitbucket":
            entry["email"] = get_bitbucket_email()
        items.append(entry)

    if as_json:
        print_json(items if provider is None else items[0])
    else:
        columns = ["Provedor", "Autenticado", "Origem", "Conta / E-mail"]
        rows: list[list[str]] = []
        for item in items:
            auth_ok = bool(item["authenticated"])
            status_str = "[bold green]Sim[/bold green]" if auth_ok else "[red]Não[/red]"
            src_str = str(item["source"]) if auth_ok else "[dim]none[/dim]"
            email_val = str(item.get("email") or "-")
            rows.append([str(item["provider"]), status_str, src_str, email_val])
        print_table("Status de Autenticação Git", columns, rows)


@git_auth_app.command("logout")
def git_auth_logout(
    ctx: typer.Context,
    provider: str = Option(
        ...,
        "--provider",
        help=f"Provedor Git para desconectar: {', '.join(SUPPORTED_GIT_PROVIDERS)}.",
    ),
    yes: bool = Option(
        False,
        "--yes",
        help="Pula a confirmação interativa.",
    ),
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Remove as credenciais salvas de um provedor Git."""
    as_json = is_json_mode(ctx, json_output)
    prov = _validate_provider_option(ctx, provider, json_output)

    if not yes:
        if as_json:
            _fail_usage(
                "A opção `--yes` é obrigatória em `neo git auth logout` quando `--json` está ativo.",
                as_json=True,
            )
        confirmed = typer.confirm(f"Deseja remover as credenciais salvas de '{prov}'?")
        if not confirmed:
            print_error("Operação cancelada pelo usuário.", as_json=False, code=int(ExitCode.ERROR))
            raise typer.Exit(code=int(ExitCode.ERROR))

    if delete_credential(prov):
        print_success(
            f"Credenciais de '{prov}' removidas com sucesso.",
            as_json=as_json,
            json_payload={"status": "success", "provider": prov, "logged_out": True},
        )
    else:
        print_error(
            f"Nenhuma credencial salva encontrada para '{prov}'.",
            as_json=as_json,
            code=int(ExitCode.NOT_FOUND),
        )
        raise typer.Exit(code=int(ExitCode.NOT_FOUND))


# ============================================================================
# neo git status
# ============================================================================


def _inspect_local_git_status() -> dict[str, object]:
    """Inspeciona o diretório atual via comandos git locais."""
    try:
        res_inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res_inside.returncode != 0 or res_inside.stdout.strip().lower() != "true":
            return {
                "is_git_repo": False,
                "current_branch": None,
                "clean": None,
                "modified_files": 0,
                "remote_url": None,
            }

        res_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=False,
        )
        branch = res_branch.stdout.strip() if res_branch.returncode == 0 else None

        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
        lines = (
            [ln for ln in res_status.stdout.splitlines() if ln.strip()]
            if res_status.returncode == 0
            else []
        )

        res_remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
        )
        remote_url = res_remote.stdout.strip() if res_remote.returncode == 0 else None

        return {
            "is_git_repo": True,
            "current_branch": branch or "HEAD (detached)",
            "clean": len(lines) == 0,
            "modified_files": len(lines),
            "remote_url": remote_url or None,
        }
    except (subprocess.SubprocessError, OSError):
        return {
            "is_git_repo": False,
            "current_branch": None,
            "clean": None,
            "modified_files": 0,
            "remote_url": None,
        }


@git_app.command("status")
def git_status(
    ctx: typer.Context,
    json_output: bool = Option(
        False,
        "--json",
        help="Emite a saída em formato JSON estruturado no stdout.",
    ),
) -> None:
    """Exibe o diagnóstico do repositório Git local, provedor resolvido e autenticação."""
    as_json = is_json_mode(ctx, json_output)
    local_info = _inspect_local_git_status()

    try:
        provider, provider_source = resolve_git_provider_and_source()
    except ValueError as e:
        _fail_usage(str(e), as_json=as_json)

    workspace, workspace_source = resolve_git_workspace_and_source(provider)
    _rem_prov, _rem_ws, detected_repo = detect_git_remote_details()
    auth_source = get_credential_source(provider)
    authenticated = auth_source is not None

    payload = {
        "local": local_info,
        "provider": provider,
        "provider_source": provider_source,
        "workspace": workspace,
        "workspace_source": workspace_source,
        "repo": detected_repo,
        "authenticated": authenticated,
        "auth_source": auth_source or "none",
    }

    if as_json:
        print_json(payload)
    else:
        is_repo = bool(local_info["is_git_repo"])
        tree_state = (
            "working tree limpa"
            if local_info["clean"]
            else f"{local_info['modified_files']} arquivo(s) alterado(s)"
        )
        repo_line = (
            f"[green]Sim[/green] (branch: [cyan]{local_info['current_branch']}[/cyan], {tree_state})"
            if is_repo
            else "[dim]Não (diretório fora de um repositório Git)[/dim]"
        )
        auth_line = (
            f"[bold green]Autenticado[/bold green] ({auth_source})"
            if authenticated
            else f"[bold red]Não autenticado[/bold red] (execute `neo git auth login --provider {provider}`)"
        )
        ws_line = (
            f"[cyan]{workspace}[/cyan] ({workspace_source})"
            if workspace
            else "[dim]auto (API)[/dim]"
        )
        rem_repo_line = f"[cyan]{detected_repo}[/cyan]" if detected_repo else "[dim]-[/dim]"

        print_panel(
            "Status do Contexto Git",
            f"[bold]Repositório Local:[/bold] {repo_line}\n"
            f"[bold]Remote Origin:[/bold] {local_info['remote_url'] or '-'}\n"
            f"[bold]Provedor Ativo:[/bold] [cyan]{provider}[/cyan] ({provider_source})\n"
            f"[bold]Workspace Ativo:[/bold] {ws_line}\n"
            f"[bold]Repositório Detectado:[/bold] {rem_repo_line}\n"
            f"[bold]Autenticação:[/bold] {auth_line}",
        )
