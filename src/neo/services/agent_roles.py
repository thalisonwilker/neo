"""Serviço de papéis especializados de agentes (`agent_roles`).

Define o catálogo de papéis suportados (`code`, `refine`, `review-pr`, `review-task`),
validação de identificadores e composição de prompts contextuais para o agente.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from neo.services.active_context import (
    count_task_commits,
    get_current_branch,
    resolve_active_task_id,
)


@dataclass(frozen=True)
class RoleDefinition:
    """Metadados de um papel de agente especializado."""

    id: str
    title: str
    description: str
    allows_code_edits: bool
    context_type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


ROLE_CODE = "code"
ROLE_REFINE = "refine"
ROLE_REVIEW_PR = "review-pr"
ROLE_REVIEW_TASK = "review-task"

SUPPORTED_AGENT_ROLES: tuple[str, ...] = (
    ROLE_CODE,
    ROLE_REFINE,
    ROLE_REVIEW_PR,
    ROLE_REVIEW_TASK,
)

DEFAULT_AGENT_ROLE: str = ROLE_CODE

_ROLE_DEFINITIONS: dict[str, RoleDefinition] = {
    ROLE_CODE: RoleDefinition(
        id=ROLE_CODE,
        title="Codificador",
        description="Implementação técnica de especificações, refatoração e resolução de bugs conforme a spec ativa.",
        allows_code_edits=True,
        context_type="Spec ativa e código-fonte do repositório",
    ),
    ROLE_REFINE: RoleDefinition(
        id=ROLE_REFINE,
        title="Refinador de Demandas",
        description="Análise e refinamento de histórias do Shortcut, definição de critérios de aceite Given/When/Then e preparação da spec.",
        allows_code_edits=False,
        context_type="Demanda ativa (Shortcut) e requisitos de negócio",
    ),
    ROLE_REVIEW_PR: RoleDefinition(
        id=ROLE_REVIEW_PR,
        title="Revisor de PR",
        description="Revisão técnica de diffs, commits da branch, cobertura de testes, segurança e conformidade arquitetural.",
        allows_code_edits=False,
        context_type="Commits da branch e git diff em relação à base",
    ),
    ROLE_REVIEW_TASK: RoleDefinition(
        id=ROLE_REVIEW_TASK,
        title="Auditor de DoD",
        description="Auditoria de critérios de aceite (AC-N), suíte de testes e checklist da Definition of Done antes do fechamento.",
        allows_code_edits=False,
        context_type="Definition of Done, suíte de testes e spec",
    ),
}


def validate_agent_role(role: str) -> str:
    """Valida se o identificador de papel é suportado (case-insensitive).

    Retorna o identificador canônico ou lança ValueError.
    """
    if not role or not role.strip():
        raise ValueError(
            f"Papel de agente não pode ser vazio. Papéis disponíveis: {', '.join(SUPPORTED_AGENT_ROLES)}."
        )

    norm = role.strip().lower()
    # Mapeamento de sinônimos/aliases comuns
    aliases = {
        "coder": ROLE_CODE,
        "coding": ROLE_CODE,
        "refinador": ROLE_REFINE,
        "task": ROLE_REFINE,
        "tasks": ROLE_REFINE,
        "pr": ROLE_REVIEW_PR,
        "review": ROLE_REVIEW_PR,
        "audit": ROLE_REVIEW_TASK,
        "dod": ROLE_REVIEW_TASK,
    }
    resolved = aliases.get(norm, norm)

    if resolved not in SUPPORTED_AGENT_ROLES:
        valid_list = ", ".join(SUPPORTED_AGENT_ROLES)
        raise ValueError(
            f"Papel de agente '{role}' não é suportado. Papéis disponíveis: {valid_list}."
        )

    return resolved


def get_role_definition(role: str) -> RoleDefinition:
    """Retorna a definição formal do papel validado."""
    valid_id = validate_agent_role(role)
    return _ROLE_DEFINITIONS[valid_id]


def list_role_definitions() -> list[RoleDefinition]:
    """Retorna todas as definições de papéis disponíveis no catálogo."""
    return list(_ROLE_DEFINITIONS.values())


def build_role_prompt(
    role: str,
    *,
    repo_path: Path | None = None,
    task_id: int | None = None,
    story_title: str | None = None,
) -> str | None:
    """Compõe o prompt inicial contextualizado para o papel especificado."""
    valid_role = validate_agent_role(role)
    active_task = task_id if task_id is not None else resolve_active_task_id(repo_path)
    branch = get_current_branch(repo_path)
    commits_count = count_task_commits(active_task, repo_path=repo_path)

    if valid_role == ROLE_REFINE:
        if active_task:
            title_part = f" — '{story_title}'" if story_title else ""
            return (
                f"Você é o Agente de Refinamento de Demandas do Neo. "
                f"Foco exclusivo na demanda ativa #{active_task}{title_part} na branch '{branch}'. "
                f"Analise os requisitos, detalhe os critérios de aceite (Given/When/Then), "
                f"decomponha em tasks atômicas e estruture a spec SDD. "
                f"ATENÇÃO: Não altere código de produção diretamente."
            )
        return (
            "Você é o Agente de Refinamento de Demandas do Neo. "
            "Nenhuma demanda ativa foi vinculada a este repositório. "
            "Qual história, tema ou funcionalidade você deseja analisar e refinar hoje?"
        )

    if valid_role == ROLE_REVIEW_PR:
        task_info = f" da demanda #{active_task}" if active_task else ""
        return (
            f"Você é o Agente Revisor de Pull Requests e Commits do Neo. "
            f"Revise as alterações realizadas na branch '{branch}' ({commits_count} commit(s){task_info}). "
            f"Avalie a conformidade com a spec, qualidade de código, boas práticas, segurança "
            f"e cobertura de testes. Emita um parecer detalhado com pontos fortes e sugestões de melhoria."
        )

    if valid_role == ROLE_REVIEW_TASK:
        task_info = f" #{active_task}" if active_task else ""
        return (
            f"Você é o Agente Auditor de Definition of Done do Neo. "
            f"Inspecione a demanda ativa{task_info} e a branch '{branch}'. "
            f"Valide se todos os critérios de aceite (AC-N) da spec foram cumpridos, "
            f"se a suíte de testes está verde, se a cobertura atende ao mínimo e se não há "
            f"desvios de especificação pendentes antes do fechamento."
        )

    # ROLE_CODE: se houver task ativa, sugere contexto breve
    if active_task:
        title_part = f" ('{story_title}')" if story_title else ""
        return (
            f"Iniciando sessão de codificação para a demanda #{active_task}{title_part} "
            f"na branch '{branch}' ({commits_count} commit(s) vinculados)."
        )

    return None
