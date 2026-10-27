import httpx
import pytest
import respx

from neo.integrations.shortcut import (
    ShortcutAuthError,
    ShortcutClient,
    ShortcutNotFoundError,
)
from neo.integrations.shortcut_models import (
    ShortcutMember,
    ShortcutStory,
    StoryAnalysis,
)


@pytest.fixture
def sc_client():
    return ShortcutClient(token="mock-sc-token", base_url="https://api.app.shortcut.com/api/v3")


@respx.mock
def test_get_current_member(sc_client: ShortcutClient):
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "member-uuid-123",
                "profile": {
                    "name": "Thalyson Dev",
                    "mention_name": "thalyson",
                    "email_address": "thalyson@exemplo.com",
                },
            },
        )
    )

    member = sc_client.get_current_member()
    assert isinstance(member, ShortcutMember)
    assert member.id == "member-uuid-123"
    assert member.name == "Thalyson Dev"
    assert member.mention_name == "thalyson"


@respx.mock
def test_list_stories(sc_client: ShortcutClient):
    respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": 101,
                        "name": "Implementar tela de login",
                        "story_type": "feature",
                        "description": "Permitir autenticação por email",
                        "labels": [{"name": "frontend"}],
                    }
                ]
            },
        )
    )

    stories = sc_client.list_stories()
    assert len(stories) == 1
    assert isinstance(stories[0], ShortcutStory)
    assert stories[0].id == 101
    assert stories[0].name == "Implementar tela de login"
    assert stories[0].labels == ["frontend"]


@respx.mock
def test_get_story_and_not_found(sc_client: ShortcutClient):
    respx.get("https://api.app.shortcut.com/api/v3/stories/101").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 101,
                "name": "Corrigir crash ao logar",
                "story_type": "bug",
                "description": "- [ ] Reproduzir em staging\n- [ ] Fix",
                "labels": [{"name": "bug"}, {"name": "blocker"}],
            },
        )
    )
    respx.get("https://api.app.shortcut.com/api/v3/stories/999").mock(
        return_value=httpx.Response(404, json={"message": "Story not found"})
    )

    story = sc_client.get_story(101)
    assert story.id == 101
    assert story.story_type == "bug"

    with pytest.raises(ShortcutNotFoundError, match="não foi encontrada"):
        sc_client.get_story(999)


@respx.mock
def test_search_stories(sc_client: ShortcutClient):
    respx.get("https://api.app.shortcut.com/api/v3/search/stories").mock(
        return_value=httpx.Response(
            200,
            json={"data": [{"id": 202, "name": "Busca avançada", "story_type": "feature"}]},
        )
    )

    results = sc_client.search_stories("busca")
    assert len(results) == 1
    assert results[0].id == 202


@respx.mock
def test_analyze_story(sc_client: ShortcutClient):
    respx.get("https://api.app.shortcut.com/api/v3/stories/505").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": 505,
                "name": "Erro de timeout na autenticação",
                "story_type": "bug",
                "description": "- [ ] Investigar queries\nDado usuário autenticado",
                "labels": [{"name": "impedimento"}],
            },
        )
    )

    analysis = sc_client.analyze_story(505)
    assert isinstance(analysis, StoryAnalysis)
    assert analysis.story_id == 505
    assert analysis.story_type == "bug"
    assert "bug/sc-505-erro-de-timeout" in analysis.suggested_branch
    assert analysis.commit_prefix == "[sc-505]"
    assert analysis.has_blockers is True
    assert len(analysis.acceptance_criteria) >= 1


@respx.mock
def test_shortcut_auth_error_401(sc_client: ShortcutClient):
    respx.get("https://api.app.shortcut.com/api/v3/member").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized token"})
    )

    with pytest.raises(ShortcutAuthError, match="Falha de autenticação no Shortcut"):
        sc_client.get_current_member()
