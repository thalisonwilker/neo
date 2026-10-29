"""Adaptador para o Google Antigravity CLI (`agy`)."""

from __future__ import annotations

import signal
import subprocess
from pathlib import Path
from typing import Any

from neo.config import (
    DEFAULT_AGENT_ADAPTER,
    DEFAULT_AGENT_COMMAND,
    SUPPORTED_AGENT_ADAPTERS,
    SUPPORTED_SDD_PROVIDERS,
    ExitCode,
)


class UnsupportedAgentCombinationError(Exception):
    """Exceção para combinações de agente e provedor SDD não suportadas (código 5)."""

    exit_code: int = int(ExitCode.UNSUPPORTED)

    def __init__(self, message: str, *, suggestion: str | None = None) -> None:
        final_msg = f"{message} Alternativa sugerida: {suggestion}" if suggestion else message
        super().__init__(final_msg)
        self.suggestion = suggestion


class AntigravityAdapter:
    """Adaptador oficial do Google Antigravity CLI no Neo."""

    adapter_id: str = DEFAULT_AGENT_ADAPTER
    external_spec_kit_key: str = "agy"
    default_command: str = DEFAULT_AGENT_COMMAND
    supported_sdd_providers: tuple[str, ...] = SUPPORTED_SDD_PROVIDERS

    @classmethod
    def validate_compatibility(cls, adapter: str, sdd_provider: str) -> None:
        """Valida se a combinação de adaptador e provedor SDD é suportada antes de alterar arquivos ou iniciar sessão."""
        norm_adapter = adapter.strip().lower()
        norm_sdd = sdd_provider.strip().lower()

        if norm_adapter not in SUPPORTED_AGENT_ADAPTERS:
            valid_adapters = ", ".join(SUPPORTED_AGENT_ADAPTERS)
            raise UnsupportedAgentCombinationError(
                f"O adaptador de agente '{adapter}' não é suportado neste incremento.",
                suggestion=f"Use `--agent {DEFAULT_AGENT_ADAPTER}` (adaptadores suportados: {valid_adapters}).",
            )

        if norm_sdd not in cls.supported_sdd_providers:
            valid_sdds = ", ".join(cls.supported_sdd_providers)
            raise UnsupportedAgentCombinationError(
                f"A combinação do agente '{norm_adapter}' com o provedor SDD '{sdd_provider}' não é suportada.",
                suggestion=f"Selecione um provedor SDD compatível: {valid_sdds}.",
            )

    @classmethod
    def build_run_args(
        cls,
        executable_path: str,
        model: str | None = None,
        initial_prompt: str | None = None,
    ) -> list[str]:
        """Constrói a lista estruturada de argumentos para iniciar o Antigravity CLI (sem shell=True)."""
        args: list[str] = [executable_path]
        if model and model.strip():
            args.extend(["--model", model.strip()])
        if initial_prompt and initial_prompt.strip():
            args.extend(["--prompt-interactive", initial_prompt.strip()])
        return args

    @classmethod
    def run_interactive_session(cls, args: list[str], cwd: Path) -> int:
        """Inicia uma sessão interativa do agente no diretório especificado com repasse de sinais e limpeza de órfãos."""
        target_dir = cwd.expanduser().resolve()
        if not target_dir.exists() or not target_dir.is_dir():
            raise FileNotFoundError(f"Diretório de trabalho não encontrado: '{cwd}'.")

        proc = subprocess.Popen(args, cwd=str(target_dir), shell=False)

        prev_sigint = signal.getsignal(signal.SIGINT)
        prev_sigterm = signal.getsignal(signal.SIGTERM)
        interrupted_sig: int | None = None

        def _forward_signal(signum: int, _frame: Any) -> None:
            nonlocal interrupted_sig
            interrupted_sig = signum
            if proc.poll() is None:
                try:
                    proc.send_signal(signum)
                except OSError:
                    pass

        try:
            signal.signal(signal.SIGINT, _forward_signal)
            signal.signal(signal.SIGTERM, _forward_signal)
            try:
                return_code = proc.wait()
            except KeyboardInterrupt:
                interrupted_sig = signal.SIGINT
                if proc.poll() is None:
                    try:
                        proc.send_signal(signal.SIGINT)
                    except OSError:
                        pass
                try:
                    return_code = proc.wait(timeout=3.0)
                except subprocess.TimeoutExpired:
                    proc.terminate()
                    try:
                        return_code = proc.wait(timeout=2.0)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        return_code = proc.wait()
        finally:
            signal.signal(signal.SIGINT, prev_sigint)
            signal.signal(signal.SIGTERM, prev_sigterm)
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()

        if interrupted_sig is not None and return_code == 0:
            return 130
        return return_code
