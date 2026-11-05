"""Configuração segura da credencial Git."""

import httpx
import typer
from keyring.errors import KeyringError

from neo.commands.git._common import _configured_provider, _fail_usage
from neo.config import ExitCode, set_credential
from neo.integrations.git.errors import GitProviderError
from neo.integrations.git.resolver import create_git_provider
from neo.output import print_error, print_success


def _set_api_key(as_json: bool) -> None:
    """Valida a credencial fornecida antes de substituir a credencial armazenada."""
    provider = _configured_provider(as_json)
    if as_json:
        _fail_usage("`config set api-key` requer entrada interativa oculta.", as_json=True)
    token = typer.prompt("Chave de API", hide_input=True).strip()
    if not token:
        _fail_usage("A chave de API não pode ser vazia.", as_json=False)
    try:
        create_git_provider(provider, token).validate_auth()
    except (GitProviderError, httpx.HTTPError, OSError, ValueError):
        print_error(
            "Conexão recusada",
            as_json=False,
            code=int(ExitCode.AUTH_ERROR),
        )
        raise typer.Exit(code=int(ExitCode.AUTH_ERROR)) from None
    try:
        set_credential(provider, token)
    except (KeyringError, OSError, RuntimeError, ValueError):
        print_error(
            "Não foi possível salvar a credencial.", as_json=False, code=int(ExitCode.ERROR)
        )
        raise typer.Exit(code=int(ExitCode.ERROR)) from None
    print_success("Conexão efetuada", as_json=False)
