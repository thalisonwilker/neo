"""Testes unitários para `neo.config` (feature 0002, 0006, 0011 e 0014)."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from keyring.errors import KeyringError

from neo.config import (
    SUPPORTED_GIT_CONFIG_KEYS,
    SUPPORTED_SERVICES,
    ExitCode,
    delete_credential,
    get_all_services_status,
    get_bitbucket_email,
    get_credential,
    get_credential_source,
    get_default_provider_config,
    get_default_workspace_config,
    get_git_config_value,
    get_task_columns_config,
    list_git_config_values,
    mask_token,
    set_credential,
    set_default_provider_config,
    set_default_workspace_config,
    set_git_config_value,
    set_task_columns_config,
    unset_git_config_value,
    validate_git_config_key,
    validate_git_provider,
    validate_service,
)


def test_exit_codes_standard():
    """AC-8 (0014): Códigos de saída padronizados 0 a 5."""
    assert ExitCode.SUCCESS == 0
    assert ExitCode.ERROR == 1
    assert ExitCode.USAGE_ERROR == 2
    assert ExitCode.AUTH_ERROR == 3
    assert ExitCode.NOT_FOUND == 4
    assert ExitCode.UNSUPPORTED == 5


def test_supported_services():
    assert "bitbucket" in SUPPORTED_SERVICES
    assert "shortcut" in SUPPORTED_SERVICES
    assert "github" in SUPPORTED_SERVICES


def test_validate_service():
    assert validate_service("bitbucket") == "bitbucket"
    assert validate_service("shortcut") == "shortcut"
    with pytest.raises(ValueError, match="Serviço não suportado"):
        validate_service("invalido")


def test_mask_token():
    assert mask_token("secret123456") == "********3456"
    assert mask_token("dev@acme.com:secret123456") == "********3456"
    assert mask_token("abc") == "***"
    assert mask_token("") == ""


def test_set_credential_empty_raises():
    with pytest.raises(ValueError, match="O token não pode ser vazio"):
        set_credential("bitbucket", "   ")


def test_AC_3_precedence_env_over_keyring_and_file(tmp_path: Path):
    """AC-3 (0014) e AC-4 (0002): Precedência de variáveis de ambiente (NEO_* e alternativas)."""
    with (
        patch.dict(
            os.environ,
            {
                "NEO_BITBUCKET_EMAIL": "dev@acme.com",
                "NEO_BITBUCKET_TOKEN": "token-from-env",
                "NEO_GITHUB_TOKEN": "ghp_from_neo_env",
            },
            clear=True,
        ),
        patch("keyring.get_password", return_value="token-from-keyring"),
    ):
        token = get_credential("bitbucket", config_dir=tmp_path)
        source = get_credential_source("bitbucket", config_dir=tmp_path)
        assert token == "dev@acme.com:token-from-env"
        assert source == "env"
        assert get_bitbucket_email(config_dir=tmp_path) == "dev@acme.com"

        gh_tok = get_credential("github", config_dir=tmp_path)
        assert gh_tok == "ghp_from_neo_env"
        assert get_credential_source("github", config_dir=tmp_path) == "env"


def test_precedence_keyring_over_file(tmp_path: Path):
    cred_file = tmp_path / "credentials.toml"
    cred_file.write_text('[auth]\nbitbucket = "token-from-file"\n')

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.get_password", return_value="token-from-keyring"),
    ):
        token = get_credential("bitbucket", config_dir=tmp_path)
        source = get_credential_source("bitbucket", config_dir=tmp_path)
        assert token == "token-from-keyring"
        assert source == "keyring"


def test_fallback_to_file_when_no_env_or_keyring(tmp_path: Path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('[auth]\nshortcut = "token-from-file"\n')

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.get_password", return_value=None),
    ):
        token = get_credential("shortcut", config_dir=tmp_path)
        source = get_credential_source("shortcut", config_dir=tmp_path)
        assert token == "token-from-file"
        assert source == "file"


def test_keyring_failure_falls_back_to_credentials_file_on_set(tmp_path: Path):
    """AC-3 (0014): Fallback para ~/.config/neo/credentials.toml com permissão 0600."""
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.set_password", side_effect=KeyringError("Keyring indisponível")),
        patch("keyring.get_password", return_value=None),
    ):
        set_credential(
            "bitbucket",
            "api-token-fallback",
            config_dir=tmp_path,
            email="user@acme.com",
        )
        token = get_credential("bitbucket", config_dir=tmp_path)
        source = get_credential_source("bitbucket", config_dir=tmp_path)
        assert token == "user@acme.com:api-token-fallback"
        assert source == "file"
        assert get_bitbucket_email(config_dir=tmp_path) == "user@acme.com"
        assert (tmp_path / "credentials.toml").exists()


def test_set_and_delete_credential(tmp_path: Path):
    stored_passwords = {}

    def mock_set(service_name, username, password):
        stored_passwords[username] = password

    def mock_get(service_name, username):
        return stored_passwords.get(username)

    def mock_del(service_name, username):
        stored_passwords.pop(username, None)

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.set_password", side_effect=mock_set),
        patch("keyring.get_password", side_effect=mock_get),
        patch("keyring.delete_password", side_effect=mock_del),
    ):
        set_credential("bitbucket", "novo-token", config_dir=tmp_path)
        assert get_credential("bitbucket", config_dir=tmp_path) == "novo-token"

        deleted = delete_credential("bitbucket", config_dir=tmp_path)
        assert deleted is True
        assert get_credential("bitbucket", config_dir=tmp_path) is None


def test_get_all_services_status(tmp_path: Path):
    with (
        patch.dict(os.environ, {"BITBUCKET_TOKEN": "token-123456"}, clear=True),
        patch("keyring.get_password", return_value=None),
    ):
        statuses = get_all_services_status(config_dir=tmp_path)
        assert "bitbucket" in statuses
        assert statuses["bitbucket"]["configured"] is True
        assert statuses["bitbucket"]["source"] == "env"
        assert statuses["bitbucket"]["masked_token"] == "********3456"
        assert statuses["shortcut"]["configured"] is False
        assert statuses["github"]["configured"] is False


def test_AC_2_git_config_keys_and_token_rejection(tmp_path: Path):
    """AC-2 (0014): Chaves da seção [git] e proibição explícita da chave 'token'."""
    assert set(SUPPORTED_GIT_CONFIG_KEYS) == {
        "provider",
        "workspace",
        "default-branch",
        "branch-pattern",
        "commit-format",
    }

    with pytest.raises(ValueError, match="neo git auth login"):
        validate_git_config_key("token")

    with pytest.raises(ValueError, match="Chave de configuração desconhecida"):
        validate_git_config_key("unknown-key")

    with patch.dict(os.environ, {}, clear=True):
        set_git_config_value("provider", "github", config_dir=tmp_path)
        set_git_config_value("workspace", "minha-org", config_dir=tmp_path)
        set_git_config_value("default-branch", "develop", config_dir=tmp_path)
        set_git_config_value("branch-pattern", "feat/{id}", config_dir=tmp_path)
        set_git_config_value("commit-format", "feat: {message}", config_dir=tmp_path)

        assert get_git_config_value("provider", config_dir=tmp_path) == (
            "provider",
            "github",
            "config",
        )
        assert get_git_config_value("workspace", config_dir=tmp_path) == (
            "workspace",
            "minha-org",
            "config",
        )
        assert get_git_config_value("default-branch", config_dir=tmp_path) == (
            "default-branch",
            "develop",
            "config",
        )

        all_vals = list_git_config_values(config_dir=tmp_path)
        assert all_vals["branch-pattern"]["value"] == "feat/{id}"
        assert all_vals["commit-format"]["value"] == "feat: {message}"

        assert unset_git_config_value("default-branch", config_dir=tmp_path) is True
        assert get_git_config_value("default-branch", config_dir=tmp_path) == (
            "default-branch",
            "main",
            "default",
        )


def test_default_workspace_config(tmp_path: Path):
    with patch.dict(os.environ, {}, clear=True):
        assert get_default_workspace_config("bitbucket", config_dir=tmp_path) is None
        assert get_default_workspace_config("github", config_dir=tmp_path) is None

        set_default_workspace_config("meu-workspace", provider="bitbucket", config_dir=tmp_path)
        assert get_default_workspace_config("bitbucket", config_dir=tmp_path) == "meu-workspace"

        set_default_workspace_config("minha-org", provider="github", config_dir=tmp_path)
        assert get_default_workspace_config("github", config_dir=tmp_path) == "minha-org"

        with pytest.raises(ValueError, match="não pode ser vazio"):
            set_default_workspace_config("  ", provider="bitbucket", config_dir=tmp_path)


def test_default_provider_config(tmp_path: Path):
    assert validate_git_provider("github") == "github"
    assert validate_git_provider("bitbucket") == "bitbucket"
    with pytest.raises(ValueError, match="Provedor Git não suportado"):
        validate_git_provider("gitlab")

    assert get_default_provider_config(config_dir=tmp_path) is None

    set_default_provider_config("github", config_dir=tmp_path)
    assert get_default_provider_config(config_dir=tmp_path) == "github"

    set_default_provider_config("bitbucket", config_dir=tmp_path)
    assert get_default_provider_config(config_dir=tmp_path) == "bitbucket"


def test_task_columns_config(tmp_path: Path):
    assert get_task_columns_config("shortcut", config_dir=tmp_path) is None

    set_task_columns_config(
        todo=["📝 - Backlog de Sprint", "🚨 - Bug"],
        doing=["🚧 - Em Progresso"],
        done=["✅ - Finalizado"],
        service="shortcut",
        config_dir=tmp_path,
    )

    cfg = get_task_columns_config("shortcut", config_dir=tmp_path)
    assert cfg == {
        "todo": ["📝 - Backlog de Sprint", "🚨 - Bug"],
        "doing": ["🚧 - Em Progresso"],
        "done": ["✅ - Finalizado"],
    }

    with pytest.raises(ValueError, match="devem ter pelo menos uma coluna"):
        set_task_columns_config(
            todo=[],
            doing=["🚧 - Em Progresso"],
            done=["✅ - Finalizado"],
            service="shortcut",
            config_dir=tmp_path,
        )
