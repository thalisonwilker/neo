"""Testes automatizados para validação da documentação MkDocs e infraestrutura Docker."""

import subprocess
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class MkDocsLoader(yaml.SafeLoader):
    """SafeLoader customizado que ignora tags python do mkdocs sem tentar importá-las."""


MkDocsLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/",
    lambda loader, suffix, node: (
        loader.construct_scalar(node) if isinstance(node, yaml.ScalarNode) else None
    ),
)


def test_AC_1_mkdocs_config():
    """Valida AC-1: Configuração do MkDocs com tema Material, paleta e extensões PyMdown."""
    mkdocs_file = PROJECT_ROOT / "mkdocs.yml"
    assert mkdocs_file.exists(), "mkdocs.yml deve existir na raiz do projeto"

    with open(mkdocs_file, "r", encoding="utf-8") as f:
        config = yaml.load(f, Loader=MkDocsLoader)

    # Tema Material
    theme = config.get("theme", {})
    assert theme.get("name") == "material"
    assert theme.get("logo") == "assets/neo-logo.jpg"
    assert theme.get("favicon") == "assets/neo-logo.jpg"
    assert "stylesheets/extra.css" in config.get("extra_css", [])
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
    """Valida AC-2: Estrutura completa e páginas de navegação do portal em submenus."""
    docs_dir = PROJECT_ROOT / "docs"
    assert (docs_dir / "index.md").exists()
    assert (docs_dir / "getting-started.md").exists()
    assert (docs_dir / "configuration.md").exists()
    assert (docs_dir / "cli" / "index.md").exists()
    assert (docs_dir / "cli" / "git" / "index.md").exists()
    assert (docs_dir / "cli" / "git" / "config.md").exists()
    assert (docs_dir / "cli" / "git" / "auth.md").exists()
    assert (docs_dir / "cli" / "git" / "workspace.md").exists()
    assert (docs_dir / "cli" / "git" / "repo.md").exists()
    assert (docs_dir / "cli" / "git" / "commits.md").exists()
    assert (docs_dir / "cli" / "git" / "status.md").exists()
    assert (docs_dir / "cli" / "git" / "planejado.md").exists()
    assert (docs_dir / "cli" / "tasks" / "index.md").exists()
    assert (docs_dir / "cli" / "tasks" / "resume.md").exists()
    assert (docs_dir / "cli" / "tasks" / "whoami.md").exists()
    assert (docs_dir / "cli" / "tasks" / "iterations.md").exists()
    assert (docs_dir / "cli" / "tasks" / "list.md").exists()
    assert (docs_dir / "cli" / "tasks" / "search.md").exists()
    assert (docs_dir / "cli" / "tasks" / "show.md").exists()
    assert (docs_dir / "cli" / "tasks" / "analyze.md").exists()
    assert (docs_dir / "cli" / "tasks" / "config.md").exists()
    assert (docs_dir / "cli" / "agent" / "index.md").exists()
    assert (docs_dir / "cli" / "agent" / "config.md").exists()
    assert (docs_dir / "cli" / "agent" / "status.md").exists()
    assert (docs_dir / "cli" / "agent" / "setup.md").exists()
    assert (docs_dir / "cli" / "agent" / "run.md").exists()
    assert (docs_dir / "guias" / "index.md").exists()
    assert (docs_dir / "guias" / "ci-json.md").exists()
    assert (docs_dir / "guias" / "trocar-provedor.md").exists()
    assert (docs_dir / "guias" / "fluxo-diario.md").exists()
    assert (docs_dir / "migration.md").exists()
    assert (docs_dir / "architecture.md").exists()
    assert (docs_dir / "assets" / "neo-logo.jpg").exists()
    assert (docs_dir / "stylesheets" / "extra.css").exists()
    assert (PROJECT_ROOT / "CHANGELOG.md").exists()


def test_AC_9_docs_no_legacy_git_commands():
    """Valida AC-9: Nenhum comando antigo do neo git aparece fora de migration.md."""
    docs_dir = PROJECT_ROOT / "docs"
    forbidden_patterns = [
        "neo git config auth",
        "neo git config set-provider",
        "neo git config get-provider",
        "neo git workspace current",
        "neo git workspace set",
        "neo git config set token",
    ]
    portal_pages = [
        docs_dir / "index.md",
        docs_dir / "getting-started.md",
        docs_dir / "configuration.md",
        docs_dir / "glossary.md",
        docs_dir / "architecture.md",
        docs_dir / "cli" / "index.md",
        docs_dir / "cli" / "git" / "index.md",
        docs_dir / "cli" / "git" / "config.md",
        docs_dir / "cli" / "git" / "auth.md",
        docs_dir / "cli" / "git" / "workspace.md",
        docs_dir / "cli" / "git" / "repo.md",
        docs_dir / "cli" / "git" / "commits.md",
        docs_dir / "cli" / "git" / "status.md",
    ]
    for page in portal_pages:
        content = page.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            assert pattern not in content, f"Padrão legado '{pattern}' encontrado em {page}"

    migration_content = (docs_dir / "migration.md").read_text(encoding="utf-8")
    assert "neo git auth login" in migration_content
    assert "neo git workspace select" in migration_content


def test_AC_16_agent_and_sdd_docs_consistency():
    """Valida AC-16 (0015): Documentação consistente com neo config agent e neo agent."""
    docs_dir = PROJECT_ROOT / "docs" / "cli" / "agent"
    combined_content = (
        (docs_dir / "index.md").read_text(encoding="utf-8")
        + "\n"
        + (docs_dir / "config.md").read_text(encoding="utf-8")
        + "\n"
        + (docs_dir / "status.md").read_text(encoding="utf-8")
        + "\n"
        + (docs_dir / "setup.md").read_text(encoding="utf-8")
        + "\n"
        + (docs_dir / "run.md").read_text(encoding="utf-8")
    )
    for expected in (
        "neo config agent set",
        "neo config agent get",
        "neo config agent list",
        "neo config agent unset",
        "neo agent status",
        "neo agent setup",
        "neo agent run",
        "spec-driven",
        "spec-kit",
        "agy",
    ):
        assert expected in combined_content


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


def test_AC_6_mkdocs_strict_build(tmp_path: Path):
    """Valida AC-6: Compilação estrita da documentação sem links quebrados."""
    site_dir = tmp_path / "site"
    res = subprocess.run(
        [
            "uv",
            "run",
            "--group",
            "docs",
            "mkdocs",
            "build",
            "--strict",
            "--site-dir",
            str(site_dir),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Falha no mkdocs build --strict:\n{res.stderr}\n{res.stdout}"
