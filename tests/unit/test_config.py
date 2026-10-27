import os
from pathlib import Path
from unittest.mock import patch

import pytest
from keyring.errors import KeyringError

from neo.config import (
    SUPPORTED_SERVICES,
    delete_credential,
    get_all_services_status,
    get_credential,
    get_credential_source,
    mask_token,
    set_credential,
    validate_service,
)


def test_supported_services():
    assert "bitbucket" in SUPPORTED_SERVICES
    assert "shortcut" in SUPPORTED_SERVICES


def test_validate_service():
    assert validate_service("bitbucket") == "bitbucket"
    assert validate_service("shortcut") == "shortcut"
    with pytest.raises(ValueError, match="Serviço não suportado"):
        validate_service("invalido")


def test_mask_token():
    assert mask_token("secret123456") == "********3456"
    assert mask_token("abc") == "***"
    assert mask_token("") == ""


def test_set_credential_empty_raises():
    with pytest.raises(ValueError, match="O token não pode ser vazio"):
        set_credential("bitbucket", "   ")


def test_precedence_env_over_keyring_and_file(tmp_path: Path):
    with (
        patch.dict(os.environ, {"BITBUCKET_TOKEN": "token-from-env"}),
        patch("keyring.get_password", return_value="token-from-keyring"),
    ):
        token = get_credential("bitbucket", config_dir=tmp_path)
        source = get_credential_source("bitbucket", config_dir=tmp_path)
        assert token == "token-from-env"
        assert source == "env"


def test_precedence_keyring_over_file(tmp_path: Path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('[auth]\nbitbucket = "token-from-file"\n')

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


def test_keyring_failure_falls_back_to_file_on_set(tmp_path: Path):
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("keyring.set_password", side_effect=KeyringError("Keyring indisponível")),
        patch("keyring.get_password", return_value=None),
    ):
        set_credential("shortcut", "token-fallback-file", config_dir=tmp_path)
        token = get_credential("shortcut", config_dir=tmp_path)
        source = get_credential_source("shortcut", config_dir=tmp_path)
        assert token == "token-fallback-file"
        assert source == "file"


def test_set_and_delete_credential(tmp_path: Path):
    stored_passwords = {}

    def mock_set(service_name, username, password):
        stored_passwords[username] = password

    def mock_get(service_name, username):
        return stored_passwords.get(username)

    def mock_del(service_name, username):
        stored_passwords.pop(username, None)

    with (
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
        patch.dict(os.environ, {"BITBUCKET_TOKEN": "token-123456"}),
        patch("keyring.get_password", return_value=None),
    ):
        statuses = get_all_services_status(config_dir=tmp_path)
        assert "bitbucket" in statuses
        assert statuses["bitbucket"]["configured"] is True
        assert statuses["bitbucket"]["source"] == "env"
        assert statuses["bitbucket"]["masked_token"] == "********3456"
        assert statuses["shortcut"]["configured"] is False
