"""Testes unitarios para ApiSettings (0037 tarefa 1, AC-1 e AC-9)."""

from __future__ import annotations

from pathlib import Path

import pytest

from neo.infrastructure.api_settings import ApiSettings, obter_api_settings


def test_AC_1_e_AC_9_settings_defaults_sem_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """AC-1 e AC-9: defaults seguros com Postgres local e CORS restrito ao painel."""
    monkeypatch.chdir(tmp_path)
    for var in (
        "NEO_DATABASE_URL",
        "NEO_API_CORS_ORIGINS",
        "CLERK_JWKS_URL",
        "CLERK_ISSUER",
        "CLERK_AUTHORIZED_PARTIES",
        "CLERK_SECRET_KEY",
        "CLERK_API_BASE_URL",
    ):
        monkeypatch.delenv(var, raising=False)

    settings = obter_api_settings()

    assert settings.neo_database_url == "postgresql+asyncpg://neo:neo@localhost:5432/neo"
    assert settings.cors_origins == ["http://localhost:3100"]
    assert settings.clerk_authorized_parties == ("http://localhost:3100",)
    assert settings.clerk_api_base_url == "https://api.clerk.com"


def test_AC_9_settings_multiplas_origens_e_override_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """AC-9: interpreta listas separadas por virgula e sobrescritas via ambiente."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("NEO_DATABASE_URL", "postgresql+asyncpg://user:pwd@db:5432/custom")
    monkeypatch.setenv(
        "NEO_API_CORS_ORIGINS",
        "http://localhost:3100 , https://painel.neo.dev , ",
    )
    monkeypatch.setenv(
        "CLERK_AUTHORIZED_PARTIES",
        "http://localhost:3100, https://painel.neo.dev",
    )
    monkeypatch.setenv("CLERK_JWKS_URL", "https://clerk.example/.well-known/jwks.json")
    monkeypatch.setenv("CLERK_ISSUER", "https://clerk.example")
    monkeypatch.setenv("CLERK_SECRET_KEY", "sk_test_fake")

    settings = ApiSettings()

    assert settings.neo_database_url == "postgresql+asyncpg://user:pwd@db:5432/custom"
    assert settings.cors_origins == ["http://localhost:3100", "https://painel.neo.dev"]
    assert settings.clerk_authorized_parties == (
        "http://localhost:3100",
        "https://painel.neo.dev",
    )
    assert settings.clerk_jwks_url == "https://clerk.example/.well-known/jwks.json"
    assert settings.clerk_issuer == "https://clerk.example"
    assert settings.clerk_secret_key == "sk_test_fake"
