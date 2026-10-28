"""Cliente HTTP para comunicação com a API REST 2.0 do Bitbucket Cloud."""

from __future__ import annotations

import base64
import logging
import re
from typing import Any

import httpx

from neo.config import ExitCode
from neo.integrations.bitbucket_models import (
    BitbucketCommit,
    BitbucketRepo,
    BitbucketWorkspace,
)

logger = logging.getLogger(__name__)


class BitbucketError(Exception):
    """Exceção base para erros de provedores Git."""

    exit_code: int = int(ExitCode.ERROR)


class BitbucketAuthError(BitbucketError):
    """Erro de autenticação ou permissão (401/403)."""

    exit_code: int = int(ExitCode.AUTH_ERROR)


class BitbucketNotFoundError(BitbucketError):
    """Recurso não encontrado (404)."""

    exit_code: int = int(ExitCode.NOT_FOUND)


class BitbucketRateLimitError(BitbucketError):
    """Limite de requisições excedido (429)."""

    exit_code: int = int(ExitCode.ERROR)


class UnsupportedProviderOperationError(BitbucketError):
    """Operação ou comando não suportado pelo provedor ativo."""

    exit_code: int = int(ExitCode.UNSUPPORTED)

    def __init__(self, message: str, suggestion: str | None = None) -> None:
        self.suggestion = suggestion
        full_msg = f"{message} Alternativa sugerida: {suggestion}" if suggestion else message
        super().__init__(full_msg)


class BitbucketClient:
    """Cliente para interagir com a API REST 2.0 do Bitbucket Cloud."""

    def __init__(
        self,
        token: str,
        username: str | None = None,
        base_url: str = "https://api.bitbucket.org/2.0",
        timeout: float = 15.0,
    ) -> None:
        self.token = token.strip()
        self.username = username.strip() if username else None
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if ":" in self.token:
            encoded = base64.b64encode(self.token.encode("utf-8")).decode("ascii")
            headers["Authorization"] = f"Basic {encoded}"
        elif self.username:
            auth_str = f"{self.username}:{self.token}"
            encoded = base64.b64encode(auth_str.encode("utf-8")).decode("ascii")
            headers["Authorization"] = f"Basic {encoded}"
        else:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _handle_response_error(self, response: httpx.Response, context: str) -> None:
        """Trata códigos de erro HTTP e traduz para exceções de domínio."""
        if response.status_code in (401, 403):
            raise BitbucketAuthError(
                f"Falha de autenticação no Bitbucket ({response.status_code}). "
                "Execute `neo git auth login --provider bitbucket` para atualizar seu API Token."
            )
        if response.status_code == 404:
            raise BitbucketNotFoundError(
                f"O recurso solicitado em {context} não foi encontrado (404)."
            )
        if response.status_code == 429:
            raise BitbucketRateLimitError(
                "Limite de requisições à API do Bitbucket atingido (429). Aguarde antes de tentar novamente."
            )
        if response.is_error:
            try:
                err_data = response.json()
                msg = err_data.get("error", {}).get("message", response.text)
            except (ValueError, KeyError):
                msg = response.text

            raise BitbucketError(f"Erro na API do Bitbucket ({response.status_code}): {msg}")

    def list_workspaces(self) -> list[BitbucketWorkspace]:
        """Lista todos os workspaces aos quais a conta autenticada tem acesso."""
        url = f"{self.base_url}/user/workspaces"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers())
            self._handle_response_error(resp, "listar workspaces do usuário")
            data = resp.json()
            workspaces: list[BitbucketWorkspace] = []
            for item in data.get("values", []):
                if isinstance(item, dict):
                    workspaces.append(BitbucketWorkspace.from_api_dict(item))
            return workspaces

    def get_default_workspace(self, ignore_config: bool = False) -> str:
        """Retorna o workspace padrão (respeitando config local ou fallback para API)."""
        if not ignore_config:
            from neo.config import get_default_workspace_config

            cfg_ws = get_default_workspace_config()
            if cfg_ws:
                return cfg_ws

        workspaces = self.list_workspaces()
        if not workspaces:
            raise BitbucketNotFoundError("Nenhum workspace encontrado para a conta autenticada.")
        return workspaces[0].slug

    def list_repositories(
        self, workspace: str | None = None, limit: int | None = None
    ) -> list[BitbucketRepo]:
        """Lista os repositórios do workspace seguindo paginação."""
        ws = workspace or self.get_default_workspace()
        next_url: str | None = f"{self.base_url}/repositories/{ws}"
        repos: list[BitbucketRepo] = []
        pages_fetched = 0
        max_pages = 10

        with httpx.Client(timeout=self.timeout) as client:
            while next_url and pages_fetched < max_pages:
                resp = client.get(next_url, headers=self._get_headers())
                self._handle_response_error(resp, f"repositórios do workspace '{ws}'")
                data = resp.json()
                for item in data.get("values", []):
                    if isinstance(item, dict):
                        repos.append(BitbucketRepo.from_api_dict(item))
                        if limit is not None and len(repos) >= limit:
                            return repos[:limit]
                next_raw = data.get("next")
                next_url = next_raw if isinstance(next_raw, str) and next_raw else None
                pages_fetched += 1

        return repos

    def search_repositories(
        self, query: str, workspace: str | None = None, limit: int | None = None
    ) -> list[BitbucketRepo]:
        """Pesquisa repositórios pelo nome, slug ou descrição."""
        all_repos = self.list_repositories(workspace=workspace)
        q = query.strip().lower()
        matched: list[BitbucketRepo] = []
        for r in all_repos:
            if (
                q in r.name.lower()
                or q in r.slug.lower()
                or (r.description and q in r.description.lower())
            ):
                matched.append(r)
                if limit is not None and len(matched) >= limit:
                    break
        return matched

    def get_repository(self, repo_slug: str, workspace: str | None = None) -> BitbucketRepo:
        """Obtém detalhes de um repositório específico."""
        ws = workspace or self.get_default_workspace()
        url = f"{self.base_url}/repositories/{ws}/{repo_slug}"

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers())
            self._handle_response_error(resp, f"repositório '{ws}/{repo_slug}'")
            return BitbucketRepo.from_api_dict(resp.json())

    def create_repository(
        self,
        name: str,
        workspace: str | None = None,
        is_private: bool = True,
        description: str | None = None,
    ) -> BitbucketRepo:
        """Cria um novo repositório no Bitbucket."""
        ws = workspace or self.get_default_workspace()
        slug = re.sub(r"[^a-zA-Z0-9_-]", "-", name.strip().lower()).strip("-")
        url = f"{self.base_url}/repositories/{ws}/{slug}"

        payload: dict[str, Any] = {
            "name": name,
            "is_private": is_private,
        }
        if description:
            payload["description"] = description

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=self._get_headers(), json=payload)
            self._handle_response_error(resp, f"criar repositório '{slug}' em '{ws}'")
            return BitbucketRepo.from_api_dict(resp.json())

    def list_commits(
        self,
        repo_slug: str,
        workspace: str | None = None,
        author: str | None = None,
        query: str | None = None,
        limit: int = 20,
    ) -> list[BitbucketCommit]:
        """Consulta o histórico de commits de um repositório."""
        ws = workspace or self.get_default_workspace()
        url = f"{self.base_url}/repositories/{ws}/{repo_slug}/commits"
        params: dict[str, Any] = {"pagelen": max(limit, 20)}

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers(), params=params)
            self._handle_response_error(resp, f"commits de '{ws}/{repo_slug}'")
            data = resp.json()
            commits: list[BitbucketCommit] = []
            for item in data.get("values", []):
                if isinstance(item, dict):
                    commit = BitbucketCommit.from_api_dict(item)
                    if author and author.lower() not in commit.author.author_name.lower():
                        continue
                    if query and query.lower() not in commit.message.lower():
                        continue
                    commits.append(commit)
                    if len(commits) >= limit:
                        break
            return commits

    def get_commit(self, repo_slug: str, sha: str, workspace: str | None = None) -> BitbucketCommit:
        """Obtém os detalhes de um commit específico pelo hash/SHA."""
        ws = workspace or self.get_default_workspace()
        url = f"{self.base_url}/repositories/{ws}/{repo_slug}/commit/{sha}"

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers())
            self._handle_response_error(resp, f"commit '{sha}' em '{ws}/{repo_slug}'")
            return BitbucketCommit.from_api_dict(resp.json())
