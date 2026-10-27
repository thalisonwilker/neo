"""Modelos tipados (DTOs) da API REST v3 do GitHub."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from neo.integrations.bitbucket_models import (
    BitbucketCommit,
    BitbucketCommitAuthor,
    BitbucketRepo,
    BitbucketWorkspace,
    CloneLink,
)

# Aliases de domínio para compatibilidade semântica
GitHubRepo = BitbucketRepo
GitHubCommit = BitbucketCommit
GitHubWorkspace = BitbucketWorkspace


class GitHubUser(BaseModel):
    """Representa um usuário autenticado no GitHub."""

    id: int
    login: str
    name: str | None = None
    email: str | None = None


def parse_github_repo(data: dict[str, Any]) -> BitbucketRepo:
    """Converte payload JSON de repositório do GitHub em BitbucketRepo."""
    clone_links = [
        CloneLink(name="https", href=data.get("clone_url", "")),
        CloneLink(name="ssh", href=data.get("ssh_url", "")),
    ]

    owner_obj = data.get("owner", {})
    owner_slug = owner_obj.get("login", "") if isinstance(owner_obj, dict) else ""

    return BitbucketRepo(
        name=data.get("name", ""),
        slug=data.get("name", ""),
        is_private=data.get("private", True),
        description=data.get("description"),
        updated_on=data.get("updated_at", ""),
        main_branch=data.get("default_branch", "main"),
        workspace=owner_slug,
        clone_links=clone_links,
    )


def parse_github_commit(data: dict[str, Any]) -> BitbucketCommit:
    """Converte payload JSON de commit do GitHub em BitbucketCommit."""
    commit_obj = data.get("commit", {})
    author_obj = commit_obj.get("author", {}) if isinstance(commit_obj, dict) else {}

    raw_author = author_obj.get("name", "") if isinstance(author_obj, dict) else ""
    date_str = author_obj.get("date", "") if isinstance(author_obj, dict) else ""
    message_str = commit_obj.get("message", "") if isinstance(commit_obj, dict) else ""

    return BitbucketCommit(
        hash=data.get("sha", ""),
        message=message_str,
        date=date_str,
        author=BitbucketCommitAuthor(raw=raw_author, display_name=raw_author),
    )
