"""Criação e clonagem de repositório remoto."""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import cast

import httpx
import typer
from rich.markup import escape
from typer import Argument, Option

from neo.commands._credentials import is_json_mode
from neo.commands.git import local_repo as common
from neo.config import ExitCode, get_bitbucket_project
from neo.integrations.git.api.bitbucket.client import BitbucketClient
from neo.integrations.git.errors import GitProviderError
from neo.output import print_error, print_success


def create_repo(
    ctx: typer.Context,
    name: str = Argument(..., help="Nome do repositório remoto."),
    path: Path | None = Option(None, "--path", help="Diretório pai do clone."),  # noqa: B008
    public: bool = Option(False, "--public", help="Cria o repositório remoto público."),
    description: str | None = Option(None, "--description", help="Descrição do repositório."),
    default_branch: str = Option("main", "--default-branch", help="Branch principal."),
) -> None:
    """Cria, clona e publica um repositório Git."""
    as_json = is_json_mode(ctx)
    name = name.strip()
    parent = (path or Path.cwd()).expanduser().absolute()
    target = parent / name
    if not name or name in (".", "..") or "/" in name or "\\" in name:
        print_error("Informe um nome válido para o repositório.", as_json=as_json, code=2)
        raise typer.Exit(code=2)
    if not parent.is_dir() or target.exists() or target.is_symlink():
        print_error("Diretório pai inválido ou destino já existente.", as_json=as_json, code=2)
        raise typer.Exit(code=2)
    try:
        branch_check = subprocess.run(
            ["git", "check-ref-format", "--branch", default_branch],
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        print_error("Não foi possível executar Git.", as_json=as_json, code=1)
        raise typer.Exit(code=1) from exc
    if branch_check.returncode or default_branch.startswith("-"):
        print_error("Informe uma branch válida.", as_json=as_json, code=2)
        raise typer.Exit(code=2)
    provider, client = common.resolve_git_provider(as_json=as_json)
    stage = "validação da conexão"
    remote_created = False
    try:
        client.validate_auth()
        workspace, _ = common.resolve_git_workspace_and_source(provider)
        if provider == "bitbucket":
            project_id = get_bitbucket_project(workspace)
            if not project_id:
                print_error(
                    "Projeto Bitbucket não configurado para este workspace. Execute `neo git config set workspace`.",
                    as_json=as_json,
                    code=int(ExitCode.USAGE_ERROR),
                )
                raise typer.Exit(code=int(ExitCode.USAGE_ERROR))
        stage = "criação do repositório remoto"
        if provider == "bitbucket":
            remote = cast(BitbucketClient, client).create_repository(
                name,
                workspace=workspace,
                is_private=not public,
                description=description,
                project_id=project_id,
            )
        else:
            remote = client.create_repository(
                name, workspace=workspace, is_private=not public, description=description
            )
        remote_created = True
        remote_url = remote.https_clone_url
        if not remote_url:
            raise ValueError("URL de clonagem ausente")
        common._validate_remote_url(provider, remote_url)
        stage = "clonagem"
        common._clone_with_credential(parent, target, provider, remote_url)
        stage = "preparação da branch e arquivos"
        common._run_git(target, "checkout", "--orphan", default_branch)
        readme = f"# {name}\n"
        if description is not None:
            readme += f"\n{description}\n"
        (target / "README.md").write_text(readme, encoding="utf-8")
        (target / "AGENTS.md").write_text("", encoding="utf-8")
        common._run_git(target, "add", "--", "README.md", "AGENTS.md")
        stage = "commit inicial"
        common._run_git(target, "commit", "-m", "first commit")
        stage = "push da branch inicial"
        common._push_with_credential(target, provider, remote_url)
        stage = "configuração da branch principal remota"
        if client.get_repository(remote.slug, workspace=workspace).main_branch != default_branch:
            client.set_default_branch(remote.slug, default_branch, workspace=workspace)
        stage = "seleção do repositório"
        common.select_repo(target)
    except typer.Exit:
        raise
    except (OSError, RuntimeError, ValueError, GitProviderError, httpx.HTTPError) as exc:
        state = "criado" if remote_created else "não confirmado"
        code = exc.exit_code if isinstance(exc, GitProviderError) else int(ExitCode.ERROR)
        print_error(
            f"Falha na etapa: {stage}. Caminho local: {escape(str(target)) if not as_json else target}; repositório remoto: {state}. "
            "Recursos existentes foram preservados.",
            as_json=as_json,
            code=code,
        )
        raise typer.Exit(code=code) from exc
    cd_command = f"cd {shlex.quote(str(target))}"
    print_success(
        f"Repositório criado e publicado: {escape(str(target))}\nPara acessar: {escape(cd_command)}",
        as_json=as_json,
        json_payload={
            "status": "success",
            "path": str(target),
            "provider": provider,
            "repo": remote.slug,
            "cd": cd_command,
        },
    )
