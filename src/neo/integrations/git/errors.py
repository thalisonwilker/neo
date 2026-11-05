"""Erros comuns dos provedores Git."""

from neo.config import ExitCode


class GitProviderError(Exception):
    """Exceção base para erros de provedores Git."""

    exit_code: int = int(ExitCode.ERROR)


class GitProviderAuthError(GitProviderError):
    """Erro de autenticação ou permissão (401/403)."""

    exit_code: int = int(ExitCode.AUTH_ERROR)


class GitProviderNotFoundError(GitProviderError):
    """Recurso não encontrado (404)."""

    exit_code: int = int(ExitCode.NOT_FOUND)


class GitProviderRateLimitError(GitProviderError):
    """Limite de requisições excedido (429)."""

    exit_code: int = int(ExitCode.ERROR)


class UnsupportedProviderOperationError(GitProviderError):
    """Operação ou comando não suportado pelo provedor ativo."""

    exit_code: int = int(ExitCode.UNSUPPORTED)

    def __init__(self, message: str, suggestion: str | None = None) -> None:
        self.suggestion = suggestion
        full_msg = f"{message} Alternativa sugerida: {suggestion}" if suggestion else message
        super().__init__(full_msg)
