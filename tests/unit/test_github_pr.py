"""Testes dos contratos GitHub de pull requests da spec 0025."""

import json

import httpx
import pytest
import respx

from neo.integrations.github import GitHubClient, GitHubError

BASE = "https://api.github.com/repos/acme/project"


def _pr(number: int, title: str, state: str = "open", merged: bool = False) -> dict:
    return {
        "number": number,
        "title": title,
        "state": state,
        "merged_at": "2026-01-01T00:00:00Z" if merged else None,
        "head": {"ref": "feature/work"},
        "base": {"ref": "main"},
        "html_url": f"https://github.com/acme/project/pull/{number}",
    }


@respx.mock
def test_AC_5_list_open_pull_requests_paginated():
    route = respx.get(f"{BASE}/pulls").mock(
        side_effect=[
            httpx.Response(
                200, json=[_pr(1, "First")], headers={"Link": f'<{BASE}/pulls?page=2>; rel="next"'}
            ),
            httpx.Response(200, json=[_pr(2, "Second")]),
        ]
    )
    result = GitHubClient("token").list_open_pull_requests("project", "acme")
    assert [pr.id for pr in result] == [1, 2]
    assert route.calls[0].request.url.params["state"] == "open"


@respx.mock
def test_AC_1_create_pull_request_and_select_all_remote_branches():
    api = GitHubClient("token")
    branches = respx.get(f"{BASE}/branches").mock(
        side_effect=[
            httpx.Response(
                200,
                json=[{"name": "main"}],
                headers={"Link": f'<{BASE}/branches?page=2>; rel="next"'},
            ),
            httpx.Response(200, json=[{"name": "develop"}]),
        ]
    )
    create = respx.post(f"{BASE}/pulls").mock(
        return_value=httpx.Response(201, json=_pr(1, "Minha PR"))
    )
    assert api.list_pr_branches("project", "acme") == ["main", "develop"]
    assert branches.call_count == 2
    pr = api.create_pull_request("project", "feature/work", "main", "Minha PR", "Descrição", "acme")
    assert pr.id == 1 and pr.state == "OPEN" and pr.url.endswith("/1")
    assert json.loads(create.calls.last.request.content) == {
        "head": "feature/work",
        "base": "main",
        "title": "Minha PR",
        "body": "Descrição",
    }


@respx.mock
def test_AC_2_approval_submits_message_and_event_once():
    route = respx.post(f"{BASE}/pulls/7/reviews").mock(return_value=httpx.Response(200, json={}))
    GitHubClient("token").approve_pull_request("project", 7, "Muito bom", "acme")
    assert route.call_count == 1
    assert json.loads(route.calls.last.request.content) == {"event": "APPROVE", "body": "Muito bom"}


@respx.mock
def test_AC_3_decline_closes_without_merge():
    route = respx.patch(f"{BASE}/pulls/7").mock(return_value=httpx.Response(200, json={}))
    GitHubClient("token").decline_pull_request("project", 7, "acme")
    assert route.call_count == 1
    assert json.loads(route.calls.last.request.content) == {"state": "closed"}


@respx.mock
def test_AC_4_search_id_and_paginated_case_insensitive_title():
    api = GitHubClient("token")
    respx.get(f"{BASE}/pulls/17").mock(return_value=httpx.Response(200, json=_pr(17, "Fix")))
    respx.get(f"{BASE}/pulls/18").mock(return_value=httpx.Response(404, json={}))
    route = respx.get(f"{BASE}/pulls").mock(
        side_effect=[
            httpx.Response(
                200, json=[_pr(1, "other")], headers={"Link": f'<{BASE}/pulls?page=2>; rel="next"'}
            ),
            httpx.Response(
                200, json=[_pr(2, "Corrige LOGIN", "closed", True), _pr(3, "login", "closed")]
            ),
        ]
    )
    assert api.search_pull_requests("project", "17", "acme")[0].id == 17
    assert api.search_pull_requests("project", "18", "acme") == []
    found = api.search_pull_requests("project", "Login", "acme")
    assert [(pr.id, pr.state) for pr in found] == [(2, "MERGED"), (3, "DECLINED")]
    assert route.calls[0].request.url.params["state"] == "all"
    assert route.call_count == 2


@respx.mock
def test_git_pagination_never_sends_token_to_another_origin():
    respx.get(f"{BASE}/branches").mock(
        return_value=httpx.Response(
            200, json=[], headers={"Link": '<https://evil.example/next>; rel="next"'}
        )
    )
    with pytest.raises(GitHubError, match="origem inválida"):
        GitHubClient("private-secret").list_pr_branches("project", "acme")
