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


@respx.mock
def test_list_workflows_and_states(sc_client: ShortcutClient):
    respx.get("https://api.app.shortcut.com/api/v3/workflows").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": 500001,
                    "name": "Atual",
                    "states": [
                        {"id": 500010, "name": "📝 - Backlog de Sprint", "type": "unstarted"},
                        {"id": 500011, "name": "🚨 - Bug", "type": "unstarted"},
                        {"id": 500012, "name": "🚧 - Em Progresso", "type": "started"},
                        {"id": 500013, "name": "✅ - Finalizado", "type": "done"},
                    ],
                }
            ],
        )
    )

    workflows = sc_client.list_workflows()
    assert len(workflows) == 1
    assert workflows[0].name == "Atual"
    assert len(workflows[0].states) == 4

    states = sc_client.list_workflow_states()
    assert [s.name for s in states] == [
        "📝 - Backlog de Sprint",
        "🚨 - Bug",
        "🚧 - Em Progresso",
        "✅ - Finalizado",
    ]
    assert states[0].workflow_name == "Atual"


@respx.mock
def test_list_and_resolve_iterations(sc_client: ShortcutClient):
    respx.get("https://api.app.shortcut.com/api/v3/iterations").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": 21001,
                    "name": "Sprint 70",
                    "status": "done",
                    "start_date": "2026-10-01",
                    "end_date": "2026-10-14",
                },
                {
                    "id": 21002,
                    "name": "Sprint 71",
                    "status": "started",
                    "start_date": "2026-10-15",
                    "end_date": "2026-10-29",
                },
            ],
        )
    )

    iterations = sc_client.list_iterations()
    assert len(iterations) == 2
    # Ordenado da mais recente para a mais antiga
    assert iterations[0].name == "Sprint 71"
    assert iterations[1].name == "Sprint 70"

    latest = sc_client.get_latest_iteration()
    assert latest is not None
    assert latest.id == 21002

    # resolve_iteration(None) -> última
    assert sc_client.resolve_iteration(None) == latest
    # resolve_iteration("all") -> None
    assert sc_client.resolve_iteration("all") is None
    # resolve por ID, nome exato e substring
    assert sc_client.resolve_iteration("21001").name == "Sprint 70"
    assert sc_client.resolve_iteration("sprint 70").id == 21001
    assert sc_client.resolve_iteration("71").id == 21002

    with pytest.raises(ShortcutNotFoundError, match="não encontrada"):
        sc_client.resolve_iteration("Sprint 999")
