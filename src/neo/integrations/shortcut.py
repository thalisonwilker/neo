"""Cliente HTTP para comunicação com a REST API v3 do Shortcut (https://developer.shortcut.com/api/rest/v3)."""

from __future__ import annotations

import logging

import httpx

from neo.integrations.shortcut_models import (
    ShortcutMember,
    ShortcutStory,
    StoryAnalysis,
)

logger = logging.getLogger(__name__)


class ShortcutError(Exception):
    """Exceção base para erros da integração com Shortcut."""


class ShortcutAuthError(ShortcutError):
    """Erro de autenticação ou permissão (401/403)."""


class ShortcutNotFoundError(ShortcutError):
    """Recurso não encontrado (404)."""


class ShortcutRateLimitError(ShortcutError):
    """Limite de requisições excedido (429)."""


class ShortcutClient:
    """Cliente para a REST API v3 do Shortcut."""

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.app.shortcut.com/api/v3",
        timeout: float = 15.0,
    ) -> None:
        self.token = token.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_headers(self) -> dict[str, str]:
        return {
            "Shortcut-Token": self.token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _handle_response_error(self, response: httpx.Response, context: str) -> None:
        if response.status_code in (401, 403):
            raise ShortcutAuthError(
                f"Falha de autenticação no Shortcut ({response.status_code}). "
                "Verifique seu token executando `neo tasks config set`."
            )
        if response.status_code == 404:
            raise ShortcutNotFoundError(
                f"A story ou recurso solicitado em {context} não foi encontrada (404)."
            )
        if response.status_code == 429:
            raise ShortcutRateLimitError("Limite de requisições à API do Shortcut atingido (429).")
        if response.is_error:
            try:
                err_data = response.json()
                msg = err_data.get("message", response.text)
            except (ValueError, KeyError):
                msg = response.text
            raise ShortcutError(f"Erro na API do Shortcut ({response.status_code}): {msg}")

    # 1. Função 1: Obter membro atual autenticado
    def get_current_member(self) -> ShortcutMember:
        """Obtém informações do membro autenticado atual (GET /api/v3/member)."""
        url = f"{self.base_url}/member"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers())
            self._handle_response_error(resp, "obter dados do membro")
            return ShortcutMember.from_api_dict(resp.json())

    # 2. Função 2: Listar stories
    def list_stories(self, owner_id: str | None = None) -> list[ShortcutStory]:
        """Lista stories ativas no workspace (GET /api/v3/search/stories)."""
        query = "!is:archived"
        if owner_id:
            query += f" owner:{owner_id}"

        return self.search_stories(query)

    # 3. Função 3: Buscar stories por query
    def search_stories(self, query: str) -> list[ShortcutStory]:
        """Pesquisa stories por termo ou query avançada (GET /api/v3/search/stories?query=...)."""
        url = f"{self.base_url}/search/stories"
        params = {"query": query}

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers(), params=params)
            self._handle_response_error(resp, f"buscar stories por query '{query}'")
            data = resp.json()
            stories_raw = data.get("data", [])
            stories: list[ShortcutStory] = []
            for item in stories_raw:
                if isinstance(item, dict):
                    stories.append(ShortcutStory.from_api_dict(item))
            return stories

    # 4. Função 4: Obter detalhes de uma story
    def get_story(self, story_id: int | str) -> ShortcutStory:
        """Obtém detalhes completos de uma story pelo ID (GET /api/v3/stories/{story_id})."""
        url = f"{self.base_url}/stories/{story_id}"

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers())
            self._handle_response_error(resp, f"story #{story_id}")
            return ShortcutStory.from_api_dict(resp.json())

    # 5. Função 5: Analisar contexto de uma story
    def analyze_story(self, story_id: int | str) -> StoryAnalysis:
        """Obtém a story e gera um relatório heurístico de contexto para branch e commits."""
        story = self.get_story(story_id)
        return StoryAnalysis.from_story(story)
