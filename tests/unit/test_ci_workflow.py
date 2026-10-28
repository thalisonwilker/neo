"""Testes automatizados para validação do GitHub Actions Workflow de CI/CD e Deploy."""

from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def test_AC_4_workflow_syntax_and_triggers():
    """Valida AC-4: Sintaxe YAML válida e triggers corretos em ci.yml."""
    ci_file = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    assert ci_file.exists(), ".github/workflows/ci.yml deve existir"

    with open(ci_file, "r", encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    # Triggers
    on_triggers = workflow.get("on") or workflow.get(True) or {}
    assert "push" in on_triggers
    assert "main" in on_triggers["push"].get("branches", [])
    assert "pull_request" in on_triggers
    assert "main" in on_triggers["pull_request"].get("branches", [])


def test_AC_1_quality_gates_jobs():
    """Valida AC-1: Presença e passos de auditoria SDD e quality gates."""
    ci_file = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    with open(ci_file, "r", encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    jobs = workflow.get("jobs", {})
    assert "audit" in jobs, "Job 'audit' deve estar definido"
    assert "quality" in jobs, "Job 'quality' deve estar definido"

    quality_job = jobs["quality"]
    steps = quality_job.get("steps", [])
    step_runs = [s.get("run", "") for s in steps if "run" in s]
    step_runs_str = " ".join(step_runs)

    assert "ruff check" in step_runs_str
    assert "ruff format --check" in step_runs_str
    assert "mypy src" in step_runs_str
    assert "--cov-fail-under=80" in step_runs_str


def test_AC_2_deploy_docs_job():
    """Valida AC-2: Configuração e permissões do deploy no GitHub Pages."""
    ci_file = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    with open(ci_file, "r", encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    jobs = workflow.get("jobs", {})
    assert "deploy-docs" in jobs, "Job 'deploy-docs' deve estar definido"

    deploy_job = jobs["deploy-docs"]
    needs = deploy_job.get("needs", [])
    assert "quality" in needs
    assert "audit" in needs

    permissions = deploy_job.get("permissions", {})
    assert permissions.get("pages") == "write"
    assert permissions.get("id-token") == "write"

    steps = deploy_job.get("steps", [])
    step_uses = [s.get("uses", "") for s in steps if "uses" in s]
    step_runs = [s.get("run", "") for s in steps if "run" in s]
    step_runs_str = " ".join(step_runs)

    assert any("upload-pages-artifact" in u for u in step_uses)
    assert any("deploy-pages" in u for u in step_uses)
    assert "mkdocs build --strict" in step_runs_str


def test_AC_3_mkdocs_site_url():
    """Valida AC-3: Configuração do site_url canônico do GitHub Pages no mkdocs.yml."""
    mkdocs_file = PROJECT_ROOT / "mkdocs.yml"
    with open(mkdocs_file, "r", encoding="utf-8") as f:
        config = yaml.unsafe_load(f)

    site_url = config.get("site_url", "")
    assert site_url == "https://thalisonwilker.github.io/neo/"
