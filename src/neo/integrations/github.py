"""Cliente HTTP para comunicação com a REST API v3 do GitHub."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from neo.config import get_default_workspace_config
from neo.integrations.bitbucket import (
    BitbucketAuthError,
    BitbucketError,
    BitbucketNotFoundError,
    BitbucketRateLimitError,
)
from neo.integrations.bitbucket_models import (
    BitbucketCommit,
    BitbucketRepo,
    BitbucketWorkspace,
)
from neo.integrations.github_models import (
    GitHubUser,
    parse_github_commit,
    parse_github_repo,
)

logger = logging.getLogger(__name__)

# Exceções especializadas com herança compatível
GitHubError = BitbucketError
GitHubAuthError = BitbucketAuthError
GitHubNotFoundError = BitbucketNotFoundError
GitHubRateLimitError = BitbucketRateLimitError


class GitHubClient:
    """Cliente para interagir com a API do GitHub."""

    def __init__(
        self,
        token: str,
        base_url: str = "https://api.github.com",
        timeout: float = 15.0,
    ) -> None:
        self.token = token.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _handle_response_error(self, response: httpx.Response, context: str) -> None:
        """Trata códigos de status HTTP e traduz para exceções de domínio."""
        if response.status_code == 401:
            raise GitHubAuthError(
                "Falha de autenticação no GitHub (401). "
                "Verifique seu token executando `neo git config auth set github`."
            )
        if response.status_code == 403:
            raise GitHubRateLimitError(
                f"Acesso negado ou limite de requisições atingido no GitHub ({context})."
            )
        if response.status_code == 404:
            raise GitHubNotFoundError(
                f"O recurso solicitado em {context} não foi encontrado no GitHub (404)."
            )
        if response.is_error:
            try:
                err_data = response.json()
                msg = err_data.get("message", response.text)
            except (ValueError, KeyError):
                msg = response.text
            raise GitHubError(f"Erro na API do GitHub ({response.status_code}): {msg}")

    def get_current_user(self) -> GitHubUser:
        """Obtém dados do usuário autenticado no GitHub."""
        url = f"{self.base_url}/user"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers())
            self._handle_response_error(resp, "obter usuário autenticado")
            data = resp.json()
            return GitHubUser(
                id=data["id"],
                login=data["login"],
                name=data.get("name"),
                email=data.get("email"),
            )

    def list_workspaces(self) -> list[BitbucketWorkspace]:
        """Lista as organizações acessíveis e a conta pessoal do usuário."""
        user = self.get_current_user()
        workspaces: list[BitbucketWorkspace] = [
            BitbucketWorkspace(
                uuid=str(user.id),
                name=user.name or user.login,
                slug=user.login,
                is_admin=True,
            )
        ]

        url = f"{self.base_url}/user/orgs"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers())
            if resp.status_code == 200:
                for org in resp.json():
                    workspaces.append(
                        BitbucketWorkspace(
                            uuid=str(org.get("id", "")),
                            name=org.get("login", ""),
                            slug=org.get("login", ""),
                            is_admin=False,
                        )
                    )

        return workspaces

    def get_default_workspace(self, ignore_config: bool = False) -> str:
        """Retorna o owner/organização padrão (respeitando config local ou conta pessoal)."""
        if not ignore_config:
            cfg_ws = get_default_workspace_config(provider="github")
            if cfg_ws:
                return cfg_ws

        user = self.get_current_user()
        return user.login

    def list_repositories(self, workspace: str | None = None) -> list[BitbucketRepo]:
        """Lista os repositórios do usuário ou organização."""
        target_ws = workspace or self.get_default_workspace()
        user = self.get_current_user()

        repos: list[BitbucketRepo] = []
        with httpx.Client(timeout=self.timeout) as client:
            if target_ws.lower() == user.login.lower():
                url = f"{self.base_url}/user/repos"
                params = {
                    "affiliation": "owner,collaborator,organization_member",
                    "sort": "updated",
                }
                resp = client.get(url, headers=self._get_headers(), params=params)
            else:
                url = f"{self.base_url}/orgs/{target_ws}/repos"
                params = {"sort": "updated"}
                resp = client.get(url, headers=self._get_headers(), params=params)

            self._handle_response_error(resp, f"repositórios de '{target_ws}'")
            for item in resp.json():
                if isinstance(item, dict):
                    repos.append(parse_github_repo(item))

        return repos

    def search_repositories(self, query: str, workspace: str | None = None) -> list[BitbucketRepo]:
        """Pesquisa repositórios pelo nome ou descrição."""
        all_repos = self.list_repositories(workspace=workspace)
        q = query.strip().lower()
        matched: list[BitbucketRepo] = []
        for r in all_repos:
            if q in r.name.lower() or (r.description and q in r.description.lower()):
                matched.append(r)
        return matched

    def get_repository(self, repo_slug: str, workspace: str | None = None) -> BitbucketRepo:
        """Obtém detalhes de um repositório no GitHub."""
        ws = workspace or self.get_default_workspace()
        url = f"{self.base_url}/repos/{ws}/{repo_slug}"

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers())
            self._handle_response_error(resp, f"repositório '{ws}/{repo_slug}'")
            return parse_github_repo(resp.json())

    def create_repository(
        self,
        name: str,
        workspace: str | None = None,
        is_private: bool = True,
        description: str | None = None,
    ) -> BitbucketRepo:
        """Cria um repositório na conta pessoal ou organização no GitHub."""
        target_ws = workspace or self.get_default_workspace()
        user = self.get_current_user()

        payload: dict[str, Any] = {
            "name": name,
            "private": is_private,
        }
        if description:
            payload["description"] = description

        with httpx.Client(timeout=self.timeout) as client:
            if target_ws.lower() == user.login.lower():
                url = f"{self.base_url}/user/repos"
            else:
                url = f"{self.base_url}/orgs/{target_ws}/repos"

            resp = client.post(url, headers=self._get_headers(), json=payload)
            self._handle_response_error(resp, f"criar repositório '{name}' em '{target_ws}'")
            return parse_github_repo(resp.json())

    def list_commits(
        self,
        repo_slug: str,
        workspace: str | None = None,
        author: str | None = None,
        query: str | None = None,
        limit: int = 20,
    ) -> list[BitbucketCommit]:
        """Lista histórico de commits no GitHub."""
        ws = workspace or self.get_default_workspace()
        url = f"{self.base_url}/repos/{ws}/{repo_slug}/commits"
        params: dict[str, Any] = {"per_page": limit}
        if author:
            params["author"] = author

        commits: list[BitbucketCommit] = []
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers(), params=params)
            self._handle_response_error(resp, f"commits de '{ws}/{repo_slug}'")
            for item in resp.json():
                if isinstance(item, dict):
                    c = parse_github_commit(item)
                    if query and query.lower() not in c.message.lower():
                        continue
                    commits.append(c)

        return commits
