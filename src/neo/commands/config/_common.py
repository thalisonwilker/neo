"""Funções compartilhadas dos comandos."""

from __future__ import annotations

import contextlib
import re
from typing import Any

import httpx


def _detect_current_task_info(
    branch: str | None,
    tasks_configured: bool,
) -> tuple[str, str, dict[str, Any] | None]:
    """Descobre a tarefa ativa para os blocos Git e Tasks.

    Retorna (task_id_for_git, current_task_for_tasks, task_data_for_json).
    """
    if not tasks_configured:
        return "-", "-", None

    candidate_id: int | None = None
    if branch:
        match = re.search(r"(?:^|/|-|_|[a-zA-Z])(\d{3,7})(?:$|/|-|_|[a-zA-Z])", branch)
        if match:
            try:
                candidate_id = int(match.group(1))
            except ValueError:
                pass

    from neo.config import get_credential
    from neo.services.tasks.errors import TaskProviderError
    from neo.services.tasks.resolver import create_task_provider

    token = get_credential("shortcut")
    if not token:
        return "-", "-", None

    client = create_task_provider("shortcut", token, timeout=2.0)

    # 1. Se encontrou candidate_id na branch
    if candidate_id:
        with contextlib.suppress(TaskProviderError, httpx.RequestError, ValueError, KeyError):
            story = client.get_story(candidate_id)
            task_git = f"#{story.id}"
            if story.tasks:
                done_cnt = sum(1 for t in story.tasks if t.complete)
                task_full = f"#{story.id} {story.name} {done_cnt}/{len(story.tasks)}"
            else:
                task_full = f"#{story.id} {story.name}"
            json_info: dict[str, Any] = {
                "id": story.id,
                "title": story.name,
                "checklist": {
                    "completed": sum(1 for t in story.tasks if t.complete),
                    "total": len(story.tasks),
                }
                if story.tasks
                else None,
            }
            return task_git, task_full, json_info

    # 2. Fallback: primeira story atribuída a mim ou em andamento
    with contextlib.suppress(TaskProviderError, httpx.RequestError, ValueError, KeyError):
        member = client.get_current_member()
        stories = client.list_stories()
        my_stories = [s for s in stories if member.id in s.owner_ids]
        target = my_stories[0] if my_stories else (stories[0] if stories else None)
        if target:
            full = client.get_story(target.id)
            task_git = f"#{full.id}"
            if full.tasks:
                done_cnt = sum(1 for t in full.tasks if t.complete)
                task_full = f"#{full.id} {full.name} {done_cnt}/{len(full.tasks)}"
            else:
                task_full = f"#{full.id} {full.name}"
            json_info = {
                "id": full.id,
                "title": full.name,
                "checklist": {
                    "completed": sum(1 for t in full.tasks if t.complete),
                    "total": len(full.tasks),
                }
                if full.tasks
                else None,
            }
            return task_git, task_full, json_info

    return "-", "-", None
