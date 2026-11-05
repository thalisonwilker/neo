"""Seleção do provedor Git configurado."""

from neo.commands.git._common import _fail_usage
from neo.config import set_git_config_value
from neo.output import print_success


def set_provider(key: str, value: str, as_json: bool) -> None:
    try:
        valid_key, clean_val = set_git_config_value(key, value)
    except ValueError as exc:
        _fail_usage(str(exc), as_json=as_json)
    print_success(
        f"Configuração Git atualizada: [bold]{valid_key}[/bold] = [cyan]{clean_val}[/cyan]",
        as_json=as_json,
        json_payload={"status": "success", "key": valid_key, "value": clean_val},
    )
