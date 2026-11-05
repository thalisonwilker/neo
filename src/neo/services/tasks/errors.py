"""Erros comuns dos provedores de tarefas."""


class TaskProviderError(Exception):
    """Exceção base para erros da integração com Shortcut."""


class TaskProviderAuthError(TaskProviderError):
    """Erro de autenticação ou permissão (401/403)."""


class TaskProviderNotFoundError(TaskProviderError):
    """Recurso não encontrado (404)."""


class TaskProviderRateLimitError(TaskProviderError):
    """Limite de requisições excedido (429)."""


class TaskProviderUnsupportedError(TaskProviderError):
    """O provedor não oferece uma capacidade necessária à operação."""
