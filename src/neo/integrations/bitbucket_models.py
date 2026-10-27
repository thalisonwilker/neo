"""Modelos tipados (DTOs) da API do Bitbucket Cloud."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CloneLink(BaseModel):
    """Representa um link de clonagem (SSH ou HTTPS)."""

    name: str
    href: str


class BitbucketRepo(BaseModel):
    """Representa um repositório no Bitbucket Cloud."""

    name: str
    slug: str
    is_private: bool = Field(default=True)
    description: str | None = None
    updated_on: str = ""
    main_branch: str = "main"
    workspace: str = ""
    clone_links: list[CloneLink] = Field(default_factory=list)

    @property
    def ssh_clone_url(self) -> str | None:
        """Retorna a URL de clonagem SSH, se disponível."""
        for link in self.clone_links:
            if link.name.lower() == "ssh":
                return link.href
        return None

    @property
    def https_clone_url(self) -> str | None:
        """Retorna a URL de clonagem HTTPS, se disponível."""
        for link in self.clone_links:
            if link.name.lower() == "https":
                return link.href
        return None

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> BitbucketRepo:
        """Constrói uma instância a partir do payload JSON da API 2.0 do Bitbucket."""
        clone_links: list[CloneLink] = []
        links_data = data.get("links", {})
        for link_obj in links_data.get("clone", []):
            if isinstance(link_obj, dict) and "name" in link_obj and "href" in link_obj:
                clone_links.append(CloneLink(name=link_obj["name"], href=link_obj["href"]))

        main_branch = "main"
        mainbranch_obj = data.get("mainbranch")
        if isinstance(mainbranch_obj, dict) and "name" in mainbranch_obj:
            main_branch = mainbranch_obj["name"]

        workspace_slug = ""
        workspace_obj = data.get("workspace")
        if isinstance(workspace_obj, dict):
            workspace_slug = workspace_obj.get("slug", "")

        return cls(
            name=data.get("name", ""),
            slug=data.get("slug", ""),
            is_private=data.get("is_private", True),
            description=data.get("description"),
            updated_on=data.get("updated_on", ""),
            main_branch=main_branch,
            workspace=workspace_slug,
            clone_links=clone_links,
        )


class BitbucketCommitAuthor(BaseModel):
    """Representa o autor de um commit."""

    raw: str = ""
    display_name: str | None = None

    @property
    def author_name(self) -> str:
        """Extrai o nome do autor do campo raw ou display_name."""
        if self.display_name:
            return self.display_name
        if "<" in self.raw:
            return self.raw.split("<")[0].strip()
        return self.raw.strip() or "Desconhecido"


class BitbucketCommit(BaseModel):
    """Representa um commit no Bitbucket Cloud."""

    hash: str
    message: str = ""
    date: str = ""
    author: BitbucketCommitAuthor = Field(default_factory=BitbucketCommitAuthor)

    @property
    def short_hash(self) -> str:
        """Retorna os 7 primeiros caracteres do hash do commit."""
        return self.hash[:7] if self.hash else ""

    @property
    def summary(self) -> str:
        """Retorna a primeira linha da mensagem de commit."""
        if not self.message:
            return ""
        return self.message.strip().split("\n")[0].strip()

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> BitbucketCommit:
        """Constrói o commit a partir da resposta JSON da API do Bitbucket."""
        author_data = data.get("author", {})
        raw_author = (
            author_data.get("raw", "") if isinstance(author_data, dict) else str(author_data)
        )
        display_name = None
        if isinstance(author_data, dict):
            user_obj = author_data.get("user")
            if isinstance(user_obj, dict):
                display_name = user_obj.get("display_name")

        return cls(
            hash=data.get("hash", ""),
            message=data.get("message", ""),
            date=data.get("date", ""),
            author=BitbucketCommitAuthor(raw=raw_author, display_name=display_name),
        )
