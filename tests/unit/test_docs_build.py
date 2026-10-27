"""Testes automatizados para validação da documentação MkDocs e infraestrutura Docker."""

import subprocess
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def test_AC_1_mkdocs_config():
    """Valida AC-1: Configuração do MkDocs com tema Material, paleta e extensões PyMdown."""
    mkdocs_file = PROJECT_ROOT / "mkdocs.yml"
    assert mkdocs_file.exists(), "mkdocs.yml deve existir na raiz do projeto"

    with open(mkdocs_file, "r", encoding="utf-8") as f:
        config = yaml.unsafe_load(f)

    # Tema Material
    theme = config.get("theme", {})
    assert theme.get("name") == "material"
    features = theme.get("features", [])
    assert "navigation.tabs" in features
    assert "navigation.sections" in features
    assert "navigation.top" in features

    # Paleta de cores claro e escuro (estilo HTTPX)
    palette = theme.get("palette", [])
    assert len(palette) >= 2
    schemes = [p.get("scheme") for p in palette]
    assert "default" in schemes
    assert "slate" in schemes

    # Extensões PyMdown e Admonition
    extensions = config.get("markdown_extensions", [])
    ext_names = [next(iter(e.keys())) if isinstance(e, dict) else e for e in extensions]
    assert "admonition" in ext_names
    assert "pymdownx.superfences" in ext_names
    assert "pymdownx.tabbed" in ext_names
    assert "pymdownx.highlight" in ext_names

    # Suporte a diagramas Mermaid via custom_fences
    superfences_cfg = next(
        (
            e["pymdownx.superfences"]
            for e in extensions
            if isinstance(e, dict) and "pymdownx.superfences" in e
        ),
        {},
    )
    custom_fences = superfences_cfg.get("custom_fences", [])
    assert any(cf.get("name") == "mermaid" for cf in custom_fences if isinstance(cf, dict))


def test_AC_2_docs_structure_and_pages():
    """Valida AC-2: Estrutura completa e páginas de navegação do portal."""
    docs_dir = PROJECT_ROOT / "docs"
    assert (docs_dir / "index.md").exists()
    assert (docs_dir / "getting-started.md").exists()
    assert (docs_dir / "configuration.md").exists()
    assert (docs_dir / "cli" / "index.md").exists()
    assert (docs_dir / "cli" / "workspace.md").exists()
    assert (docs_dir / "cli" / "repo.md").exists()
    assert (docs_dir / "cli" / "commits.md").exists()
    assert (docs_dir / "cli" / "story.md").exists()
    assert (docs_dir / "architecture.md").exists()


def test_AC_3_dockerfile_docs():
    """Valida AC-3: Dockerfile dedicado para documentação."""
    dockerfile = PROJECT_ROOT / "Dockerfile.docs"
    assert dockerfile.exists()
    content = dockerfile.read_text(encoding="utf-8")
    assert "mkdocs-material" in content
    assert "EXPOSE 8000" in content
    assert "0.0.0.0:8000" in content


def test_AC_4_docker_compose_docs():
    """Valida AC-4: Orquestração conteinerizada via Docker Compose."""
    compose_file = PROJECT_ROOT / "docker-compose.docs.yml"
    assert compose_file.exists()
    with open(compose_file, "r", encoding="utf-8") as f:
        compose_data = yaml.safe_load(f)

    services = compose_data.get("services", {})
    assert "docs" in services
    docs_service = services["docs"]
    assert "8000:8000" in docs_service.get("ports", [])
    volumes = docs_service.get("volumes", [])
    assert any("mkdocs.yml" in str(v) for v in volumes)
    assert any("docs" in str(v) for v in volumes)


def test_AC_5_pyproject_docs_dependency_group():
    """Valida AC-5: Suporte a execução local com grupo docs no pyproject.toml."""
    pyproject = PROJECT_ROOT / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text(encoding="utf-8")
    assert "[dependency-groups]" in content
    assert "mkdocs-material" in content
    assert "pymdown-extensions" in content


def test_AC_6_mkdocs_strict_build():
    """Valida AC-6: Compilação estrita da documentação sem links quebrados."""
    res = subprocess.run(
        ["uv", "run", "--group", "docs", "mkdocs", "build", "--strict"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Falha no mkdocs build --strict:\n{res.stderr}\n{res.stdout}"
