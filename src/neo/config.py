"""Módulo de configuração e gerenciamento seguro de credenciais do Neo.

Suporta hierarquia de precedência:
1. Variáveis de ambiente (BITBUCKET_TOKEN, SHORTCUT_API_TOKEN)
2. Keyring seguro do sistema operacional
3. Arquivo local ~/.config/neo/config.toml (permissões 0600)
"""

from __future__ import annotations

import logging
import os
import stat
import tomllib
from pathlib import Path
from typing import Any, Literal

import keyring
from keyring.errors import KeyringError

logger = logging.getLogger(__name__)

KEYRING_SERVICE_NAME = "neo-cli"
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "neo"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"

ServiceType = Literal["bitbucket", "shortcut", "github"]
SUPPORTED_SERVICES: tuple[ServiceType, ...] = ("bitbucket", "shortcut", "github")

GitProviderType = Literal["bitbucket", "github"]
SUPPORTED_GIT_PROVIDERS: tuple[GitProviderType, ...] = ("bitbucket", "github")

TaskServiceType = Literal["shortcut"]
SUPPORTED_TASK_SERVICES: tuple[TaskServiceType, ...] = ("shortcut",)
DEFAULT_TASK_SERVICE: TaskServiceType = "shortcut"

ENV_VAR_MAPPING: dict[ServiceType, tuple[str, ...]] = {
    "bitbucket": ("BITBUCKET_TOKEN", "BITBUCKET_APP_PASSWORD"),
    "shortcut": ("SHORTCUT_API_TOKEN", "SHORTCUT_TOKEN"),
    "github": ("GITHUB_TOKEN", "GH_TOKEN"),
}


def validate_service(service: str) -> ServiceType:
    """Valida se o serviço informado é suportado."""
    normalized = service.strip().lower()
    if normalized not in SUPPORTED_SERVICES:
        valid_services = ", ".join(SUPPORTED_SERVICES)
        raise ValueError(
            f"Serviço não suportado: '{service}'. Serviços suportados: {valid_services}"
        )
    return normalized


def validate_git_provider(provider: str) -> GitProviderType:
    """Valida se o provedor Git informado é suportado."""
    normalized = provider.strip().lower()
    if normalized not in SUPPORTED_GIT_PROVIDERS:
        valid_providers = ", ".join(SUPPORTED_GIT_PROVIDERS)
        raise ValueError(
            f"Provedor Git não suportado: '{provider}'. Provedores suportados: {valid_providers}"
        )
    return normalized


def validate_task_service(service: str) -> TaskServiceType:
    """Valida se o serviço de tasks informado é suportado."""
    normalized = service.strip().lower()
    if normalized not in SUPPORTED_TASK_SERVICES:
        valid_services = ", ".join(SUPPORTED_TASK_SERVICES)
        raise ValueError(
            f"Serviço de tasks não suportado: '{service}'. Serviços suportados: {valid_services}"
        )
    return normalized


def mask_token(token: str) -> str:
    """Mascara o token preservando apenas os 4 caracteres finais se houver tamanho suficiente."""
    if not token:
        return ""
    length = len(token)
    if length <= 6:
        return "*" * length
    masked_part = "*" * (length - 4)
    visible_part = token[-4:]
    return f"{masked_part}{visible_part}"


def _get_config_path(config_dir: Path | None = None) -> Path:
    """Retorna o caminho do arquivo de configuração."""
    base_dir = config_dir or DEFAULT_CONFIG_DIR
    return base_dir / "config.toml"


def _read_file_config(config_file: Path) -> dict[str, Any]:
    """Lê as configurações do arquivo TOML."""
    if not config_file.exists():
        return {}
    try:
        with config_file.open("rb") as f:
            return tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError) as exc:
        logger.debug("Falha ao ler arquivo de configuração %s: %s", config_file, exc)
        return {}


def _write_file_config(config_file: Path, data: dict[str, Any]) -> None:
    """Escreve as configurações no arquivo TOML garantindo permissões 0600."""
    config_file.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    for section, values in data.items():
        if isinstance(values, dict) and values:
            lines.append(f"[{section}]")
            for k, v in values.items():
                if isinstance(v, bool):
                    lines.append(f"{k} = {str(v).lower()}")
                elif isinstance(v, (int, float)):
                    lines.append(f"{k} = {v}")
                else:
                    lines.append(f'{k} = "{v}"')
            lines.append("")

    content = "\n".join(lines).strip() + "\n"
    config_file.write_text(content, encoding="utf-8")
    try:
        config_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except OSError as exc:
        logger.debug("Não foi possível alterar permissões de %s: %s", config_file, exc)


def get_default_provider_config(config_dir: Path | None = None) -> GitProviderType | None:
    """Recupera o provedor Git padrão configurado em config.toml."""
    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    git_cfg = data.get("git", {})
    if isinstance(git_cfg, dict):
        provider = git_cfg.get("default_provider")
        if isinstance(provider, str) and provider.strip() in SUPPORTED_GIT_PROVIDERS:
            return provider.strip()  # type: ignore[return-value]
    return None


def set_default_provider_config(provider: str, config_dir: Path | None = None) -> None:
    """Salva o provedor Git padrão em config.toml."""
    prov = validate_git_provider(provider)
    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    if "git" not in data or not isinstance(data["git"], dict):
        data["git"] = {}
    data["git"]["default_provider"] = prov
    _write_file_config(config_file, data)


def get_default_workspace_config(
    provider: str = "bitbucket", config_dir: Path | None = None
) -> str | None:
    """Recupera o workspace/org padrão configurado para um provedor específico."""
    prov = validate_git_provider(provider)
    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    prov_cfg = data.get(prov, {})
    if isinstance(prov_cfg, dict):
        ws = prov_cfg.get("default_workspace")
        if isinstance(ws, str) and ws.strip():
            return ws.strip()
    return None


def set_default_workspace_config(
    workspace: str, provider: str = "bitbucket", config_dir: Path | None = None
) -> None:
    """Salva o workspace/org padrão para um provedor específico no arquivo config.toml."""
    prov = validate_git_provider(provider)
    clean_ws = workspace.strip()
    if not clean_ws:
        raise ValueError("O slug do workspace/organização não pode ser vazio.")
    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    if prov not in data or not isinstance(data[prov], dict):
        data[prov] = {}
    data[prov]["default_workspace"] = clean_ws
    _write_file_config(config_file, data)


def get_credential_source(service: str, config_dir: Path | None = None) -> str | None:
    """Retorna a fonte da credencial ('env', 'keyring', 'file') ou None."""
    svc = validate_service(service)

    # 1. Variáveis de ambiente
    for env_var in ENV_VAR_MAPPING[svc]:
        if os.environ.get(env_var):
            return "env"

    # 2. Keyring do SO
    try:
        token = keyring.get_password(KEYRING_SERVICE_NAME, svc)
        if token:
            return "keyring"
    except (KeyringError, OSError, RuntimeError) as exc:
        logger.debug("Falha ao consultar keyring para %s: %s", svc, exc)

    # 3. Arquivo config.toml
    config_file = _get_config_path(config_dir)
    file_data = _read_file_config(config_file)
    auth = file_data.get("auth", {})
    if auth.get(svc):
        return "file"

    return None


def get_credential(service: str, config_dir: Path | None = None) -> str | None:
    """Recupera a credencial do serviço seguindo a hierarquia de precedência."""
    svc = validate_service(service)

    # 1. Variáveis de ambiente
    for env_var in ENV_VAR_MAPPING[svc]:
        val = os.environ.get(env_var)
        if val:
            return val

    # 2. Keyring do SO
    try:
        token = keyring.get_password(KEYRING_SERVICE_NAME, svc)
        if token:
            return token
    except (KeyringError, OSError, RuntimeError) as exc:
        logger.debug("Falha ao obter senha do keyring para %s: %s", svc, exc)

    # 3. Arquivo de configuração
    config_file = _get_config_path(config_dir)
    file_data = _read_file_config(config_file)
    auth = file_data.get("auth", {})
    token_from_file = auth.get(svc)
    if isinstance(token_from_file, str) and token_from_file:
        return token_from_file

    return None


def set_credential(service: str, token: str, config_dir: Path | None = None) -> None:
    """Salva a credencial do serviço no Keyring (com fallback para config.toml)."""
    svc = validate_service(service)
    clean_token = token.strip()
    if not clean_token:
        raise ValueError("O token não pode ser vazio.")

    # Tenta salvar no Keyring
    keyring_success = False
    try:
        keyring.set_password(KEYRING_SERVICE_NAME, svc, clean_token)
        keyring_success = True
    except (KeyringError, OSError, RuntimeError) as exc:
        logger.debug("Falha ao salvar no keyring (%s), utilizando fallback: %s", svc, exc)
        keyring_success = False

    # Se falhou no Keyring, grava no arquivo de fallback
    if not keyring_success:
        config_file = _get_config_path(config_dir)
        data = _read_file_config(config_file)
        if "auth" not in data:
            data["auth"] = {}
        data["auth"][svc] = clean_token
        _write_file_config(config_file, data)


def delete_credential(service: str, config_dir: Path | None = None) -> bool:
    """Remove a credencial do serviço do Keyring e do arquivo de configuração."""
    svc = validate_service(service)

    has_keyring = False
    try:
        has_keyring = keyring.get_password(KEYRING_SERVICE_NAME, svc) is not None
    except (KeyringError, OSError, RuntimeError) as exc:
        logger.debug("Falha ao checar keyring antes de deletar (%s): %s", svc, exc)

    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    has_file = "auth" in data and svc in data["auth"]

    if not has_keyring and not has_file:
        return False

    deleted = False
    if has_keyring:
        try:
            keyring.delete_password(KEYRING_SERVICE_NAME, svc)
            deleted = True
        except (KeyringError, OSError, RuntimeError) as exc:
            logger.debug("Falha ao deletar do keyring (%s): %s", svc, exc)

    if has_file:
        del data["auth"][svc]
        _write_file_config(config_file, data)
        deleted = True

    return deleted


def get_all_services_status(config_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Retorna o status de configuração de todos os serviços suportados."""
    statuses: dict[str, dict[str, Any]] = {}
    for svc in SUPPORTED_SERVICES:
        source = get_credential_source(svc, config_dir=config_dir)
        token = get_credential(svc, config_dir=config_dir)
        statuses[svc] = {
            "configured": source is not None,
            "source": source,
            "masked_token": mask_token(token) if token else None,
        }
    return statuses
