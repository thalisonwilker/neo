"""Testes unitários para agent_roles.py (AC-1, AC-3)."""

from __future__ import annotations

import pytest

from neo.services.agent_roles import (
    ROLE_CODE,
    ROLE_REFINE,
    ROLE_REVIEW_PR,
    ROLE_REVIEW_TASK,
    SUPPORTED_AGENT_ROLES,
    build_role_prompt,
    get_role_definition,
    list_role_definitions,
    validate_agent_role,
)


@pytest.mark.parametrize(
    ("input_role", "expected"),
    [
        ("code", ROLE_CODE),
        ("CODE", ROLE_CODE),
        ("coder", ROLE_CODE),
        ("coding", ROLE_CODE),
        ("refine", ROLE_REFINE),
        ("tasks", ROLE_REFINE),
        ("refinador", ROLE_REFINE),
        ("review-pr", ROLE_REVIEW_PR),
        ("review", ROLE_REVIEW_PR),
        ("pr", ROLE_REVIEW_PR),
        ("review-task", ROLE_REVIEW_TASK),
        ("dod", ROLE_REVIEW_TASK),
        ("audit", ROLE_REVIEW_TASK),
    ],
)
def test_validate_agent_role_success(input_role: str, expected: str) -> None:
    assert validate_agent_role(input_role) == expected


@pytest.mark.parametrize("invalid_role", ["invalid", "deploy", "tester", ""])
def test_validate_agent_role_invalid_raises_value_error(invalid_role: str) -> None:
    with pytest.raises(ValueError, match="não é suportado|não pode ser vazio"):
        validate_agent_role(invalid_role)


def test_list_and_get_role_definitions() -> None:
    roles = list_role_definitions()
    assert len(roles) == 4
    role_ids = [r.id for r in roles]
    for expected in SUPPORTED_AGENT_ROLES:
        assert expected in role_ids

    refine_def = get_role_definition(ROLE_REFINE)
    assert refine_def.id == "refine"
    assert refine_def.allows_code_edits is False
    assert "Refinador" in refine_def.title

    code_def = get_role_definition(ROLE_CODE)
    assert code_def.allows_code_edits is True


def test_build_role_prompt_refine_with_and_without_task(tmp_path) -> None:
    prompt_with_task = build_role_prompt(
        ROLE_REFINE,
        task_id=2157,
        story_title="Refatoração de Config",
    )
    assert prompt_with_task is not None
    assert "#2157" in prompt_with_task
    assert "Refatoração de Config" in prompt_with_task
    assert "Não altere código de produção" in prompt_with_task

    prompt_without_task = build_role_prompt(ROLE_REFINE, repo_path=tmp_path)
    assert prompt_without_task is not None
    assert "Nenhuma demanda ativa foi vinculada" in prompt_without_task


def test_build_role_prompt_review_pr() -> None:
    prompt = build_role_prompt(ROLE_REVIEW_PR, task_id=3000)
    assert prompt is not None
    assert "Revisor de Pull Requests" in prompt
    assert "#3000" in prompt


def test_build_role_prompt_review_task() -> None:
    prompt = build_role_prompt(ROLE_REVIEW_TASK, task_id=123)
    assert prompt is not None
    assert "Auditor de Definition of Done" in prompt
    assert "#123" in prompt


def test_build_role_prompt_code_without_task_returns_none(tmp_path) -> None:
    prompt = build_role_prompt(ROLE_CODE, repo_path=tmp_path)
    assert prompt is None
