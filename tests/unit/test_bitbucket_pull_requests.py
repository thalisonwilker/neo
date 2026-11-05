"""Operações de pull request no Bitbucket Cloud, com API simulada."""

import json

import httpx
import pytest
import respx

from neo.integrations.git.api.bitbucket.client import BitbucketClient, BitbucketError

BASE = "https://api.bitbucket.org/2.0/repositories/acme/demo"


def pull_request(pr_id: int, title: str, state: str = "OPEN") -> dict:
    return {
        "id": pr_id,
        "title": title,
        "state": state,
        "source": {"branch": {"name": "feature"}},
        "destination": {"branch": {"name": "main"}},
        "links": {"html": {"href": f"https://bitbucket.org/acme/demo/pull-requests/{pr_id}"}},
    }


@respx.mock
def test_AC_5_list_open_pull_requests_paginated():
    route = respx.get(f"{BASE}/pullrequests").mock(
        side_effect=[
            httpx.Response(
                200,
                json={"values": [pull_request(1, "First")], "next": f"{BASE}/pullrequests?page=2"},
            ),
            httpx.Response(200, json={"values": [pull_request(2, "Second")]}),
        ]
    )
    result = BitbucketClient("secret").list_open_pull_requests("demo", "acme")
    assert [pr.id for pr in result] == [1, 2]
    assert route.calls[0].request.url.params["state"] == "OPEN"


@respx.mock
def test_branches_and_search_follow_pages():
    client = BitbucketClient("secret")
    respx.get(f"{BASE}/refs/branches", params={"page": "2"}).mock(
        return_value=httpx.Response(200, json={"values": [{"name": "release"}]})
    )
    respx.get(f"{BASE}/refs/branches").mock(
        return_value=httpx.Response(
            200, json={"values": [{"name": "main"}], "next": f"{BASE}/refs/branches?page=2"}
        )
    )
    assert client.list_pr_branches("demo", "acme") == ["main", "release"]

    respx.get(f"{BASE}/pullrequests", params={"state": ["OPEN", "MERGED", "DECLINED"]}).mock(
        return_value=httpx.Response(
            200, json={"values": [pull_request(1, "Other")], "next": f"{BASE}/pullrequests?page=2"}
        )
    )
    respx.get(f"{BASE}/pullrequests", params={"page": "2"}).mock(
        return_value=httpx.Response(
            200, json={"values": [pull_request(2, "Fix important bug", "MERGED")]}
        )
    )
    matches = client.search_pull_requests("demo", "FIX", "acme")
    assert [(pr.id, pr.state) for pr in matches] == [(2, "MERGED")]


@respx.mock
def test_search_exact_id_and_missing():
    client = BitbucketClient("secret")
    respx.get(f"{BASE}/pullrequests/12").mock(
        return_value=httpx.Response(200, json=pull_request(12, "Title"))
    )
    respx.get(f"{BASE}/pullrequests/13").mock(return_value=httpx.Response(404))
    assert client.search_pull_requests("demo", "12", "acme")[0].id == 12
    assert client.search_pull_requests("demo", "13", "acme") == []


@respx.mock
def test_open_and_decline():
    client = BitbucketClient("secret")
    opened = respx.post(f"{BASE}/pullrequests").mock(
        return_value=httpx.Response(201, json=pull_request(1, "Fix"))
    )
    declined = respx.post(f"{BASE}/pullrequests/1/decline").mock(
        return_value=httpx.Response(200, json={})
    )
    pr = client.create_pull_request("demo", "feature", "main", "Fix", "Details", "acme")
    assert pr.id == 1
    assert json.loads(opened.calls[0].request.content) == {
        "title": "Fix",
        "description": "Details",
        "source": {"branch": {"name": "feature"}},
        "destination": {"branch": {"name": "main"}},
    }
    client.decline_pull_request("demo", 1, "acme")
    assert declined.called


@respx.mock
def test_approve_comment_first_and_failure_partial():
    client = BitbucketClient("secret")
    comment = respx.post(f"{BASE}/pullrequests/1/comments").mock(
        return_value=httpx.Response(201, json={})
    )
    approval = respx.post(f"{BASE}/pullrequests/1/approve").mock(return_value=httpx.Response(403))
    with pytest.raises(BitbucketError, match="Comentário publicado"):
        client.approve_pull_request("demo", 1, "looks good", "acme")
    assert json.loads(comment.calls[0].request.content) == {"content": {"raw": "looks good"}}
    assert approval.call_count == 1


@respx.mock
def test_comment_failure_does_not_approve():
    client = BitbucketClient("secret")
    respx.post(f"{BASE}/pullrequests/1/comments").mock(return_value=httpx.Response(403))
    approval = respx.post(f"{BASE}/pullrequests/1/approve").mock(return_value=httpx.Response(200))
    with pytest.raises(BitbucketError):
        client.approve_pull_request("demo", 1, "looks good", "acme")
    assert not approval.called


@respx.mock
def test_approval_succeeds_after_comment():
    client = BitbucketClient("secret")
    operations: list[str] = []

    def respond(request: httpx.Request) -> httpx.Response:
        operations.append(request.url.path.rsplit("/", 1)[-1])
        return httpx.Response(200, json={})

    respx.post(f"{BASE}/pullrequests/1/comments").mock(side_effect=respond)
    respx.post(f"{BASE}/pullrequests/1/approve").mock(side_effect=respond)
    client.approve_pull_request("demo", 1, "looks good", "acme")
    assert operations == ["comments", "approve"]


@respx.mock
def test_pagination_rejects_cross_origin():
    client = BitbucketClient("secret")
    respx.get(f"{BASE}/refs/branches").mock(
        return_value=httpx.Response(200, json={"values": [], "next": "https://evil.example/next"})
    )
    with pytest.raises(BitbucketError, match="paginação"):
        client.list_pr_branches("demo", "acme")
