"""Cliente HTTP para comunicação com a REST API v3 do GitHub."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote, urljoin, urlsplit

import httpx

from neo.config import get_default_workspace_config
from neo.integrations.git.api.github.models import (
    GitHubUser,
    parse_github_commit,
    parse_github_repo,
)
from neo.integrations.git.errors import (
    GitProviderAuthError,
    GitProviderError,
    GitProviderNotFoundError,
    GitProviderRateLimitError,
    UnsupportedProviderOperationError,
)
from neo.integrations.git.models import (
    GitCommit,
    GitRepo,
    GitWorkspace,
)
from neo.integrations.git.pr_models import PullRequest

logger = logging.getLogger(__name__)

# Exceções especializadas com herança compatível
GitHubError = GitProviderError
GitHubAuthError = GitProviderAuthError
GitHubNotFoundError = GitProviderNotFoundError
GitHubRateLimitError = GitProviderRateLimitError
GitHubUnsupportedError = UnsupportedProviderOperationError


class GitHubClient:
    """Cliente para interagir com a API do GitHub."""

    def validate_auth(self) -> None:
        """Valida a credencial consultando o usuário autenticado."""
        self.get_current_user()

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
                "Execute `neo git config set api-key` para atualizar seu Personal Access Token."
            )
        if response.status_code == 403:
            if "rate limit" in response.text.lower():
                raise GitHubRateLimitError(f"Limite de requisições atingido no GitHub ({context}).")
            raise GitHubAuthError(
                f"Acesso negado no GitHub (403 em {context}). "
                "Verifique os escopos do seu Personal Access Token com `neo git config set api-key`."
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

    def list_workspaces(self) -> list[GitWorkspace]:
        """Lista as organizações acessíveis e a conta pessoal do usuário."""
        user = self.get_current_user()
        workspaces: list[GitWorkspace] = [
            GitWorkspace(
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
                        GitWorkspace(
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

    def list_repositories(
        self, workspace: str | None = None, limit: int | None = None
    ) -> list[GitRepo]:
        """Lista os repositórios do usuário ou organização."""
        target_ws = workspace or self.get_default_workspace()
        user = self.get_current_user()

        repos: list[GitRepo] = []
        with httpx.Client(timeout=self.timeout) as client:
            if target_ws.lower() == user.login.lower():
                url = f"{self.base_url}/user/repos"
                params: dict[str, Any] = {
                    "affiliation": "owner,collaborator,organization_member",
                    "sort": "updated",
                    "per_page": 100,
                }
                resp = client.get(url, headers=self._get_headers(), params=params)
            else:
                url = f"{self.base_url}/orgs/{target_ws}/repos"
                params = {"sort": "updated", "per_page": 100}
                resp = client.get(url, headers=self._get_headers(), params=params)

            self._handle_response_error(resp, f"repositórios de '{target_ws}'")
            for item in resp.json():
                if isinstance(item, dict):
                    repos.append(parse_github_repo(item))
                    if limit is not None and len(repos) >= limit:
                        return repos[:limit]

        return repos

    def search_repositories(
        self, query: str, workspace: str | None = None, limit: int | None = None
    ) -> list[GitRepo]:
        """Pesquisa repositórios pelo nome, slug ou descrição."""
        all_repos = self.list_repositories(workspace=workspace)
        q = query.strip().lower()
        matched: list[GitRepo] = []
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

    def get_repository(self, repo_slug: str, workspace: str | None = None) -> GitRepo:
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
    ) -> GitRepo:
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

    def update_repository_description(
        self, repo_slug: str, description: str, workspace: str | None = None
    ) -> GitRepo:
        """Atualiza a descrição do repositório no GitHub."""
        ws = workspace or self.get_default_workspace()
        url = f"{self.base_url}/repos/{ws}/{repo_slug}"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.patch(url, headers=self._get_headers(), json={"description": description})
            self._handle_response_error(resp, f"atualizar descrição de '{ws}/{repo_slug}'")
            return parse_github_repo(resp.json())

    def _pr_base(self, repo_slug: str, workspace: str | None) -> str:
        ws = workspace or self.get_default_workspace()
        return f"{self.base_url}/repos/{quote(ws, safe='')}/{quote(repo_slug, safe='')}"

    @staticmethod
    def _parse_pull_request(data: dict[str, Any]) -> PullRequest:
        state = str(data.get("state", "")).lower()
        normalized = (
            "OPEN" if state == "open" else "MERGED" if data.get("merged_at") else "DECLINED"
        )
        return PullRequest(
            id=data["number"],
            title=data["title"],
            state=normalized,
            source=data["head"]["ref"],
            destination=data["base"]["ref"],
            url=data.get("html_url", ""),
        )

    def _get_paginated(self, url: str, params: dict[str, str | int]) -> list[dict[str, Any]]:
        """Segue todas as páginas, sem enviar credenciais para uma origem diferente."""
        result: list[dict[str, Any]] = []
        visited: set[str] = set()
        origin = urlsplit(self.base_url)
        next_url: str | None = url
        with httpx.Client(timeout=self.timeout) as client:
            while next_url:
                if next_url in visited:
                    raise GitHubError("A paginação do GitHub contém um ciclo.")
                visited.add(next_url)
                resp = client.get(next_url, headers=self._get_headers(), params=params or None)
                self._handle_response_error(resp, "consultar pull requests ou branches")
                payload = resp.json()
                if not isinstance(payload, list):
                    raise GitHubError("Resposta inválida do GitHub ao consultar resultados.")
                result.extend(item for item in payload if isinstance(item, dict))
                raw_next = resp.links.get("next", {}).get("url")
                if raw_next:
                    resolved = urljoin(str(resp.url), raw_next)
                    parsed = urlsplit(resolved)
                    if (parsed.scheme, parsed.netloc) != (origin.scheme, origin.netloc):
                        raise GitHubError("O GitHub retornou uma página de origem inválida.")
                    next_url = resolved
                else:
                    next_url = None
                params = {}
        return result

    def list_pr_branches(self, repo_slug: str, workspace: str | None = None) -> list[str]:
        """Lista todas as branches remotas usadas na escolha da branch de destino."""
        url = f"{self._pr_base(repo_slug, workspace)}/branches"
        return [str(item["name"]) for item in self._get_paginated(url, {"per_page": 100})]

    def list_open_pull_requests(
        self, repo_slug: str, workspace: str | None = None
    ) -> list[PullRequest]:
        """Lista PRs abertos em todas as páginas."""
        url = f"{self._pr_base(repo_slug, workspace)}/pulls"
        return [
            self._parse_pull_request(item)
            for item in self._get_paginated(url, {"state": "open", "per_page": 100})
        ]

    def create_pull_request(
        self,
        repo_slug: str,
        source: str,
        destination: str,
        title: str,
        description: str,
        workspace: str | None = None,
    ) -> PullRequest:
        """Abre PR a partir de uma branch existente no remoto."""
        url = f"{self._pr_base(repo_slug, workspace)}/pulls"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url,
                headers=self._get_headers(),
                json={"head": source, "base": destination, "title": title, "body": description},
            )
            self._handle_response_error(resp, "abrir pull request")
            return self._parse_pull_request(resp.json())

    def approve_pull_request(
        self, repo_slug: str, pr_id: int, message: str, workspace: str | None = None
    ) -> None:
        """Envia aprovação e mensagem em uma única revisão."""
        url = f"{self._pr_base(repo_slug, workspace)}/pulls/{pr_id}/reviews"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(
                url, headers=self._get_headers(), json={"event": "APPROVE", "body": message}
            )
            self._handle_response_error(resp, "aprovar pull request")

    def decline_pull_request(
        self, repo_slug: str, pr_id: int, workspace: str | None = None
    ) -> None:
        """Fecha um PR sem fazer merge."""
        url = f"{self._pr_base(repo_slug, workspace)}/pulls/{pr_id}"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.patch(url, headers=self._get_headers(), json={"state": "closed"})
            self._handle_response_error(resp, "recusar pull request")

    def search_pull_requests(
        self, repo_slug: str, query: str, workspace: str | None = None
    ) -> list[PullRequest]:
        """Busca por ID exato ou trecho de título, incluindo todas as páginas e estados."""
        base = f"{self._pr_base(repo_slug, workspace)}/pulls"
        if query.isdecimal():
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.get(f"{base}/{int(query)}", headers=self._get_headers())
                if resp.status_code == 404:
                    return []
                self._handle_response_error(resp, "buscar pull request")
                return [self._parse_pull_request(resp.json())]
        search = query.casefold()
        return [
            self._parse_pull_request(item)
            for item in self._get_paginated(base, {"state": "all", "per_page": 100})
            if search in str(item.get("title", "")).casefold()
        ]

    def list_commits(
        self,
        repo_slug: str,
        workspace: str | None = None,
        author: str | None = None,
        query: str | None = None,
        limit: int = 20,
    ) -> list[GitCommit]:
        """Lista histórico de commits no GitHub."""
        ws = workspace or self.get_default_workspace()
        url = f"{self.base_url}/repos/{ws}/{repo_slug}/commits"
        params: dict[str, Any] = {"per_page": max(limit, 20)}
        if author:
            params["author"] = author

        commits: list[GitCommit] = []
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers(), params=params)
            self._handle_response_error(resp, f"commits de '{ws}/{repo_slug}'")
            for item in resp.json():
                if isinstance(item, dict):
                    c = parse_github_commit(item)
                    if query and query.lower() not in c.message.lower():
                        continue
                    commits.append(c)
                    if len(commits) >= limit:
                        break

        return commits

    def get_commit(self, repo_slug: str, sha: str, workspace: str | None = None) -> GitCommit:
        """Obtém os detalhes de um commit específico pelo hash/SHA no GitHub."""
        ws = workspace or self.get_default_workspace()
        url = f"{self.base_url}/repos/{ws}/{repo_slug}/commits/{sha}"

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(url, headers=self._get_headers())
            self._handle_response_error(resp, f"commit '{sha}' em '{ws}/{repo_slug}'")
            return parse_github_commit(resp.json())
