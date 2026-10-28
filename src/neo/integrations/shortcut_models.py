"""Modelos tipados (DTOs) da REST API v3 do Shortcut."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field


class ShortcutMember(BaseModel):
    """Representa um membro/usuário no Shortcut."""

    id: str
    name: str = ""
    mention_name: str = ""
    email_address: str | None = None

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> ShortcutMember:
        profile = data.get("profile", {})
        return cls(
            id=data.get("id", ""),
            name=profile.get("name", "") or data.get("name", ""),
            mention_name=profile.get("mention_name", "") or data.get("mention_name", ""),
            email_address=profile.get("email_address"),
        )


class ShortcutWorkflowState(BaseModel):
    """Representa uma coluna/estado de um Workflow no Shortcut."""

    id: int
    name: str
    type: str = "unstarted"  # unstarted, started, done
    workflow_id: int | None = None
    workflow_name: str = ""

    @classmethod
    def from_api_dict(
        cls,
        data: dict[str, Any],
        workflow_id: int | None = None,
        workflow_name: str = "",
    ) -> ShortcutWorkflowState:
        return cls(
            id=int(data.get("id", 0)),
            name=str(data.get("name", "")),
            type=str(data.get("type", "unstarted")),
            workflow_id=workflow_id,
            workflow_name=workflow_name,
        )


class ShortcutWorkflow(BaseModel):
    """Representa um Workflow (board) no Shortcut e suas colunas (states)."""

    id: int
    name: str
    states: list[ShortcutWorkflowState] = Field(default_factory=list)

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> ShortcutWorkflow:
        wf_id = int(data.get("id", 0))
        wf_name = str(data.get("name", ""))
        raw_states = data.get("states", [])
        states = [
            ShortcutWorkflowState.from_api_dict(s, workflow_id=wf_id, workflow_name=wf_name)
            for s in raw_states
            if isinstance(s, dict)
        ]
        return cls(id=wf_id, name=wf_name, states=states)


class ShortcutIteration(BaseModel):
    """Representa uma Iteração (Sprint) no Shortcut."""

    id: int
    name: str
    status: str = "started"  # unstarted, started, done
    start_date: str = ""
    end_date: str = ""

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> ShortcutIteration:
        return cls(
            id=int(data.get("id", 0)),
            name=str(data.get("name", "")),
            status=str(data.get("status", "started")),
            start_date=str(data.get("start_date", "") or ""),
            end_date=str(data.get("end_date", "") or ""),
        )


class ShortcutStory(BaseModel):
    """Representa uma Story no Shortcut."""

    id: int
    name: str
    story_type: str = "feature"  # feature, bug, chore
    description: str | None = None
    app_url: str | None = None
    archived: bool = False
    completed: bool = False
    workflow_state_id: int | None = None
    workflow_state_name: str = "Em andamento"
    iteration_id: int | None = None
    owner_ids: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    estimate: float | None = None

    @classmethod
    def from_api_dict(cls, data: dict[str, Any]) -> ShortcutStory:
        label_names = [lb.get("name", "") for lb in data.get("labels", []) if isinstance(lb, dict)]
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            story_type=data.get("story_type", "feature"),
            description=data.get("description"),
            app_url=data.get("app_url"),
            archived=data.get("archived", False),
            completed=data.get("completed", False),
            workflow_state_id=data.get("workflow_state_id"),
            iteration_id=data.get("iteration_id"),
            owner_ids=data.get("owner_ids", []),
            labels=label_names,
            estimate=data.get("estimate"),
        )


class StoryAnalysis(BaseModel):
    """Relatório estruturado de análise de contexto de uma story."""

    story_id: int
    story_type: str
    title: str
    suggested_branch: str
    commit_prefix: str
    keywords: list[str]
    has_blockers: bool = False
    acceptance_criteria: list[str] = Field(default_factory=list)

    @classmethod
    def from_story(cls, story: ShortcutStory) -> StoryAnalysis:
        """Gera análise heurística de contexto a partir dos metadados da story."""
        # Normalização do slug para branch git
        slug = re.sub(r"[^a-zA-Z0-9_-]", "-", story.name.lower()).strip("-")
        # Encurtar slug
        short_slug = "-".join([w for w in slug.split("-") if w][:5])
        type_prefix = "bug" if story.story_type == "bug" else "feature"
        suggested_branch = f"{type_prefix}/sc-{story.id}-{short_slug}"
        commit_prefix = f"[sc-{story.id}]"

        # Extração de palavras-chave
        text = f"{story.name} {story.description or ''}"
        words = re.findall(r"\b[a-zA-Z0-9_-]{4,}\b", text.lower())
        stopwords = {
            "para",
            "com",
            "como",
            "esta",
            "este",
            "esse",
            "isso",
            "pelo",
            "pela",
            "quando",
            "entao",
            "onde",
            "porque",
            "qual",
            "mais",
            "sobre",
            "qualquer",
            "have",
            "with",
            "from",
            "that",
            "this",
            "which",
            "will",
            "what",
            "then",
        }
        unique_keywords = sorted({w for w in words if w not in stopwords})[:8]

        # Extração de critérios de aceite
        criteria: list[str] = []
        if story.description:
            for line in story.description.split("\n"):
                line_strip = line.strip()
                if line_strip.startswith(("- [ ]", "- [x]", "* [ ]", "* [x]")):
                    criteria.append(line_strip[5:].strip())
                elif re.match(r"^(dado|quando|então|given|when|then)\b", line_strip, re.IGNORECASE):
                    criteria.append(line_strip)

        has_blockers = any(
            "block" in lb.lower() or "impedimento" in lb.lower() for lb in story.labels
        )

        return cls(
            story_id=story.id,
            story_type=story.story_type,
            title=story.name,
            suggested_branch=suggested_branch,
            commit_prefix=commit_prefix,
            keywords=unique_keywords,
            has_blockers=has_blockers,
            acceptance_criteria=criteria,
        )
