"""Representação compartilhada de pull requests entre provedores Git."""

from pydantic import BaseModel


class PullRequest(BaseModel):
    """Pull request normalizado para a CLI."""

    id: int
    title: str
    state: str
    source: str
    destination: str
    url: str
