"""Testes unitários para o GitHubClient usando respx."""

import httpx
import pytest
import respx

from neo.integrations.github import (
    GitHubAuthError,
    GitHubClient,
    GitHubNotFoundError,
)


@pytest.fixture
def gh_client():
    return GitHubClient(token="ghp_mock_token", base_url="https://api.github.com")


MOCK_USER_PAYLOAD = {
    "id": 12345,
    "login": "octocat",
    "name": "The Octocat",
    "email": "octocat@github.com",
}


@respx.mock
def test_get_current_user(gh_client: GitHubClient):
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json=MOCK_USER_PAYLOAD)
    )

    user = gh_client.get_current_user()
    assert user.login == "octocat"
    assert user.name == "The Octocat"
    assert user.id == 12345


@respx.mock
def test_list_workspaces(gh_client: GitHubClient):
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json=MOCK_USER_PAYLOAD)
    )
    respx.get("https://api.github.com/user/orgs").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"id": 999, "login": "my-org"},
            ],
        )
    )

    workspaces = gh_client.list_workspaces()
    assert len(workspaces) == 2
    assert workspaces[0].slug == "octocat"
    assert workspaces[0].is_admin is True
    assert workspaces[1].slug == "my-org"
    assert workspaces[1].is_admin is False


@respx.mock
def test_list_repositories(gh_client: GitHubClient):
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json=MOCK_USER_PAYLOAD)
    )
    respx.get("https://api.github.com/user/repos").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "name": "Hello-World",
                    "private": False,
                    "description": "Meu repositório",
                    "default_branch": "main",
                    "updated_at": "2026-10-27T10:00:00Z",
                    "clone_url": "https://github.com/octocat/Hello-World.git",
                    "ssh_url": "git@github.com:octocat/Hello-World.git",
                    "owner": {"login": "octocat"},
                }
            ],
        )
    )

    repos = gh_client.list_repositories()
    assert len(repos) == 1
    assert repos[0].name == "Hello-World"
    assert repos[0].is_private is False
    assert repos[0].https_clone_url == "https://github.com/octocat/Hello-World.git"
    assert repos[0].ssh_clone_url == "git@github.com:octocat/Hello-World.git"


@respx.mock
def test_create_and_get_repository(gh_client: GitHubClient):
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(200, json=MOCK_USER_PAYLOAD)
    )
    respx.post("https://api.github.com/user/repos").mock(
        return_value=httpx.Response(
            201,
            json={
                "name": "novo-repo",
                "private": True,
                "description": "Desc",
                "default_branch": "main",
                "updated_at": "2026-10-27T10:00:00Z",
                "clone_url": "https://github.com/octocat/novo-repo.git",
                "ssh_url": "git@github.com:octocat/novo-repo.git",
                "owner": {"login": "octocat"},
            },
        )
    )
    respx.get("https://api.github.com/repos/octocat/novo-repo").mock(
        return_value=httpx.Response(
            200,
            json={
                "name": "novo-repo",
                "private": True,
                "description": "Desc",
                "default_branch": "main",
                "updated_at": "2026-10-27T10:00:00Z",
                "clone_url": "https://github.com/octocat/novo-repo.git",
                "ssh_url": "git@github.com:octocat/novo-repo.git",
                "owner": {"login": "octocat"},
            },
        )
    )

    created = gh_client.create_repository("novo-repo", is_private=True, description="Desc")
    assert created.name == "novo-repo"

    retrieved = gh_client.get_repository("novo-repo", workspace="octocat")
    assert retrieved.name == "novo-repo"


@respx.mock
def test_list_commits(gh_client: GitHubClient):
    respx.get("https://api.github.com/repos/octocat/Hello-World/commits").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
                    "commit": {
                        "message": "fix: resolve timeout bug\n\nDetalhes",
                        "author": {
                            "name": "Monalisa Octocat",
                            "date": "2026-10-27T12:00:00Z",
                        },
                    },
                }
            ],
        )
    )

    commits = gh_client.list_commits("Hello-World", workspace="octocat")
    assert len(commits) == 1
    assert commits[0].short_hash == "6dcb09b"
    assert commits[0].summary == "fix: resolve timeout bug"
    assert commits[0].author.author_name == "Monalisa Octocat"


@respx.mock
def test_get_commit_github(gh_client: GitHubClient):
    """AC-6 (0014): get_commit individual no GitHub."""
    respx.get("https://api.github.com/repos/octocat/Hello-World/commits/6dcb09b").mock(
        return_value=httpx.Response(
            200,
            json={
                "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
                "html_url": "https://github.com/octocat/Hello-World/commit/6dcb09b",
                "commit": {
                    "message": "fix: resolve timeout bug\n\nDetalhes",
                    "author": {
                        "name": "Monalisa Octocat",
                        "email": "octocat@github.com",
                        "date": "2026-10-27T12:00:00Z",
                    },
                },
            },
        )
    )
    c = gh_client.get_commit("Hello-World", "6dcb09b", workspace="octocat")
    assert c.short_hash == "6dcb09b"
    assert c.web_url == "https://github.com/octocat/Hello-World/commit/6dcb09b"
    assert "octocat@github.com" in c.author.raw


@respx.mock
def test_github_error_handling(gh_client: GitHubClient):
    respx.get("https://api.github.com/user").mock(
        return_value=httpx.Response(401, json={"message": "Bad credentials"})
    )
    with pytest.raises(GitHubAuthError, match="Falha de autenticação no GitHub"):
        gh_client.get_current_user()

    respx.get("https://api.github.com/repos/octocat/inexistente").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )
    with pytest.raises(GitHubNotFoundError):
        gh_client.get_repository("inexistente", workspace="octocat")
