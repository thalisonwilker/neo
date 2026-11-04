"""Contratos HTTP da alteração de descrição no GitHub e Bitbucket."""

import json

import httpx
import respx

from neo.integrations.bitbucket import BitbucketClient
from neo.integrations.github import GitHubClient


@respx.mock
def test_github_update_description():
    route = respx.patch("https://api.github.com/repos/acme/demo").mock(
        return_value=httpx.Response(200, json={"name": "demo", "description": "Nova"})
    )
    repo = GitHubClient("secret").update_repository_description("demo", "Nova", workspace="acme")
    assert repo.description == "Nova"
    assert json.loads(route.calls.last.request.content) == {"description": "Nova"}


@respx.mock
def test_bitbucket_update_description():
    respx.get("https://api.bitbucket.org/2.0/repositories/acme/demo").mock(
        return_value=httpx.Response(200, json={"name": "demo", "slug": "demo"})
    )
    route = respx.put("https://api.bitbucket.org/2.0/repositories/acme/demo").mock(
        return_value=httpx.Response(
            200, json={"name": "demo", "slug": "demo", "description": "Nova"}
        )
    )
    repo = BitbucketClient("secret").update_repository_description("demo", "Nova", workspace="acme")
    assert repo.description == "Nova"
    assert json.loads(route.calls.last.request.content) == {"description": "Nova"}
