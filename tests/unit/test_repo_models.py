"""Testes unitários para modelos de repositório e formatação de data (spec 0028)."""

from neo.integrations.git.api.github.models import parse_github_repo
from neo.integrations.git.models import GitRepo
from neo.output import format_american_date


def test_bitbucket_repo_from_api_dict_includes_created_on():
    payload = {
        "name": "meu-repo",
        "slug": "meu-repo",
        "is_private": False,
        "description": "Repositório de teste",
        "created_on": "2024-03-15T08:30:00.000000+00:00",
        "updated_on": "2026-11-04T12:00:00.000000+00:00",
        "mainbranch": {"name": "main"},
        "workspace": {"slug": "meu-ws"},
        "links": {
            "clone": [
                {"name": "https", "href": "https://bitbucket.org/meu-ws/meu-repo.git"},
                {"name": "ssh", "href": "git@bitbucket.org:meu-ws/meu-repo.git"},
            ],
            "html": {"href": "https://bitbucket.org/meu-ws/meu-repo"},
        },
    }
    repo = GitRepo.from_api_dict(payload)
    assert repo.name == "meu-repo"
    assert repo.created_on == "2024-03-15T08:30:00.000000+00:00"
    assert repo.updated_on == "2026-11-04T12:00:00.000000+00:00"


def test_parse_github_repo_includes_created_on():
    payload = {
        "name": "meu-repo-gh",
        "private": True,
        "description": "Repo GitHub",
        "created_at": "2023-01-20T10:15:30Z",
        "updated_at": "2026-10-30T18:45:00Z",
        "default_branch": "develop",
        "owner": {"login": "minha-org"},
        "html_url": "https://github.com/minha-org/meu-repo-gh",
        "clone_url": "https://github.com/minha-org/meu-repo-gh.git",
        "ssh_url": "git@github.com:minha-org/meu-repo-gh.git",
    }
    repo = parse_github_repo(payload)
    assert repo.name == "meu-repo-gh"
    assert repo.created_on == "2023-01-20T10:15:30Z"
    assert repo.updated_on == "2026-10-30T18:45:00Z"


def test_format_american_date_various_formats():
    assert format_american_date("2024-03-15T08:30:00.000000+00:00") == "03/15/2024"
    assert format_american_date("2023-01-20T10:15:30Z") == "01/20/2023"
    assert format_american_date("2026-11-04") == "11/04/2026"
    assert format_american_date(None) == "-"
    assert format_american_date("") == "-"
    assert format_american_date("   ") == "-"
    assert format_american_date("invalid-date") == "-"
