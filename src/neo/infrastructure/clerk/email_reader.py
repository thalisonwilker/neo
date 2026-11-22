"""Leitor de e-mail principal do usuario via Clerk Backend API."""

from __future__ import annotations

from typing import Any

import httpx

from neo.domain.identidade import (
    ClerkIndisponivelError,
    DadosInvalidosError,
    Email,
    IdentidadeExterna,
)


class LeitorDeEmailClerk:
    """Consulta `GET /v1/users/{user_id}` no Clerk para obter o e-mail principal."""

    def __init__(
        self,
        secret_key: str,
        *,
        base_url: str = "https://api.clerk.com",
        timeout: float = 5.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._secret_key = secret_key.strip()
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._http_client = http_client

    async def _consultar_usuario(self, clerk_user_id: str) -> httpx.Response:
        url = f"{self._base_url}/v1/users/{clerk_user_id}"
        headers = {"Authorization": f"Bearer {self._secret_key}"}
        if self._http_client is not None:
            return await self._http_client.get(url, headers=headers, timeout=self._timeout)
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            return await client.get(url, headers=headers)

    def _extrair_email_principal(self, payload: Any) -> Email:
        if not isinstance(payload, dict):
            raise ClerkIndisponivelError()
        primary_id = payload.get("primary_email_address_id")
        enderecos = payload.get("email_addresses")
        if not isinstance(primary_id, str) or not isinstance(enderecos, list):
            raise ClerkIndisponivelError()

        for item in enderecos:
            if not isinstance(item, dict) or item.get("id") != primary_id:
                continue
            bruto = item.get("email_address")
            if isinstance(bruto, str):
                try:
                    return Email(bruto)
                except DadosInvalidosError as exc:
                    raise ClerkIndisponivelError() from exc

        raise ClerkIndisponivelError()

    async def obter_email_principal(self, identidade: IdentidadeExterna) -> Email:
        """Retorna o e-mail principal validado do usuario no Clerk."""
        if not self._secret_key:
            raise ClerkIndisponivelError()

        try:
            response = await self._consultar_usuario(identidade.clerk_user_id)
        except httpx.HTTPError as exc:
            raise ClerkIndisponivelError() from exc

        if response.status_code != 200:
            raise ClerkIndisponivelError()

        try:
            payload = response.json()
        except ValueError as exc:
            raise ClerkIndisponivelError() from exc

        return self._extrair_email_principal(payload)
