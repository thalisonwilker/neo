"""Contratos dos serviços de tarefas e capacidades opcionais."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from neo.services.tasks.errors import TaskProviderUnsupportedError
from neo.services.tasks.models import (
    ChecklistItem,
    StoryAnalysis,
    TaskComment,
    TaskIteration,
    TaskMember,
    TaskStory,
    TaskWorkflow,
    TaskWorkflowState,
)


@runtime_checkable
class TaskProvider(Protocol):
    def get_current_member(self) -> TaskMember: ...

    def list_stories(
        self, owner_id: str | None = None, iteration_id: int | None = None
    ) -> list[TaskStory]: ...

    def search_stories(self, query: str) -> list[TaskStory]: ...

    def get_story(self, story_id: int | str) -> TaskStory: ...

    def analyze_story(self, story_id: int | str) -> StoryAnalysis: ...

    def create_story(
        self,
        name: str,
        description: str | None = None,
        story_type: str = "feature",
        iteration_id: int | None = None,
        owner_ids: list[str] | None = None,
        workflow_state_id: int | None = None,
    ) -> TaskStory: ...

    def create_task(
        self, story_id: int | str, description: str, complete: bool = False
    ) -> ChecklistItem: ...

    def update_task(
        self,
        story_id: int | str,
        task_id: int | str,
        complete: bool | None = None,
        description: str | None = None,
    ) -> ChecklistItem: ...

    def create_comment(self, story_id: int | str, text: str) -> TaskComment: ...


@runtime_checkable
class TaskWorkflowProvider(Protocol):
    def list_workflows(self) -> list[TaskWorkflow]: ...

    def list_workflow_states(self) -> list[TaskWorkflowState]: ...

    def get_default_workflow_state_id(self) -> int | None: ...


@runtime_checkable
class TaskIterationProvider(Protocol):
    def list_iterations(self) -> list[TaskIteration]: ...

    def get_latest_iteration(self) -> TaskIteration | None: ...

    def resolve_iteration(self, term: str | None = None) -> TaskIteration | None: ...


class ConfiguredTaskProvider(TaskProvider, TaskWorkflowProvider, TaskIterationProvider, Protocol):
    """Capacidades disponíveis nos provedores atualmente configuráveis."""


def require_iterations(provider: TaskProvider) -> TaskIterationProvider:
    if not isinstance(provider, TaskIterationProvider):
        raise TaskProviderUnsupportedError("O provedor não oferece a capacidade de iterações.")
    return provider


def require_workflows(provider: TaskProvider) -> TaskWorkflowProvider:
    if not isinstance(provider, TaskWorkflowProvider):
        raise TaskProviderUnsupportedError("O provedor não oferece a capacidade de workflows.")
    return provider
