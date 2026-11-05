"""Registro local de repositórios e contexto selecionado do Neo."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from neo import config


def _path() -> Path:
    return config.DEFAULT_CONFIG_DIR / "git-context.json"


def _read() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"selected": None, "repositories": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("repositories"), dict):
            raise TypeError("Formato inválido")
        return data
    except (OSError, ValueError, TypeError) as exc:
        raise ValueError(f"Não foi possível ler o registro Git: {exc}") from exc


def _write(data: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".git-context-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _git_root(path: Path) -> Path:
    path = path.expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"Diretório não encontrado: {path}")
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise ValueError(f"Não foi possível executar git: {exc}") from exc
    if result.returncode or not result.stdout.strip():
        raise ValueError(f"Não é um repositório Git: {path}")
    return Path(result.stdout.strip()).resolve()


def select_repo(path: Path) -> Path:
    root = _git_root(path)
    data = _read()
    data["repositories"].setdefault(str(root), {"task": None})
    data["selected"] = str(root)
    _write(data)
    return root


def selected_repo() -> Path | None:
    selected = _read().get("selected")
    return Path(selected) if isinstance(selected, str) and selected else None


def resolve_repo_path() -> Path:
    selected = selected_repo()
    try:
        return _git_root(selected or Path.cwd())
    except ValueError as exc:
        raise ValueError(
            f"{exc}. Selecione um repositório com `neo git repo select <caminho>`."
        ) from exc


def list_repos() -> list[dict[str, object]]:
    data = _read()
    return [
        {"path": path, "selected": path == data.get("selected"), "task": item.get("task")}
        for path, item in data["repositories"].items()
        if isinstance(item, dict)
    ]


def unset_repo() -> bool:
    data = _read()
    existed = bool(data.get("selected"))
    data["selected"] = None
    _write(data)
    return existed


def get_task() -> str | None:
    data = _read()
    path = str(resolve_repo_path())
    entry = data["repositories"].get(path, {})
    task = entry.get("task") if isinstance(entry, dict) else None
    return task if isinstance(task, str) else None


def set_task(task: str) -> None:
    task = task.strip()
    if not task:
        raise ValueError("O ID da task não pode ser vazio.")
    path = str(resolve_repo_path())
    data = _read()
    data["repositories"].setdefault(path, {})["task"] = task
    _write(data)


def unset_task() -> bool:
    path = str(resolve_repo_path())
    data = _read()
    entry = data["repositories"].get(path, {})
    existed = bool(entry.get("task")) if isinstance(entry, dict) else False
    if existed:
        entry.pop("task", None)
        _write(data)
    return existed


def get_repo_tasks_map() -> dict[str, str]:
    """Retorna um mapeamento de nome/slug de repositório (minúsculo) para a task formatada (#<TASK-ID>)."""
    try:
        data = _read()
    except ValueError:
        return {}
    mapping: dict[str, str] = {}
    repos = data.get("repositories", {})
    if not isinstance(repos, dict):
        return mapping
    for path_str, entry in repos.items():
        if isinstance(entry, dict):
            task = entry.get("task")
            if isinstance(task, str) and task.strip():
                clean_task = f"#{task.strip().lstrip('#')}"
                base_name = Path(path_str).name.lower()
                mapping[base_name] = clean_task
    return mapping


def resolve_task_for_repo(
    repo_name: str,
    repo_slug: str | None = None,
    tasks_map: dict[str, str] | None = None,
) -> str | None:
    """Busca a task vinculada localmente ao repositório pelo nome ou slug."""
    if tasks_map is None:
        tasks_map = get_repo_tasks_map()
    if repo_name.lower() in tasks_map:
        return tasks_map[repo_name.lower()]
    if repo_slug and repo_slug.lower() in tasks_map:
        return tasks_map[repo_slug.lower()]
    return None
