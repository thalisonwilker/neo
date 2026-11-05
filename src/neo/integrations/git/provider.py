"""Contrato comum para provedores Git."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from neo.integrations.git.models import GitCommit, GitRepo, GitWorkspace
from neo.integrations.git.pr_models import PullRequest


@runtime_checkable
class GitProvider(Protocol):
    """Protocolo comum que qualquer provedor Git (Bitbucket, GitHub) deve implementar."""

    def validate_auth(self) -> None: ...

    def list_open_pull_requests(
        self, repo_slug: str, workspace: str | None = None
    ) -> list[PullRequest]: ...

    def list_pr_branches(self, repo_slug: str, workspace: str | None = None) -> list[str]: ...

    def create_pull_request(
        self,
        repo_slug: str,
        source: str,
        destination: str,
        title: str,
        description: str,
        workspace: str | None = None,
    ) -> PullRequest: ...

    def approve_pull_request(
        self,
        repo_slug: str,
        pr_id: int,
        message: str,
        workspace: str | None = None,
    ) -> None: ...

    def decline_pull_request(
        self,
        repo_slug: str,
        pr_id: int,
        workspace: str | None = None,
    ) -> None: ...

    def search_pull_requests(
        self,
        repo_slug: str,
        query: str,
        workspace: str | None = None,
    ) -> list[PullRequest]: ...

    def list_repositories(
        self, workspace: str | None = None, limit: int | None = None
    ) -> list[GitRepo]: ...

    def search_repositories(
        self, query: str, workspace: str | None = None, limit: int | None = None
    ) -> list[GitRepo]: ...

    def get_repository(self, repo_slug: str, workspace: str | None = None) -> GitRepo: ...

    def create_repository(
        self,
        name: str,
        workspace: str | None = None,
        is_private: bool = True,
        description: str | None = None,
    ) -> GitRepo: ...

    def update_repository_description(
        self, repo_slug: str, description: str, workspace: str | None = None
    ) -> GitRepo: ...

    def list_commits(
        self,
        repo_slug: str,
        workspace: str | None = None,
        author: str | None = None,
        query: str | None = None,
        limit: int = 20,
    ) -> list[GitCommit]: ...

    def get_commit(self, repo_slug: str, sha: str, workspace: str | None = None) -> GitCommit: ...

    def list_workspaces(self) -> list[GitWorkspace]: ...

    def get_default_workspace(self, ignore_config: bool = False) -> str: ...
