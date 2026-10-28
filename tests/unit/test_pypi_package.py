"""Testes unitários de aceite para a feature 0013 — pacote PyPI (`neo-cli`), limpeza de estrutura e workflow de publicação."""

import subprocess
import tomllib
import zipfile
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def test_AC_1_unnecessary_dirs_removed():
    """AC-1: Pastas de editores não utilizados e spec fictícia de exemplo não existem no repositório."""
    removed_paths = [
        PROJECT_ROOT / ".cursor",
        PROJECT_ROOT / ".windsurf",
        PROJECT_ROOT / ".spec-driven",
        PROJECT_ROOT / ".github" / "prompts",
        PROJECT_ROOT / ".github" / "copilot-instructions.md",
        PROJECT_ROOT / "specs" / "0001-exemplo-cota-de-uso",
        PROJECT_ROOT / "src" / "README.md",
    ]
    for path in removed_paths:
        assert not path.exists(), f"Caminho desnecessário ainda existe: {path}"


def test_AC_2_pyproject_pypi_metadata():
    """AC-2: `pyproject.toml` define `name = 'neo-cmd'`, `license = 'MIT'`, `module-name = 'neo'` e URLs do PyPI."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.exists()

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    assert project.get("name") == "neo-cmd"
    assert project.get("license") == "MIT"
    assert project.get("readme") == "README.md"
    assert project.get("scripts", {}).get("neo") == "neo.cli:app"
    assert "keywords" in project and len(project["keywords"]) >= 3
    assert "classifiers" in project and len(project["classifiers"]) >= 3

    urls = project.get("urls", {})
    assert "Homepage" in urls
    assert "Documentation" in urls
    assert "Repository" in urls

    uv_backend = data.get("tool", {}).get("uv", {}).get("build-backend", {})
    assert uv_backend.get("module-name") == "neo"


def test_AC_2_wheel_registers_standalone_neo_entrypoint(tmp_path: Path):
    """AC-2: O wheel compilado para o PyPI registra `neo = neo.cli:app` em console_scripts (roda direto como `neo`)."""
    res = subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Falha ao construir wheel: {res.stderr}"

    wheels = list(tmp_path.glob("neo_cmd-*.whl"))
    assert len(wheels) == 1

    with zipfile.ZipFile(wheels[0], "r") as zf:
        ep_files = [name for name in zf.namelist() if name.endswith("entry_points.txt")]
        assert len(ep_files) == 1
        ep_content = zf.read(ep_files[0]).decode("utf-8")

    assert "[console_scripts]" in ep_content
    assert "neo = neo.cli:app" in ep_content


def test_AC_3_readme_is_concise_and_pypi_ready():
    """AC-3: `README.md` é resumido, menciona instalação do `neo-cmd` e aponta para a documentação completa."""
    readme_path = PROJECT_ROOT / "README.md"
    content = readme_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    assert len(lines) <= 130, f"README.md deve ser resumido (atual: {len(lines)} linhas)"
    assert "neo-cmd" in content
    assert "https://thalisonwilker.github.io/neo/" in content
    assert "MIT" in content


def test_AC_4_publish_workflow_valid():
    """AC-4: Workflow `.github/workflows/publish.yml` constrói com `uv build` e publica via OIDC."""
    publish_file = PROJECT_ROOT / ".github" / "workflows" / "publish.yml"
    assert publish_file.exists(), ".github/workflows/publish.yml deve existir"

    with publish_file.open("r", encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    on_triggers = workflow.get("on") or workflow.get(True) or {}
    assert "release" in on_triggers
    assert "push" in on_triggers
    assert "v*" in on_triggers["push"].get("tags", [])
    assert "workflow_dispatch" in on_triggers

    jobs = workflow.get("jobs", {})
    assert "build" in jobs
    assert "publish-pypi" in jobs

    build_steps = jobs["build"].get("steps", [])
    build_runs = " ".join(s.get("run", "") for s in build_steps if "run" in s)
    assert "uv build" in build_runs

    publish_job = jobs["publish-pypi"]
    assert "build" in publish_job.get("needs", [])
    assert publish_job.get("permissions", {}).get("id-token") == "write"
    assert publish_job.get("environment", {}).get("name") == "pypi"

    publish_uses = [s.get("uses", "") for s in publish_job.get("steps", []) if "uses" in s]
    assert any("gh-action-pypi-publish" in u for u in publish_uses)
