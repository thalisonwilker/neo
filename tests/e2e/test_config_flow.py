import json
import os
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from neo.cli import app

runner = CliRunner()


def test_AC_1_help_and_version():
    """AC-1: neo --help exibe descrição e comandos; neo --version exibe versão."""
    res_help = runner.invoke(app, ["--help"])
    assert res_help.exit_code == 0
    assert "Neo — Sua vida organizada, a um comando de distância." in res_help.output

    res_ver = runner.invoke(app, ["--version"])
    assert res_ver.exit_code == 0
    assert "0.1.1" in res_ver.output


def test_AC_2_and_AC_3_auth_set_and_get(tmp_path: Path):
    """AC-2 e AC-3: Configurar credencial via CLI e consultar valor mascarado."""
    stored: dict[str, str] = {}

    def mock_set(service, username, password):
        stored[username] = password

    def mock_get(service, username):
        return stored.get(username)

    with (
        patch("keyring.set_password", side_effect=mock_set),
        patch("keyring.get_password", side_effect=mock_get),
        patch.dict(os.environ, {}, clear=True),
    ):
        # 1. Get em serviço não configurado deve falhar (código 1)
        res_not_found = runner.invoke(app, ["git", "config", "auth", "get", "bitbucket"])
        assert res_not_found.exit_code == 1

        # 2. Set token com flag
        res_set = runner.invoke(
            app, ["git", "config", "auth", "set", "bitbucket", "--token", "secret-bitbucket-token"]
        )
        assert res_set.exit_code == 0
        assert "configurado com sucesso" in res_set.output

        # 3. Get token (deve estar mascarado, nunca o texto puro)
        res_get = runner.invoke(app, ["git", "config", "auth", "get", "bitbucket"])
        assert res_get.exit_code == 0
        assert "secret-bitbucket-token" not in res_get.output
        assert "oken" in res_get.output

        # 4. Set token com prompt interativo
        res_set_prompt = runner.invoke(app, ["tasks", "config", "set"], input="interactive-token\n")
        assert res_set_prompt.exit_code == 0
        assert "configurado com sucesso" in res_set_prompt.output


def test_AC_2_auth_set_invalid_service_and_json_error():
    """AC-2: Tratamento de erros no auth set."""
    # Serviço inválido
    res = runner.invoke(app, ["git", "config", "auth", "set", "invalido", "--token", "abc"])
    assert res.exit_code == 1
    assert "não suportado" in res.output

    # Sem token em modo --json
    res_json_missing = runner.invoke(app, ["--json", "git", "config", "auth", "set", "bitbucket"])
    assert res_json_missing.exit_code == 1
    data = json.loads(res_json_missing.output)
    assert data["status"] == "error"


def test_AC_3_auth_get_invalid_service():
    """AC-3: Erro ao consultar serviço inválido."""
    res = runner.invoke(app, ["git", "config", "auth", "get", "invalido"])
    assert res.exit_code == 1
    assert "não suportado" in res.output


def test_AC_4_precedence_env_var():
    """AC-4: Variável de ambiente tem prioridade máxima."""
    with (
        patch.dict(os.environ, {"BITBUCKET_TOKEN": "token-from-env-var"}),
        patch("keyring.get_password", return_value="token-from-keyring"),
    ):
        res = runner.invoke(app, ["--json", "git", "config", "auth", "get", "bitbucket"])
        assert res.exit_code == 0
        data = json.loads(res.output)
        assert data["configured"] is True
        assert data["source"] == "env"


def test_AC_5_json_flag_output():
    """AC-5: A flag global --json gera saída em JSON estruturado estrito."""
    with patch.dict(os.environ, {"SHORTCUT_API_TOKEN": "token-sh-123456"}):
        res = runner.invoke(app, ["--json", "tasks", "config", "get"])
        assert res.exit_code == 0
        data = json.loads(res.output)
        assert data["service"] == "shortcut"
        assert data["configured"] is True
        assert data["source"] == "env"
        assert "masked_token" in data
        assert "token-sh-123456" not in res.output

    # Teste config show --json
    res_show = runner.invoke(app, ["--json", "config", "show"])
    assert res_show.exit_code == 0
    show_data = json.loads(res_show.output)
    assert "services" in show_data
    assert "bitbucket" in show_data["services"]
    assert "shortcut" in show_data["services"]


def test_config_show_human_mode():
    """Testa neo config show renderizando tabela Rich."""
    with patch.dict(os.environ, {"BITBUCKET_TOKEN": "token-12345"}):
        res = runner.invoke(app, ["config", "show"])
        assert res.exit_code == 0
        assert "Status de Autenticação do Neo" in res.output
        assert "bitbucket" in res.output


def test_AC_6_auth_delete():
    """AC-6: Remoção de credencial configurada."""
    stored = {"bitbucket": "token-xyz"}

    def mock_del(service, username):
        stored.pop(username, None)

    with (
        patch("keyring.delete_password", side_effect=mock_del),
        patch("keyring.get_password", side_effect=lambda s, u: stored.get(u)),
    ):
        # Remoção com sucesso
        res_del = runner.invoke(app, ["git", "config", "auth", "delete", "bitbucket"])
        assert res_del.exit_code == 0
        assert "removida com sucesso" in res_del.output
        assert "bitbucket" not in stored

        # Remoção de serviço já inexistente
        res_del_not_found = runner.invoke(app, ["git", "config", "auth", "delete", "bitbucket"])
        assert res_del_not_found.exit_code == 1
        assert "Nenhuma credencial encontrada" in res_del_not_found.output

        # Remoção de serviço inválido
        res_del_invalid = runner.invoke(app, ["git", "config", "auth", "delete", "invalido"])
        assert res_del_invalid.exit_code == 1
