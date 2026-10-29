"""Testes unitários para active_context.py (AC-1, AC-2)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from neo.services.active_context import (
    bind_task_id,
    count_task_commits,
    extract_task_id_from_branch,
    get_bound_task_id,
    resolve_active_task_id,
    unbind_task_id,
)


@pytest.mark.parametrize(
    ("branch", "expected_id"),
    [
        ("feature/sc-1234-nome", 1234),
        ("sc-1234", 1234),
        ("fix/1234-slug", 1234),
        ("story/1234", 1234),
        ("feature/SC-5678-abc", 5678),
        ("fix/9999", 9999),
        ("feature/0017-contexto-ativo", 17),
        ("main", None),
        ("master", None),
        ("develop", None),
        ("docs/refactor-cli", None),
        ("", None),
        (None, None),
    ],
)
def test_extract_task_id_from_branch(branch: str | None, expected_id: int | None) -> None:
    assert extract_task_id_from_branch(branch) == expected_id


def test_bind_and_unbind_task_id(tmp_path: Path) -> None:
    # Cria estrutura simulando repo git
    git_dir = tmp_path / ".git"
    git_dir.mkdir(parents=True)

    # Inicialmente nada vinculado
    assert get_bound_task_id(tmp_path) is None

    # Vincula task 2157
    bind_path = bind_task_id(2157, repo_path=tmp_path)
    assert bind_path.exists()
    assert get_bound_task_id(tmp_path) == 2157

    # Remove vínculo
    removed = unbind_task_id(tmp_path)
    assert removed is True
    assert get_bound_task_id(tmp_path) is None

    # Segunda remoção deve retornar False
    assert unbind_task_id(tmp_path) is False


def test_bind_task_id_outside_git_raises_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="não é um repositório Git válido"):
        bind_task_id(1234, repo_path=tmp_path)


def test_resolve_active_task_id_precedence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    git_dir = tmp_path / ".git"
    git_dir.mkdir(parents=True)

    # Mock get_current_branch para retornar 'feature/sc-100-auto'
    monkeypatch.setattr(
        "neo.services.active_context.get_current_branch",
        lambda _repo=None: "feature/sc-100-auto",
    )

    # 1. Sem bind, deve inferir 100 da branch
    assert resolve_active_task_id(tmp_path) == 100

    # 2. Com bind manual em 200, bind deve ter precedência
    bind_task_id(200, repo_path=tmp_path)
    assert resolve_active_task_id(tmp_path) == 200

    # 3. Ao dar unbind, volta a inferir 100 da branch
    unbind_task_id(tmp_path)
    assert resolve_active_task_id(tmp_path) == 100


def test_count_task_commits_outside_git(tmp_path: Path) -> None:
    assert count_task_commits(123, repo_path=tmp_path) == 0


def test_count_task_commits_with_real_git(tmp_path: Path) -> None:
    # Inicializa um git real no diretório temporário
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tester"],
        cwd=tmp_path,
        check=True,
    )

    # Commit inicial na main
    (tmp_path / "file.txt").write_text("v1")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=tmp_path, check=True)

    # Cria branch de feature
    subprocess.run(
        ["git", "checkout", "-b", "feature/sc-555-minha-feature"],
        cwd=tmp_path,
        check=True,
    )

    (tmp_path / "file.txt").write_text("v2")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "feat: refactor 555"], cwd=tmp_path, check=True)

    (tmp_path / "file2.txt").write_text("v3")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "fix: sc-555 fix issue"], cwd=tmp_path, check=True)

    count = count_task_commits(555, repo_path=tmp_path)
    assert count == 2
