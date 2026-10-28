"""Módulo de configuração, códigos de saída e gerenciamento seguro de credenciais do Neo.

Hierarquia de precedência de configuração Git:
1. Opção de linha de comando (`--provider`, `--workspace`)
2. Variáveis de ambiente (`NEO_GIT_PROVIDER`, `NEO_GIT_WORKSPACE`)
3. Seção `[git]` do arquivo `~/.config/neo/config.toml`
4. Auto-detecção pelo `remote origin` do repositório Git local
5. Padrão

Hierarquia de precedência de credenciais:
1. Variáveis de ambiente (`NEO_GITHUB_TOKEN` / `GITHUB_TOKEN` / `GH_TOKEN`,
   `NEO_BITBUCKET_EMAIL` + `NEO_BITBUCKET_TOKEN` / `BITBUCKET_TOKEN`, `SHORTCUT_API_TOKEN`)
2. Keyring seguro do sistema operacional
3. Arquivo local `~/.config/neo/credentials.toml` (ou fallback em `config.toml`) com permissão `0600`
"""

from __future__ import annotations

import logging
import os
import stat
import tomllib
from enum import IntEnum
from pathlib import Path
from typing import Any, Literal

import keyring
from keyring.errors import KeyringError

logger = logging.getLogger(__name__)


class ExitCode(IntEnum):
    """Códigos de saída padronizados da CLI Neo."""

    SUCCESS = 0
    ERROR = 1
    USAGE_ERROR = 2
    AUTH_ERROR = 3
    NOT_FOUND = 4
    UNSUPPORTED = 5


KEYRING_SERVICE_NAME = "neo-cli"
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "neo"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.toml"
DEFAULT_CREDENTIALS_FILE = DEFAULT_CONFIG_DIR / "credentials.toml"

ServiceType = Literal["bitbucket", "shortcut", "github"]
SUPPORTED_SERVICES: tuple[ServiceType, ...] = ("bitbucket", "shortcut", "github")

GitProviderType = Literal["bitbucket", "github"]
SUPPORTED_GIT_PROVIDERS: tuple[GitProviderType, ...] = ("bitbucket", "github")

GitConfigKey = Literal[
    "provider",
    "workspace",
    "default-branch",
    "branch-pattern",
    "commit-format",
]
SUPPORTED_GIT_CONFIG_KEYS: tuple[GitConfigKey, ...] = (
    "provider",
    "workspace",
    "default-branch",
    "branch-pattern",
    "commit-format",
)
FORBIDDEN_GIT_CONFIG_KEYS: frozenset[str] = frozenset(
    {"token", "api-token", "auth", "password", "secret"}
)

DEFAULT_GIT_CONFIG_VALUES: dict[GitConfigKey, str | None] = {
    "provider": None,
    "workspace": None,
    "default-branch": "main",
    "branch-pattern": "{type}/{id}-{slug}",
    "commit-format": "{type}: {message}",
}

TaskServiceType = Literal["shortcut"]
SUPPORTED_TASK_SERVICES: tuple[TaskServiceType, ...] = ("shortcut",)
DEFAULT_TASK_SERVICE: TaskServiceType = "shortcut"

ENV_VAR_MAPPING: dict[ServiceType, tuple[str, ...]] = {
    "bitbucket": ("NEO_BITBUCKET_TOKEN", "BITBUCKET_TOKEN", "BITBUCKET_APP_PASSWORD"),
    "shortcut": ("SHORTCUT_API_TOKEN", "SHORTCUT_TOKEN"),
    "github": ("NEO_GITHUB_TOKEN", "GITHUB_TOKEN", "GH_TOKEN"),
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


def validate_git_config_key(key: str) -> GitConfigKey:
    """Valida se a chave de configuração do módulo `neo git config` é suportada."""
    normalized = key.strip().lower()
    if normalized in FORBIDDEN_GIT_CONFIG_KEYS:
        raise ValueError(
            f"A chave '{normalized}' não existe em `neo git config`. "
            "Credenciais nunca são salvas como configuração: use "
            "`neo git auth login --provider <github|bitbucket>`."
        )
    if normalized not in SUPPORTED_GIT_CONFIG_KEYS:
        valid_keys = ", ".join(SUPPORTED_GIT_CONFIG_KEYS)
        raise ValueError(
            f"Chave de configuração desconhecida: '{key}'. Chaves válidas: {valid_keys}"
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
    # Se estiver no formato email:token, mascara apenas a parte do token ou tudo exceto 4 finais
    secret = token.split(":", 1)[1] if ":" in token else token
    length = len(secret)
    if length <= 6:
        return "*" * length
    masked_part = "*" * (length - 4)
    visible_part = secret[-4:]
    return f"{masked_part}{visible_part}"


def _get_config_path(config_dir: Path | None = None) -> Path:
    """Retorna o caminho do arquivo de configuração (`config.toml`)."""
    base_dir = config_dir or DEFAULT_CONFIG_DIR
    return base_dir / "config.toml"


def _get_credentials_path(config_dir: Path | None = None) -> Path:
    """Retorna o caminho do arquivo de credenciais (`credentials.toml`)."""
    base_dir = config_dir or DEFAULT_CONFIG_DIR
    return base_dir / "credentials.toml"


def _read_file_config(config_file: Path) -> dict[str, Any]:
    """Lê as configurações de um arquivo TOML."""
    if not config_file.exists():
        return {}
    try:
        with config_file.open("rb") as f:
            return tomllib.load(f)
    except (tomllib.TOMLDecodeError, OSError) as exc:
        logger.debug("Falha ao ler arquivo TOML %s: %s", config_file, exc)
        return {}


def _write_file_config(config_file: Path, data: dict[str, Any]) -> None:
    """Escreve as configurações no arquivo TOML garantindo permissões 0600."""
    config_file.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    for section, values in data.items():
        if isinstance(values, dict) and values:
            lines.append(f"[{section}]")
            for k, v in values.items():
                if v is None:
                    continue
                if isinstance(v, bool):
                    lines.append(f"{k} = {str(v).lower()}")
                elif isinstance(v, (int, float)):
                    lines.append(f"{k} = {v}")
                elif isinstance(v, list):
                    escaped_items = [
                        f'"{str(item).replace(chr(34), chr(92) + chr(34))}"' for item in v
                    ]
                    lines.append(f"{k} = [{', '.join(escaped_items)}]")
                else:
                    escaped_val = str(v).replace("\\", "\\\\").replace('"', '\\"')
                    lines.append(f'{k} = "{escaped_val}"')
            lines.append("")

    content = "\n".join(lines).strip() + "\n" if lines else ""
    config_file.write_text(content, encoding="utf-8")
    try:
        config_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except OSError as exc:
        logger.debug("Não foi possível alterar permissões de %s: %s", config_file, exc)


def set_git_config_value(
    key: str, value: str, config_dir: Path | None = None
) -> tuple[GitConfigKey, str]:
    """Define uma chave na seção `[git]` de `config.toml`."""
    valid_key = validate_git_config_key(key)
    clean_val = value.strip()
    if not clean_val:
        raise ValueError(f"O valor para '{valid_key}' não pode ser vazio.")

    if valid_key == "provider":
        clean_val = validate_git_provider(clean_val)

    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    if "git" not in data or not isinstance(data["git"], dict):
        data["git"] = {}

    data["git"][valid_key] = clean_val
    # Remove chave legada se existir para evitar ambiguidade
    if valid_key == "provider" and "default_provider" in data["git"]:
        del data["git"]["default_provider"]

    _write_file_config(config_file, data)
    return valid_key, clean_val


def get_git_config_value(
    key: str, config_dir: Path | None = None
) -> tuple[GitConfigKey, str | None, str]:
    """Recupera o valor efetivo de uma chave de `neo git config` e sua fonte ('env', 'config', 'default')."""
    valid_key = validate_git_config_key(key)

    if valid_key == "provider":
        env_prov = os.environ.get("NEO_GIT_PROVIDER", "").strip()
        if env_prov:
            return valid_key, validate_git_provider(env_prov), "env"
    elif valid_key == "workspace":
        env_ws = os.environ.get("NEO_GIT_WORKSPACE", "").strip()
        if env_ws:
            return valid_key, env_ws, "env"

    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    git_cfg = data.get("git", {})
    if isinstance(git_cfg, dict):
        raw = git_cfg.get(valid_key)
        if raw is None and valid_key == "provider":
            raw = git_cfg.get("default_provider")
        if isinstance(raw, str) and raw.strip():
            return valid_key, raw.strip(), "config"

    return valid_key, DEFAULT_GIT_CONFIG_VALUES[valid_key], "default"


def list_git_config_values(config_dir: Path | None = None) -> dict[str, dict[str, str | None]]:
    """Lista todas as chaves suportadas de `neo git config` com valor e fonte."""
    result: dict[str, dict[str, str | None]] = {}
    for k in SUPPORTED_GIT_CONFIG_KEYS:
        _, val, source = get_git_config_value(k, config_dir=config_dir)
        result[k] = {"value": val, "source": source}
    return result


def unset_git_config_value(key: str, config_dir: Path | None = None) -> bool:
    """Remove uma chave da seção `[git]` do `config.toml`. Retorna True se existia."""
    valid_key = validate_git_config_key(key)
    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    git_cfg = data.get("git", {})
    if not isinstance(git_cfg, dict):
        return False

    existed = False
    if valid_key in git_cfg:
        del git_cfg[valid_key]
        existed = True
    if valid_key == "provider" and "default_provider" in git_cfg:
        del git_cfg["default_provider"]
        existed = True

    if existed:
        _write_file_config(config_file, data)
    return existed


def get_default_provider_config(config_dir: Path | None = None) -> GitProviderType | None:
    """Recupera o provedor Git configurado na seção `[git]` de `config.toml`."""
    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    git_cfg = data.get("git", {})
    if isinstance(git_cfg, dict):
        provider = git_cfg.get("provider") or git_cfg.get("default_provider")
        if isinstance(provider, str) and provider.strip().lower() in SUPPORTED_GIT_PROVIDERS:
            return provider.strip().lower()  # type: ignore[return-value]
    return None


def set_default_provider_config(provider: str, config_dir: Path | None = None) -> None:
    """Salva o provedor Git padrão na seção `[git]` de `config.toml`."""
    set_git_config_value("provider", provider, config_dir=config_dir)


def get_default_workspace_config(
    provider: str = "bitbucket", config_dir: Path | None = None
) -> str | None:
    """Recupera o workspace/org padrão (respeitando `NEO_GIT_WORKSPACE`, `[git].workspace` e seção do provedor)."""
    validate_git_provider(provider)
    env_ws = os.environ.get("NEO_GIT_WORKSPACE", "").strip()
    if env_ws:
        return env_ws

    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)

    git_cfg = data.get("git", {})
    if isinstance(git_cfg, dict):
        ws_git = git_cfg.get("workspace")
        if isinstance(ws_git, str) and ws_git.strip():
            return ws_git.strip()

    prov = provider.strip().lower()
    prov_cfg = data.get(prov, {})
    if isinstance(prov_cfg, dict):
        ws = prov_cfg.get("default_workspace")
        if isinstance(ws, str) and ws.strip():
            return ws.strip()
    return None


def set_default_workspace_config(
    workspace: str, provider: str = "bitbucket", config_dir: Path | None = None
) -> None:
    """Salva o workspace/org padrão na seção `[git]` e na seção do provedor em `config.toml`."""
    prov = validate_git_provider(provider)
    clean_ws = workspace.strip()
    if not clean_ws:
        raise ValueError("O slug do workspace/organização não pode ser vazio.")
    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    if "git" not in data or not isinstance(data["git"], dict):
        data["git"] = {}
    data["git"]["workspace"] = clean_ws
    if prov not in data or not isinstance(data[prov], dict):
        data[prov] = {}
    data[prov]["default_workspace"] = clean_ws
    _write_file_config(config_file, data)


def get_task_columns_config(
    service: str = DEFAULT_TASK_SERVICE, config_dir: Path | None = None
) -> dict[str, list[str]] | None:
    """Recupera o mapeamento de colunas (todo, doing, done) configurado para o serviço de tasks."""
    svc = validate_task_service(service)
    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    svc_cfg = data.get(svc, {})
    if not isinstance(svc_cfg, dict):
        return None

    todo = svc_cfg.get("todo_columns")
    doing = svc_cfg.get("doing_columns")
    done = svc_cfg.get("done_columns")

    if (
        isinstance(todo, list)
        and isinstance(doing, list)
        and isinstance(done, list)
        and len(todo) > 0
        and len(doing) > 0
        and len(done) > 0
    ):
        clean_todo = [str(x).strip() for x in todo if str(x).strip()]
        clean_doing = [str(x).strip() for x in doing if str(x).strip()]
        clean_done = [str(x).strip() for x in done if str(x).strip()]
        if clean_todo and clean_doing and clean_done:
            return {
                "todo": clean_todo,
                "doing": clean_doing,
                "done": clean_done,
            }
    return None


def set_task_columns_config(
    todo: list[str],
    doing: list[str],
    done: list[str],
    service: str = DEFAULT_TASK_SERVICE,
    config_dir: Path | None = None,
) -> None:
    """Salva o mapeamento de colunas (A fazer, Fazendo, Feito) de um serviço de tasks em config.toml."""
    svc = validate_task_service(service)
    clean_todo = [c.strip() for c in todo if c and c.strip()]
    clean_doing = [c.strip() for c in doing if c and c.strip()]
    clean_done = [c.strip() for c in done if c and c.strip()]

    if not clean_todo or not clean_doing or not clean_done:
        raise ValueError(
            "As colunas 'A fazer', 'Fazendo' e 'Feito' devem ter pelo menos uma coluna mapeada cada."
        )

    config_file = _get_config_path(config_dir)
    data = _read_file_config(config_file)
    if svc not in data or not isinstance(data[svc], dict):
        data[svc] = {}
    data[svc]["todo_columns"] = clean_todo
    data[svc]["doing_columns"] = clean_doing
    data[svc]["done_columns"] = clean_done
    _write_file_config(config_file, data)


def _get_env_credential(svc: ServiceType) -> str | None:
    """Recupera credencial a partir das variáveis de ambiente suportadas."""
    if svc == "bitbucket":
        email = os.environ.get("NEO_BITBUCKET_EMAIL", "").strip()
        bb_token = os.environ.get("NEO_BITBUCKET_TOKEN", "").strip()
        if bb_token:
            if email and ":" not in bb_token:
                return f"{email}:{bb_token}"
            return bb_token
        for fallback_var in ("BITBUCKET_TOKEN", "BITBUCKET_APP_PASSWORD"):
            val = os.environ.get(fallback_var, "").strip()
            if val:
                if email and ":" not in val:
                    return f"{email}:{val}"
                return val
        return None

    for env_var in ENV_VAR_MAPPING[svc]:
        val = os.environ.get(env_var, "").strip()
        if val:
            return val
    return None


def _get_file_credential(svc: ServiceType, config_dir: Path | None = None) -> str | None:
    """Lê credencial de `credentials.toml` ou do fallback legado em `config.toml`."""
    for path in (_get_credentials_path(config_dir), _get_config_path(config_dir)):
        file_data = _read_file_config(path)
        auth = file_data.get("auth", {})
        if isinstance(auth, dict):
            token_from_file = auth.get(svc)
            if isinstance(token_from_file, str) and token_from_file.strip():
                email = auth.get(f"{svc}_email")
                raw_tok = token_from_file.strip()
                if (
                    svc == "bitbucket"
                    and isinstance(email, str)
                    and email.strip()
                    and ":" not in raw_tok
                ):
                    return f"{email.strip()}:{raw_tok}"
                return raw_tok
    return None


def get_credential_source(service: str, config_dir: Path | None = None) -> str | None:
    """Retorna a fonte da credencial ('env', 'keyring', 'file') ou None."""
    svc = validate_service(service)

    # 1. Variáveis de ambiente
    if _get_env_credential(svc):
        return "env"

    # 2. Keyring do SO
    try:
        token = keyring.get_password(KEYRING_SERVICE_NAME, svc)
        if token:
            return "keyring"
    except (KeyringError, OSError, RuntimeError) as exc:
        logger.debug("Falha ao consultar keyring para %s: %s", svc, exc)

    # 3. Arquivo credentials.toml / config.toml
    if _get_file_credential(svc, config_dir=config_dir):
        return "file"

    return None


def get_credential(service: str, config_dir: Path | None = None) -> str | None:
    """Recupera a credencial do serviço seguindo a hierarquia de precedência."""
    svc = validate_service(service)

    # 1. Variáveis de ambiente
    env_val = _get_env_credential(svc)
    if env_val:
        return env_val

    # 2. Keyring do SO
    try:
        token = keyring.get_password(KEYRING_SERVICE_NAME, svc)
        if token:
            return token
    except (KeyringError, OSError, RuntimeError) as exc:
        logger.debug("Falha ao obter senha do keyring para %s: %s", svc, exc)

    # 3. Arquivo local restrito (0600)
    return _get_file_credential(svc, config_dir=config_dir)


def get_bitbucket_email(config_dir: Path | None = None) -> str | None:
    """Retorna o e-mail configurado para o Bitbucket Cloud, se disponível."""
    env_email = os.environ.get("NEO_BITBUCKET_EMAIL", "").strip()
    if env_email:
        return env_email

    cred = get_credential("bitbucket", config_dir=config_dir)
    if cred and ":" in cred:
        return cred.split(":", 1)[0].strip() or None
    return None


def set_credential(
    service: str,
    token: str,
    config_dir: Path | None = None,
    email: str | None = None,
) -> None:
    """Salva a credencial do serviço no Keyring (com fallback para credentials.toml 0600)."""
    svc = validate_service(service)
    clean_token = token.strip()
    if not clean_token:
        raise ValueError("O token não pode ser vazio.")

    stored_value = clean_token
    if svc == "bitbucket" and email and email.strip() and ":" not in clean_token:
        stored_value = f"{email.strip()}:{clean_token}"

    # Tenta salvar no Keyring
    keyring_success = False
    try:
        keyring.set_password(KEYRING_SERVICE_NAME, svc, stored_value)
        keyring_success = True
    except (KeyringError, OSError, RuntimeError) as exc:
        logger.debug("Falha ao salvar no keyring (%s), utilizando fallback 0600: %s", svc, exc)
        keyring_success = False

    # Se falhou no Keyring, grava em credentials.toml (0600)
    if not keyring_success:
        cred_file = _get_credentials_path(config_dir)
        data = _read_file_config(cred_file)
        if "auth" not in data or not isinstance(data["auth"], dict):
            data["auth"] = {}
        data["auth"][svc] = stored_value
        _write_file_config(cred_file, data)


def delete_credential(service: str, config_dir: Path | None = None) -> bool:
    """Remove a credencial do serviço do Keyring e dos arquivos locais."""
    svc = validate_service(service)

    has_keyring = False
    try:
        has_keyring = keyring.get_password(KEYRING_SERVICE_NAME, svc) is not None
    except (KeyringError, OSError, RuntimeError) as exc:
        logger.debug("Falha ao checar keyring antes de deletar (%s): %s", svc, exc)

    cred_file = _get_credentials_path(config_dir)
    cred_data = _read_file_config(cred_file)
    has_cred_file = (
        "auth" in cred_data and isinstance(cred_data["auth"], dict) and svc in cred_data["auth"]
    )

    config_file = _get_config_path(config_dir)
    cfg_data = _read_file_config(config_file)
    has_cfg_file = (
        "auth" in cfg_data and isinstance(cfg_data["auth"], dict) and svc in cfg_data["auth"]
    )

    if not has_keyring and not has_cred_file and not has_cfg_file:
        return False

    deleted = False
    if has_keyring:
        try:
            keyring.delete_password(KEYRING_SERVICE_NAME, svc)
            deleted = True
        except (KeyringError, OSError, RuntimeError) as exc:
            logger.debug("Falha ao deletar do keyring (%s): %s", svc, exc)

    if has_cred_file:
        del cred_data["auth"][svc]
        _write_file_config(cred_file, cred_data)
        deleted = True

    if has_cfg_file:
        del cfg_data["auth"][svc]
        _write_file_config(config_file, cfg_data)
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
