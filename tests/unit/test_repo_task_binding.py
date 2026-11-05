"""Testes unitários para resolução e formatação de task por repositório (spec 0028)."""

from unittest.mock import patch

from neo.git_context import get_repo_tasks_map, resolve_task_for_repo


def test_get_repo_tasks_map_and_normalization():
    fake_data = {
        "selected": "/Users/user/repo-a",
        "repositories": {
            "/Users/user/repo-a": {"task": "1234"},
            "/Users/user/repo-b": {"task": "#5678"},
            "/Users/user/repo-c": {"task": "   #999   "},
            "/Users/user/repo-d": {"task": None},
            "/Users/user/repo-e": {"task": ""},
        },
    }
    with patch("neo.git_context._read", return_value=fake_data):
        tasks_map = get_repo_tasks_map()
        assert tasks_map["repo-a"] == "#1234"
        assert tasks_map["repo-b"] == "#5678"
        assert tasks_map["repo-c"] == "#999"
        assert "repo-d" not in tasks_map
        assert "repo-e" not in tasks_map


def test_resolve_task_for_repo_matches_name_or_slug():
    tasks_map = {
        "servico-auth": "#101",
        "meu-backend": "#202",
    }
    # Match pelo nome
    assert resolve_task_for_repo("servico-auth", tasks_map=tasks_map) == "#101"
    # Match pelo slug
    assert (
        resolve_task_for_repo(
            "Serviço de Autenticação", repo_slug="servico-auth", tasks_map=tasks_map
        )
        == "#101"
    )
    # Match insensível a maiúsculas
    assert resolve_task_for_repo("Meu-Backend", tasks_map=tasks_map) == "#202"
    # Sem match
    assert resolve_task_for_repo("outro-repo", repo_slug="outro", tasks_map=tasks_map) is None
