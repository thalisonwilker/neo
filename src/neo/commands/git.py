"""Comandos Git: configuração, branches, repositórios, commits e status."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import NoReturn
from urllib.parse import urlsplit, urlunsplit

import httpx
import typer
from keyring.errors import KeyringError
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.branch import branch_app, current_branch, select_branch
from neo.commands.commits import commits_app
from neo.commands.repo import repo_app
from neo.config import (
    SUPPORTED_GIT_CONFIG_KEYS,
    ExitCode,
    GitProviderType,
    delete_credential,
    get_credential_source,
    get_git_config_value,
    list_git_config_values,
    set_credential,
    set_git_config_value,
    unset_git_config_value,
    validate_git_config_key,
    validate_git_provider,
)
from neo.git_context import (
    get_task,
    resolve_repo_path,
    select_repo,
    selected_repo,
    set_task,
    unset_repo,
    unset_task,
)
from neo.integrations.bitbucket import BitbucketClient, BitbucketError
from neo.integrations.github import GitHubClient
from neo.integrations.resolver import (
    detect_git_remote_details,
    resolve_git_provider_and_source,
    resolve_git_workspace_and_source,
)
from neo.output import print_error, print_json, print_panel, print_success, print_table

git_app = typer.Typer(
    name="git",
    help="Gerencia configuração, repositórios e branches no GitHub e Bitbucket Cloud.",
    no_args_is_help=True,
)

git_config_app = typer.Typer(
    name="config",
    help="Gerencia preferências do módulo Git na seção [git] de config.toml (set, get, list, unset).",
    no_args_is_help=True,
)

git_app.add_typer(git_config_app, name="config")
git_app.add_typer(repo_app, name="repo")
git_app.add_typer(commits_app, name="commits")
git_app.add_typer(branch_app, name="branch")


def _fail_usage(message: str, as_json: bool) -> NoReturn:
    print_error(message, as_json=as_json, code=int(ExitCode.USAGE_ERROR))
    raise typer.Exit(code=int(ExitCode.USAGE_ERROR))


def _configured_provider(as_json: bool) -> GitProviderType:
    """Obtém apenas um provedor explicitamente configurado, sem inferir do remote."""
    try:
        _, provider, source = get_git_config_value("provider")
        if not provider or source not in ("config", "env"):
            _fail_usage(
                "Configure primeiro o provedor com `neo git config set provider <github|bitbucket>`.",
                as_json=as_json,
            )
        return validate_git_provider(provider)
    except ValueError as exc:
        _fail_usage(str(exc), as_json=as_json)


def _api_key_info() -> dict[str, str | None]:
    """Retorna estado e origem, sem ler ou expor o segredo."""
    try:
        _, provider, source = get_git_config_value("provider")
        if not provider or source not in ("env", "config"):
            return {"value": None, "source": "none"}
        valid_provider = validate_git_provider(provider)
        credential_source = get_credential_source(valid_provider)
    except ValueError:
        credential_source = None
    return {
        "value": "Configurado" if credential_source else None,
        "source": credential_source or "none",
    }


def _set_api_key(as_json: bool) -> None:
    """Valida a credencial fornecida antes de substituir a credencial armazenada."""
    provider = _configured_provider(as_json)
    if as_json:
        _fail_usage("`config set api-key` requer entrada interativa oculta.", as_json=True)
    email: str | None = None
    if provider == "bitbucket":
        email = typer.prompt("E-mail da conta Bitbucket").strip()
        if not email:
            _fail_usage("O e-mail da conta Bitbucket não pode ser vazio.", as_json=False)
    token = typer.prompt("Chave de API", hide_input=True).strip()
    if not token:
        _fail_usage("A chave de API não pode ser vazia.", as_json=False)
    try:
        if provider == "github":
            GitHubClient(token=token).get_current_user()
        else:
            BitbucketClient(token=token, username=email).list_workspaces()
    except (BitbucketError, httpx.HTTPError, OSError, ValueError):
        print_error(
            "Não foi possível validar a chave de API no provedor. A credencial anterior foi preservada.",
            as_json=False,
            code=int(ExitCode.AUTH_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.AUTH_ERROR)) from None
    try:
        set_credential(provider, token, email=email)
    except (KeyringError, OSError, RuntimeError, ValueError):
        print_error(
            "Não foi possível salvar a credencial.", as_json=False, code=int(ExitCode.ERROR)
        )
        raise typer.Exit(code=int(ExitCode.ERROR)) from None
    print_success(f"Credencial de {provider} validada e salva.", as_json=False)


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
    value: str | None = Argument(None, help="Valor a ser atribuído à chave (exceto api-key)."),
) -> None:
    """Define o valor de uma chave na seção [git] do config.toml."""
    as_json = is_json_mode(ctx)
    if key.strip().lower() == "api-key":
        if value is not None:
            _fail_usage(
                "Não informe a chave como argumento; ela será solicitada com entrada oculta.",
                as_json,
            )
        _set_api_key(as_json)
        return
    if value is None:
        _fail_usage("Informe o valor da configuração.", as_json)
    normalized = key.strip().lower()
    if normalized in ("repo", "task", "branch"):
        try:
            if normalized == "repo":
                value = str(select_repo(Path(value)))
            elif normalized == "task":
                set_task(value)
            else:
                select_branch(value)
        except (ValueError, OSError) as exc:
            _fail_usage(str(exc), as_json)
        print_success(
            f"Configuração Git atualizada: {normalized} = {value}",
            as_json=as_json,
            json_payload={"status": "success", "key": normalized, "value": value},
        )
        return
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
    if key.strip().lower() == "api-key":
        info = _api_key_info()
        if as_json:
            print_json({"key": "api-key", **info})
        else:
            print_panel(
                "Configuração Git: api-key",
                f"Estado: {info['value'] or 'Não configurado'}\nOrigem: {info['source']}",
            )
        return
    normalized = key.strip().lower()
    if normalized in ("repo", "task", "branch"):
        try:
            if normalized == "repo":
                selected = selected_repo()
                val = str(selected) if selected else None
            elif normalized == "task":
                val = get_task()
            else:
                val = current_branch()
        except ValueError as exc:
            _fail_usage(str(exc), as_json)
        if as_json:
            print_json({"key": normalized, "value": val, "source": "context"})
        else:
            print_panel(f"Configuração Git: {normalized}", f"Valor: {val or '-'}\nOrigem: context")
        return
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
    values["api-key"] = _api_key_info()
    try:
        selected = selected_repo()
        values["repo"] = {"value": str(selected) if selected else None, "source": "context"}
        values["task"] = {"value": get_task(), "source": "context"}
        values["branch"] = {"value": current_branch(), "source": "context"}
    except ValueError:
        values.setdefault("repo", {"value": None, "source": "context"})
        values["task"] = {"value": None, "source": "context"}
        values["branch"] = {"value": None, "source": "context"}

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
    yes: bool = Option(False, "--yes", help="Confirma a remoção da credencial armazenada."),
) -> None:
    """Remove uma chave personalizada da seção [git] do config.toml."""
    as_json = is_json_mode(ctx)
    normalized = key.strip().lower()
    if normalized in ("repo", "task", "branch"):
        if normalized == "branch":
            _fail_usage(
                "A branch ativa é estado do Git e não pode ser removida; selecione outra branch.",
                as_json,
            )
        try:
            existed = unset_repo() if normalized == "repo" else unset_task()
        except (ValueError, OSError) as exc:
            _fail_usage(str(exc), as_json)
        print_success(
            f"Configuração Git removida: {normalized}",
            as_json=as_json,
            json_payload={"status": "success", "key": normalized, "existed": existed},
        )
        return
    if key.strip().lower() == "api-key":
        provider = _configured_provider(as_json)
        if not yes:
            if as_json:
                _fail_usage("Use --yes para remover a credencial em modo JSON.", as_json=True)
            if not typer.confirm(f"Deseja remover a credencial salva de '{provider}'?"):
                print_error(
                    "Operação cancelada pelo usuário.", as_json=False, code=int(ExitCode.ERROR)
                )
                raise typer.Exit(code=int(ExitCode.ERROR))
        removed = delete_credential(provider)
        print_success(
            "Credencial armazenada removida."
            if removed
            else "Nenhuma credencial armazenada encontrada.",
            as_json=as_json,
            json_payload={"status": "success", "key": "api-key", "removed": removed},
        )
        return
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
        "Use `neo git config set api-key`, `neo git config get api-key` ou "
        "`neo git config unset api-key`.",
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
# neo git status
# ============================================================================


def _inspect_local_git_status() -> dict[str, object]:
    """Inspeciona o diretório atual via comandos git locais."""
    try:
        selected = selected_repo()
        cwd = resolve_repo_path() if selected else None
        res_inside = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
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
            cwd=cwd,
        )
        branch = res_branch.stdout.strip() if res_branch.returncode == 0 else None

        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
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
            cwd=cwd,
        )
        remote_url = res_remote.stdout.strip() if res_remote.returncode == 0 else None
        if remote_url and "://" in remote_url:
            parts = urlsplit(remote_url)
            remote_url = urlunsplit(
                (parts.scheme, parts.netloc.rsplit("@", 1)[-1], parts.path, "", "")
            )

        return {
            "is_git_repo": True,
            "current_branch": branch or "HEAD (detached)",
            "clean": len(lines) == 0,
            "modified_files": len(lines),
            "remote_url": remote_url or None,
        }
    except (subprocess.SubprocessError, OSError, ValueError):
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
    try:
        task = get_task()
        selected_path = selected_repo()
    except ValueError:
        task = None
        selected_path = None

    payload = {
        "local": local_info,
        "provider": provider,
        "provider_source": provider_source,
        "workspace": workspace,
        "workspace_source": workspace_source,
        "repo": detected_repo,
        "authenticated": authenticated,
        "auth_source": auth_source or "none",
        "task": task,
        "selected_repo": str(selected_path) if selected_path else None,
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
            else "[bold red]Não autenticado[/bold red] (execute `neo git config set api-key`)"
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
            f"[bold]Repositório Selecionado:[/bold] {selected_path or '-'}\n"
            f"[bold]Task:[/bold] {task or '-'}\n"
            f"[bold]Autenticação:[/bold] {auth_line}",
        )
