"""Adaptadores para os provedores SDD `spec-driven` e `spec-kit`."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from neo.config import SDDProviderType, validate_sdd_provider
from neo.integrations.agents.antigravity import AntigravityAdapter

SPEC_DRIVEN_AGENTS_MD_TEMPLATE = """# AGENTS.md — Convenções de Spec-Driven Development (SDD)

Este projeto utiliza **Spec-Driven Development (SDD)** integrado ao Google Antigravity CLI (`agy`).

## Fluxo de Trabalho
1. Especifique a funcionalidade em `specs/NNNN-<nome>/spec.md` com critérios `AC-N` em formato Given/When/Then.
2. Decomponha as tarefas em `specs/NNNN-<nome>/tasks.md`.
3. Implemente e valide cada `AC-N` com testes automatizados antes de concluir.
"""

SPEC_DRIVEN_SKILL_TEMPLATE = """---
name: nova-feature
description: Abre e conduz uma nova feature no padrão Spec-Driven Development (SDD) criando spec.md e tasks.md.
---

# Skill: Nova Feature (SDD)

1. Identifique o próximo número sequencial em `specs/NNNN-<slug>/`.
2. Crie `spec.md` com critérios de aceite (`AC-1`, `AC-2`...) em formato Given/When/Then.
3. Crie `tasks.md` mapeando cada task aos critérios `AC-N` e aguarde aprovação antes de implementar.
"""

SPECKIT_CONFIG_TEMPLATE = """# Configuração de integração Spec Kit para Google Antigravity (agy)
[speckit]
integration = "agy"
skills_dir = ".agents/skills"
"""

SPECKIT_SKILLS_TEMPLATES: dict[str, tuple[str, str]] = {
    "speckit-specify": (
        "Cria ou atualiza a especificação da feature no fluxo Spec Kit (/speckit-specify).",
        "# /speckit-specify\n\nDefine os requisitos e critérios de aceite da funcionalidade antes do planejamento técnico.\n",
    ),
    "speckit-plan": (
        "Gera o plano de arquitetura e design técnico a partir da spec (/speckit-plan).",
        "# /speckit-plan\n\nElabora o plano técnico e decisões de arquitetura respeitando a constituição do projeto.\n",
    ),
    "speckit-tasks": (
        "Decompõe o plano em tarefas executáveis e testáveis (/speckit-tasks).",
        "# /speckit-tasks\n\nQuebra o plano técnico em tarefas ordenadas e rastreáveis.\n",
    ),
    "speckit-implement": (
        "Executa a implementação guiada pelas tasks e critérios de aceite (/speckit-implement).",
        "# /speckit-implement\n\nImplementa e verifica cada tarefa aprovada na especificação.\n",
    ),
}


@dataclass
class SDDSetupPlan:
    """Plano de preparação SDD antes de aplicar mudanças no filesystem."""

    provider: SDDProviderType
    adapter: str
    target_dir: Path
    files_to_create: dict[Path, str] = field(default_factory=dict)
    files_preserved: list[Path] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def inspect_project_sdd(target_dir: Path, sdd_provider: str) -> dict[str, Any]:
    """Inspeciona o estado dos artefatos SDD e binários auxiliares no diretório alvo."""
    valid_provider = validate_sdd_provider(sdd_provider)
    resolved_dir = target_dir.expanduser().resolve()

    agents_md = resolved_dir / "AGENTS.md"
    skills_dir = resolved_dir / ".agents" / "skills"
    speckit_dir = resolved_dir / ".speckit"

    discovered_skills: list[str] = []
    if skills_dir.exists() and skills_dir.is_dir():
        for item in sorted(skills_dir.iterdir()):
            if item.is_dir() and (item / "SKILL.md").exists():
                discovered_skills.append(item.name)

    if valid_provider == "spec-driven":
        external_tool = "npx"
        external_tool_path = shutil.which("npx")
        ready = agents_md.exists() and len(discovered_skills) > 0
    else:
        external_tool = "specify"
        external_tool_path = shutil.which("specify")
        has_speckit_skills = any(s.startswith("speckit-") for s in discovered_skills)
        ready = has_speckit_skills or speckit_dir.exists()

    return {
        "provider": valid_provider,
        "target_dir": str(resolved_dir),
        "ready": ready,
        "agents_md_exists": agents_md.exists(),
        "skills_dir_exists": skills_dir.exists(),
        "discovered_skills": discovered_skills,
        "speckit_dir_exists": speckit_dir.exists(),
        "external_tool": external_tool,
        "external_tool_available": external_tool_path is not None,
        "external_tool_path": external_tool_path,
    }


def plan_sdd_setup(
    target_dir: Path,
    sdd_provider: str,
    adapter: str = "antigravity",
) -> SDDSetupPlan:
    """Calcula de forma idempotente os arquivos a criar e os arquivos existentes a preservar."""
    AntigravityAdapter.validate_compatibility(adapter, sdd_provider)
    valid_provider = validate_sdd_provider(sdd_provider)
    resolved_dir = target_dir.expanduser().resolve()

    plan = SDDSetupPlan(
        provider=valid_provider,
        adapter=adapter.strip().lower(),
        target_dir=resolved_dir,
    )

    if valid_provider == "spec-driven":
        agents_md = resolved_dir / "AGENTS.md"
        if agents_md.exists():
            plan.files_preserved.append(agents_md)
        else:
            plan.files_to_create[agents_md] = SPEC_DRIVEN_AGENTS_MD_TEMPLATE

        skills_root = resolved_dir / ".agents" / "skills"
        existing_skill_files = list(skills_root.glob("*/SKILL.md")) if skills_root.exists() else []
        if existing_skill_files:
            for sf in sorted(existing_skill_files):
                plan.files_preserved.append(sf)
        else:
            default_skill = skills_root / "nova-feature" / "SKILL.md"
            plan.files_to_create[default_skill] = SPEC_DRIVEN_SKILL_TEMPLATE

    elif valid_provider == "spec-kit":
        agents_md = resolved_dir / "AGENTS.md"
        if agents_md.exists():
            plan.files_preserved.append(agents_md)
            plan.warnings.append("AGENTS.md existente detectado e preservado sem alterações.")

        speckit_cfg = resolved_dir / ".speckit" / "config.toml"
        if speckit_cfg.exists():
            plan.files_preserved.append(speckit_cfg)
        else:
            plan.files_to_create[speckit_cfg] = SPECKIT_CONFIG_TEMPLATE

        skills_root = resolved_dir / ".agents" / "skills"
        for skill_name, (desc, body) in SPECKIT_SKILLS_TEMPLATES.items():
            skill_path = skills_root / skill_name / "SKILL.md"
            if skill_path.exists():
                plan.files_preserved.append(skill_path)
            else:
                content = f"---\nname: {skill_name}\ndescription: {desc}\n---\n\n{body}"
                plan.files_to_create[skill_path] = content

    return plan


def apply_sdd_setup(plan: SDDSetupPlan) -> dict[str, Any]:
    """Aplica o plano de setup criando apenas os arquivos ausentes e preservando customizações."""
    plan.target_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    for file_path, content in plan.files_to_create.items():
        if file_path.exists():
            if file_path not in plan.files_preserved:
                plan.files_preserved.append(file_path)
            continue
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        created.append(str(file_path.relative_to(plan.target_dir)))

    preserved = [
        str(p.relative_to(plan.target_dir)) if p.is_relative_to(plan.target_dir) else str(p)
        for p in plan.files_preserved
    ]

    return {
        "status": "success",
        "provider": plan.provider,
        "adapter": plan.adapter,
        "target_dir": str(plan.target_dir),
        "created_files": created,
        "preserved_files": preserved,
        "warnings": plan.warnings,
    }
