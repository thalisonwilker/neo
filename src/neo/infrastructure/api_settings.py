"""Configuracoes da API FastAPI e integracoes de infraestrutura."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


class ApiSettings(BaseSettings):
    """Configuracoes tipadas carregadas de variaveis de ambiente e `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    neo_database_url: str = Field(
        default="postgresql+asyncpg://neo:neo@localhost:5432/neo",
        alias="NEO_DATABASE_URL",
    )
    neo_api_cors_origins_raw: str = Field(
        default="http://localhost:3100",
        alias="NEO_API_CORS_ORIGINS",
    )
    clerk_jwks_url: str = Field(default="", alias="CLERK_JWKS_URL")
    clerk_issuer: str = Field(default="", alias="CLERK_ISSUER")
    clerk_authorized_parties_raw: str = Field(
        default="http://localhost:3100",
        alias="CLERK_AUTHORIZED_PARTIES",
    )
    clerk_secret_key: str = Field(default="", alias="CLERK_SECRET_KEY")
    clerk_api_base_url: str = Field(
        default="https://api.clerk.com",
        alias="CLERK_API_BASE_URL",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Lista de origens permitidas pelo CORS."""
        return _split_csv(self.neo_api_cors_origins_raw)

    @property
    def clerk_authorized_parties(self) -> tuple[str, ...]:
        """Partes autorizadas (`azp`) aceitas nos tokens de sessao do Clerk."""
        return tuple(_split_csv(self.clerk_authorized_parties_raw))


def obter_api_settings() -> ApiSettings:
    """Carrega uma instancia de configuracoes da API a partir do ambiente atual."""
    return ApiSettings()
