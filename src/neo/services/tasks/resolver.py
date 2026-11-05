"""Composição dos provedores de tarefas disponíveis."""

from neo.services.tasks.api.shortcut.client import ShortcutClient
from neo.services.tasks.provider import TaskProvider


def create_task_provider(service: str, token: str, timeout: float = 15.0) -> TaskProvider:
    if service != "shortcut":
        raise ValueError(f"Serviço de tarefas não suportado: {service}")
    return ShortcutClient(token=token, timeout=timeout)
