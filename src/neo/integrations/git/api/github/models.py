"""Modelos tipados (DTOs) da API REST v3 do GitHub."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from neo.integrations.git.models import (
    CloneLink,
    GitCommit,
    GitCommitAuthor,
    GitRepo,
    GitWorkspace,
)

# Aliases de domínio para compatibilidade semântica
GitHubRepo = GitRepo
GitHubCommit = GitCommit
GitHubWorkspace = GitWorkspace


class GitHubUser(BaseModel):
    """Representa um usuário autenticado no GitHub."""

    id: int
    login: str
    name: str | None = None
    email: str | None = None


def parse_github_repo(data: dict[str, Any]) -> GitRepo:
    """Converte payload JSON de repositório do GitHub em GitRepo."""
    clone_links = [
        CloneLink(name="https", href=data.get("clone_url", "")),
        CloneLink(name="ssh", href=data.get("ssh_url", "")),
    ]

    owner_obj = data.get("owner", {})
    owner_slug = owner_obj.get("login", "") if isinstance(owner_obj, dict) else ""

    return GitRepo(
        name=data.get("name", ""),
        slug=data.get("name", ""),
        is_private=data.get("private", True),
        description=data.get("description"),
        created_on=data.get("created_at", ""),
        updated_on=data.get("updated_at", ""),
        main_branch=data.get("default_branch", "main"),
        workspace=owner_slug,
        web_url=data.get("html_url", ""),
        clone_links=clone_links,
    )


def parse_github_commit(data: dict[str, Any]) -> GitCommit:
    """Converte payload JSON de commit do GitHub em GitCommit."""
    commit_obj = data.get("commit", {})
    author_obj = commit_obj.get("author", {}) if isinstance(commit_obj, dict) else {}

    author_name = author_obj.get("name", "") if isinstance(author_obj, dict) else ""
    author_email = author_obj.get("email", "") if isinstance(author_obj, dict) else ""
    raw_author = f"{author_name} <{author_email}>" if author_email else author_name
    date_str = author_obj.get("date", "") if isinstance(author_obj, dict) else ""
    message_str = commit_obj.get("message", "") if isinstance(commit_obj, dict) else ""

    return GitCommit(
        hash=data.get("sha", ""),
        message=message_str,
        date=date_str,
        web_url=data.get("html_url", ""),
        author=GitCommitAuthor(raw=raw_author, display_name=author_name or None),
    )
