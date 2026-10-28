import httpx
import pytest
import respx

from neo.integrations.bitbucket import (
    BitbucketAuthError,
    BitbucketClient,
    BitbucketNotFoundError,
)
from neo.integrations.bitbucket_models import BitbucketCommit, BitbucketRepo


@pytest.fixture
def bb_client():
    return BitbucketClient(token="mock-token", base_url="https://api.bitbucket.org/2.0")


@respx.mock
def test_list_repositories(bb_client: BitbucketClient):
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "name": "Repo One",
                        "slug": "repo-one",
                        "is_private": True,
                        "description": "Primary backend",
                        "updated_on": "2026-10-27T10:00:00Z",
                        "mainbranch": {"name": "main"},
                        "links": {
                            "clone": [
                                {
                                    "name": "ssh",
                                    "href": "git@bitbucket.org:my-workspace/repo-one.git",
                                },
                                {
                                    "name": "https",
                                    "href": "https://bitbucket.org/my-workspace/repo-one.git",
                                },
                            ]
                        },
                    }
                ]
            },
        )
    )

    repos = bb_client.list_repositories(workspace="my-workspace")
    assert len(repos) == 1
    assert isinstance(repos[0], BitbucketRepo)
    assert repos[0].name == "Repo One"
    assert repos[0].slug == "repo-one"
    assert repos[0].ssh_clone_url == "git@bitbucket.org:my-workspace/repo-one.git"
    assert repos[0].https_clone_url == "https://bitbucket.org/my-workspace/repo-one.git"


@respx.mock
def test_search_repositories(bb_client: BitbucketClient):
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {"name": "Frontend App", "slug": "frontend-app", "is_private": False},
                    {
                        "name": "Backend API",
                        "slug": "backend-api",
                        "is_private": True,
                        "description": "Core API",
                    },
                ]
            },
        )
    )

    results = bb_client.search_repositories(query="backend", workspace="my-workspace")
    assert len(results) == 1
    assert results[0].slug == "backend-api"


@respx.mock
def test_get_repository_not_found(bb_client: BitbucketClient):
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace/repo-inexistente").mock(
        return_value=httpx.Response(404, json={"error": {"message": "Repository not found"}})
    )

    with pytest.raises(BitbucketNotFoundError, match="não foi encontrado"):
        bb_client.get_repository(repo_slug="repo-inexistente", workspace="my-workspace")


@respx.mock
def test_auth_error_401(bb_client: BitbucketClient):
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        return_value=httpx.Response(401, json={"error": {"message": "Invalid token"}})
    )

    with pytest.raises(BitbucketAuthError, match="Falha de autenticação"):
        bb_client.list_repositories(workspace="my-workspace")


@respx.mock
def test_create_repository(bb_client: BitbucketClient):
    respx.post("https://api.bitbucket.org/2.0/repositories/my-workspace/new-repo").mock(
        return_value=httpx.Response(
            201,
            json={
                "name": "New Repo",
                "slug": "new-repo",
                "is_private": True,
                "description": "Criado via Neo CLI",
            },
        )
    )

    repo = bb_client.create_repository(
        name="New Repo",
        workspace="my-workspace",
        is_private=True,
        description="Criado via Neo CLI",
    )
    assert repo.slug == "new-repo"
    assert repo.is_private is True


@respx.mock
def test_list_commits(bb_client: BitbucketClient):
    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace/my-repo/commits").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "hash": "1234567890abcdef",
                        "message": "feat: adiciona login\n\nDetalhes do commit",
                        "date": "2026-10-27T12:00:00Z",
                        "author": {"raw": "Thalyson <thalyson@exemplo.com>"},
                    }
                ]
            },
        )
    )

    commits = bb_client.list_commits(repo_slug="my-repo", workspace="my-workspace")
    assert len(commits) == 1
    assert isinstance(commits[0], BitbucketCommit)
    assert commits[0].short_hash == "1234567"
    assert commits[0].summary == "feat: adiciona login"
    assert commits[0].author.author_name == "Thalyson"


@respx.mock
def test_get_commit_and_pagination(bb_client: BitbucketClient):
    """AC-5 e AC-6 (0014): get_commit individual e paginação em list_repositories."""
    respx.get(
        "https://api.bitbucket.org/2.0/repositories/my-workspace/my-repo/commit/1234567"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "hash": "1234567890abcdef",
                "message": "feat: detalhe de commit",
                "date": "2026-10-27T12:00:00Z",
                "author": {"raw": "Thalyson <thalyson@exemplo.com>"},
                "links": {
                    "html": {"href": "https://bitbucket.org/my-workspace/my-repo/commits/1234567"}
                },
            },
        )
    )
    commit = bb_client.get_commit(repo_slug="my-repo", sha="1234567", workspace="my-workspace")
    assert commit.hash == "1234567890abcdef"
    assert commit.web_url == "https://bitbucket.org/my-workspace/my-repo/commits/1234567"

    respx.get("https://api.bitbucket.org/2.0/repositories/my-workspace").mock(
        side_effect=[
            httpx.Response(
                200,
                json={
                    "values": [{"name": "R1", "slug": "r1", "is_private": True}],
                    "next": "https://api.bitbucket.org/2.0/repositories/my-workspace?page=2",
                },
            ),
            httpx.Response(
                200,
                json={"values": [{"name": "R2", "slug": "r2", "is_private": False}]},
            ),
        ]
    )
    repos = bb_client.list_repositories(workspace="my-workspace")
    assert [r.slug for r in repos] == ["r1", "r2"]


@respx.mock
def test_list_workspaces(bb_client: BitbucketClient):
    from neo.integrations.bitbucket_models import BitbucketWorkspace

    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "type": "workspace_access",
                        "administrator": True,
                        "workspace": {
                            "name": "Acme Corp",
                            "slug": "acme_corp",
                            "uuid": "{f39a5585-9c5e-4ff5-a3c3-f799032772f2}",
                        },
                    }
                ]
            },
        )
    )

    workspaces = bb_client.list_workspaces()
    assert len(workspaces) == 1
    assert isinstance(workspaces[0], BitbucketWorkspace)
    assert workspaces[0].name == "Acme Corp"
    assert workspaces[0].slug == "acme_corp"
    assert workspaces[0].is_admin is True


@respx.mock
def test_get_default_workspace_precedence(bb_client: BitbucketClient):
    from unittest.mock import patch

    # 1. Com config salvo
    with patch("neo.config.get_default_workspace_config", return_value="configured-ws"):
        ws = bb_client.get_default_workspace()
        assert ws == "configured-ws"

    # 2. Sem config salvo (fallback para API)
    respx.get("https://api.bitbucket.org/2.0/user/workspaces").mock(
        return_value=httpx.Response(
            200,
            json={
                "values": [
                    {
                        "workspace": {
                            "name": "Auto WS",
                            "slug": "auto-ws",
                        }
                    }
                ]
            },
        )
    )
    with patch("neo.config.get_default_workspace_config", return_value=None):
        ws = bb_client.get_default_workspace()
        assert ws == "auto-ws"
