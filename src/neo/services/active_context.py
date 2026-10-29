"""Serviço de contexto ativo de trabalho (Git ↔ Tasks/Demandas).

Fornece extração de ID de task via branch, persistência de binding manual
em `.git/neo-context.json` e contagem de commits associados à demanda no repositório.
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONTEXT_FILE_NAME = "neo-context.json"

# Padrões de extração de ID de task a partir do nome da branch:
# 1. sc-1234 ou feature/sc-1234-nome
# 2. story/1234 ou feature/1234-slug ou fix/1234
# 3. Qualquer bloco de dígitos delimitado por / ou - (ex.: 0017-contexto...)
_BRANCH_PATTERNS = [
    re.compile(r"(?:^|[/-])sc-(\d+)(?:[/-]|$)", re.IGNORECASE),
    re.compile(r"(?:^|[/-])(?:story|feature|fix)[/-](\d+)(?:[/-]|$)", re.IGNORECASE),
    re.compile(r"(?:^|[/-])(\d{2,})(?:[/-]|$)", re.IGNORECASE),
]


def extract_task_id_from_branch(branch_name: str | None) -> int | None:
    """Extrai o identificador numérico da task/história a partir do nome da branch.

    Retorna None se a branch for vazia, None ou não contiver padrão reconhecido
    (ex.: 'main', 'master', 'develop', 'docs/refactor-cli').
    """
    if not branch_name:
        return None

    cleaned = branch_name.strip()
    # Ignora branches padrão comuns
    if cleaned.lower() in {"main", "master", "develop", "dev", "trunk"}:
        return None

    for pattern in _BRANCH_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                continue

    return None


def get_git_dir(repo_path: Path | None = None) -> Path | None:
    """Retorna o diretório `.git` do repositório (suportando worktrees e subdiretórios)."""
    base = (repo_path or Path.cwd()).resolve()
    direct_git = base / ".git"
    if direct_git.is_dir():
        return direct_git
    if direct_git.is_file():
        try:
            content = direct_git.read_text(encoding="utf-8").strip()
            if content.startswith("gitdir:"):
                target = Path(content[len("gitdir:") :].strip())
                if not target.is_absolute():
                    target = (base / target).resolve()
                if target.is_dir():
                    return target
        except OSError:
            pass

    cwd = str(repo_path) if repo_path else None
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            raw_git_dir = Path(res.stdout.strip())
            if not raw_git_dir.is_absolute():
                return (base / raw_git_dir).resolve()
            return raw_git_dir.resolve()
    except (subprocess.SubprocessError, OSError) as exc:
        logger.debug("Falha ao obter diretório git: %s", exc)

    return None


def get_context_file_path(repo_path: Path | None = None) -> Path | None:
    """Retorna o caminho do arquivo `.git/neo-context.json` se estiver em um repositório Git."""
    git_dir = get_git_dir(repo_path)
    if git_dir and git_dir.is_dir():
        return git_dir / CONTEXT_FILE_NAME
    return None


def get_bound_task_id(repo_path: Path | None = None) -> int | None:
    """Lê o ID da task manualmente vinculada ao repositório em `.git/neo-context.json`."""
    ctx_file = get_context_file_path(repo_path)
    if not ctx_file or not ctx_file.is_file():
        return None

    try:
        data = json.loads(ctx_file.read_text(encoding="utf-8"))
        task_id = data.get("active_task_id")
        if task_id is not None:
            return int(task_id)
    except (json.JSONDecodeError, OSError, ValueError, TypeError) as exc:
        logger.debug("Erro ao ler %s: %s", ctx_file, exc)

    return None


def bind_task_id(story_id: int, repo_path: Path | None = None) -> Path:
    """Vincula manualmente uma task ao repositório salvando em `.git/neo-context.json`.

    Lança ValueError se não estiver dentro de um repositório Git.
    """
    ctx_file = get_context_file_path(repo_path)
    if not ctx_file:
        raise ValueError("O diretório atual não é um repositório Git válido.")

    payload: dict[str, Any] = {
        "active_task_id": int(story_id),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    ctx_file.parent.mkdir(parents=True, exist_ok=True)
    ctx_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return ctx_file


def unbind_task_id(repo_path: Path | None = None) -> bool:
    """Remove a vinculação manual de task em `.git/neo-context.json`.

    Retorna True se o arquivo existia e foi removido, False caso contrário.
    """
    ctx_file = get_context_file_path(repo_path)
    if ctx_file and ctx_file.is_file():
        try:
            ctx_file.unlink()
            return True
        except OSError as exc:
            logger.debug("Falha ao remover %s: %s", ctx_file, exc)
    return False


def get_current_branch(repo_path: Path | None = None) -> str | None:
    """Retorna o nome da branch atual ou None se fora de um repositório Git."""
    cwd = str(repo_path) if repo_path else None
    try:
        res = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            branch = res.stdout.strip()
            return branch if branch else None
    except (subprocess.SubprocessError, OSError):
        pass
    return None


def resolve_active_task_id(repo_path: Path | None = None) -> int | None:
    """Resolve a task ativa com a precedência:

    1. Vínculo manual persistido em `.git/neo-context.json` (`neo tasks bind`)
    2. Inferência automática a partir do nome da branch atual
    """
    bound_id = get_bound_task_id(repo_path)
    if bound_id is not None:
        return bound_id

    current_branch = get_current_branch(repo_path)
    return extract_task_id_from_branch(current_branch)


def _detect_default_branch(repo_path: Path | None = None) -> str:
    """Tenta detectar a branch padrão (main, master) do repositório."""
    cwd = str(repo_path) if repo_path else None
    try:
        # Tenta verificar se origin/main ou main existe
        for candidate in ["main", "master", "develop"]:
            res = subprocess.run(
                ["git", "rev-parse", "--verify", candidate],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0:
                return candidate
    except (subprocess.SubprocessError, OSError):
        pass
    return "main"


def count_task_commits(
    story_id: int | None,
    repo_path: Path | None = None,
    default_branch: str | None = None,
) -> int:
    """Calcula a quantidade de commits vinculados à task ativa no repositório.

    Combina:
    - Commits na branch atual em relação à branch padrão (default_branch..HEAD)
    - Commits que mencionam o ID da story na mensagem (ex.: 'sc-1234', '[1234]', '#1234')
    Retorna 0 se fora de git ou sem commits.
    """
    git_dir = get_git_dir(repo_path)
    if not git_dir:
        return 0

    cwd = str(repo_path) if repo_path else None
    current_branch = get_current_branch(repo_path)
    base_branch = default_branch or _detect_default_branch(repo_path)

    commit_shas: set[str] = set()

    # 1. Se estiver numa branch de feature diferente da base, conta commits da branch
    if current_branch and current_branch != base_branch:
        try:
            res = subprocess.run(
                ["git", "log", f"{base_branch}..HEAD", "--format=%H"],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                for sha in res.stdout.strip().splitlines():
                    if sha.strip():
                        commit_shas.add(sha.strip())
        except (subprocess.SubprocessError, OSError) as exc:
            logger.debug("Falha ao listar commits da branch: %s", exc)

    # 2. Se houver story_id, procura commits no histórico que mencionem o ID
    if story_id is not None:
        patterns = [f"sc-{story_id}", f"story {story_id}", f"#{story_id}", f"{story_id}"]
        for pat in patterns:
            try:
                res = subprocess.run(
                    ["git", "log", f"--grep={pat}", "--format=%H"],
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode == 0 and res.stdout.strip():
                    for sha in res.stdout.strip().splitlines():
                        if sha.strip():
                            commit_shas.add(sha.strip())
            except (subprocess.SubprocessError, OSError) as exc:
                logger.debug("Falha ao buscar commits por grep: %s", exc)

    return len(commit_shas)
