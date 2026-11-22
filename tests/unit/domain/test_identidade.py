"""Testes unitarios do dominio Identidade (0037 tarefa 2, AC-3, AC-4, AC-6, AC-7, AC-8)."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from neo.domain.identidade import (
    DadosInvalidosError,
    Email,
    IdentidadeExterna,
    MetaSemanal,
    NomeDeExibicao,
    NomeDoEspaco,
    PrimeiroAcessoJaConcluidoError,
    PrimeiroAcessoPendenteError,
    TipoEspaco,
    TokenInvalidoError,
    Usuario,
)


def test_dominio_identidade_nao_importa_frameworks_ou_io() -> None:
    """Regra de dependencias: domain/ nao importa frameworks nem outras camadas."""
    domain_dir = Path(__file__).resolve().parents[3] / "src" / "neo" / "domain"
    proibidos = {
        "fastapi",
        "starlette",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "pydantic_settings",
        "httpx",
        "jwt",
        "typer",
        "rich",
    }
    for py_file in domain_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    raiz = alias.name.split(".")[0]
                    assert raiz not in proibidos
                    assert not alias.name.startswith("neo.infrastructure")
                    assert not alias.name.startswith("neo.application")
                    assert not alias.name.startswith("neo.interfaces")
            elif isinstance(node, ast.ImportFrom) and node.module:
                raiz = node.module.split(".")[0]
                assert raiz not in proibidos
                assert not node.module.startswith("neo.infrastructure")
                assert not node.module.startswith("neo.application")
                assert not node.module.startswith("neo.interfaces")


def test_AC_3_email_normaliza_mascara_e_rejeita_invalidos() -> None:
    """AC-3 e AC-9: e-mail normalizado em minusculas, validado e mascarado corretamente."""
    email = Email("  Thalyson.Dev@Gmail.com  ")
    assert email.valor == "thalyson.dev@gmail.com"
    assert str(email) == "thalyson.dev@gmail.com"
    assert email.mascarado() == "t***@gmail.com"

    for invalido in ("", "   ", "sem-arroba", "@dominio.com", "user@", "user@dominio", "a b@x.com"):
        with pytest.raises(DadosInvalidosError) as exc_info:
            Email(invalido)
        assert exc_info.value.campo == "email"

    muito_longo = f"{'a' * 250}@b.co"
    with pytest.raises(DadosInvalidosError):
        Email(muito_longo)


def test_AC_4_identidade_externa_rejeita_vazia() -> None:
    """AC-4: IdentidadeExterna exige identificador nao vazio apos strip."""
    identidade = IdentidadeExterna("  user_2abc  ")
    assert identidade.clerk_user_id == "user_2abc"

    for invalida in ("", "   "):
        with pytest.raises(TokenInvalidoError):
            IdentidadeExterna(invalida)


def test_AC_7_limites_nome_exibicao_nome_espaco_e_tipos() -> None:
    """AC-7: remove espacos nas pontas, valida limites (1-60 / 1-100, ver 0040 AC-6) e tipos fixos."""
    assert NomeDeExibicao("  A  ").valor == "A"
    assert len(NomeDeExibicao("x" * 60).valor) == 60
    for invalido in ("", "   ", "x" * 61):
        with pytest.raises(DadosInvalidosError) as exc_info:
            NomeDeExibicao(invalido)
        assert exc_info.value.campo == "nome_exibicao"

    assert NomeDoEspaco("  N  ").valor == "N"
    assert len(NomeDoEspaco("y" * 100).valor) == 100
    for invalido in ("", "   ", "y" * 101):
        with pytest.raises(DadosInvalidosError) as exc_info:
            NomeDoEspaco(invalido)
        assert exc_info.value.campo == "espaco.nome"

    for tipo_valido in ("trabalho", "estudos", "hobbies", "pessoal", "  trabalho  "):
        assert isinstance(TipoEspaco.parse(tipo_valido), TipoEspaco)

    for tipo_invalido in ("", "TRABALHO", "lazer", "outro"):
        with pytest.raises(DadosInvalidosError) as exc_info:
            TipoEspaco.parse(tipo_invalido)
        assert exc_info.value.campo == "espaco.tipo"


def test_AC_6_e_AC_8_ciclo_primeiro_acesso_usuario() -> None:
    """AC-6 e AC-8: registrar nasce pendente, conclui uma vez com 1 Espaco e bloqueia repeticao."""
    usuario = Usuario.registrar(
        identidade=IdentidadeExterna("user_123"),
        email=Email("Thalyson@Example.com"),
    )
    assert usuario.primeiro_acesso_concluido is False
    assert usuario.nome_exibicao is None
    assert usuario.espacos == []

    espaco = usuario.concluir_primeiro_acesso(
        nome_exibicao=NomeDeExibicao("  Thalyson  "),
        nome_espaco=NomeDoEspaco("  Neo  "),
        tipo_espaco=TipoEspaco.TRABALHO,
    )
    assert usuario.primeiro_acesso_concluido is True
    assert usuario.nome_exibicao == NomeDeExibicao("Thalyson")
    assert len(usuario.espacos) == 1
    assert usuario.espacos[0] == espaco
    assert espaco.usuario_id == usuario.id
    assert espaco.nome == NomeDoEspaco("Neo")
    assert espaco.tipo is TipoEspaco.TRABALHO

    with pytest.raises(PrimeiroAcessoJaConcluidoError) as exc_info:
        usuario.concluir_primeiro_acesso(
            nome_exibicao=NomeDeExibicao("Outro"),
            nome_espaco=NomeDoEspaco("Outro"),
            tipo_espaco=TipoEspaco.PESSOAL,
        )
    assert exc_info.value.codigo == "primeiro_acesso_ja_concluido"


# --- 0040: criar Espaco ---------------------------------------------------------------


def _usuario_com_primeiro_acesso() -> Usuario:
    usuario = Usuario.registrar(IdentidadeExterna("user_0040"), Email("dev@neo.app"))
    usuario.concluir_primeiro_acesso(
        nome_exibicao=NomeDeExibicao("Thalyson"),
        nome_espaco=NomeDoEspaco("Neo"),
        tipo_espaco=TipoEspaco.TRABALHO,
    )
    return usuario


def test_0040_AC_3_nome_do_espaco_aceita_ate_100_caracteres_apos_trim() -> None:
    assert NomeDoEspaco("  " + "z" * 100 + "  ").valor == "z" * 100
    with pytest.raises(DadosInvalidosError) as exc_info:
        NomeDoEspaco("z" * 101)
    assert exc_info.value.campo == "espaco.nome"


@pytest.mark.parametrize("valor", [1, 30, 168])
def test_0040_AC_3_meta_semanal_valida(valor: int) -> None:
    assert MetaSemanal(valor).valor == valor


@pytest.mark.parametrize("valor", [0, -1, 169, 12.5, "12", True, None])
def test_0040_AC_3_meta_semanal_invalida(valor: object) -> None:
    with pytest.raises(DadosInvalidosError) as exc_info:
        MetaSemanal(valor)  # type: ignore[arg-type]
    assert exc_info.value.campo == "meta_semanal"


@pytest.mark.parametrize(
    ("tipo", "meta"),
    [
        (TipoEspaco.TRABALHO, 30),
        (TipoEspaco.ESTUDOS, 10),
        (TipoEspaco.HOBBIES, 8),
        (TipoEspaco.PESSOAL, 8),
    ],
)
def test_0040_AC_2_meta_sugerida_por_tipo(tipo: TipoEspaco, meta: int) -> None:
    assert tipo.meta_sugerida == meta
    assert MetaSemanal.sugerida(tipo) == MetaSemanal(meta)


def test_0040_AC_1_criar_espaco_com_meta_e_agentes() -> None:
    usuario = _usuario_com_primeiro_acesso()
    espaco = usuario.criar_espaco(
        nome=NomeDoEspaco("  Faculdade  "),
        tipo=TipoEspaco.ESTUDOS,
        meta_semanal=MetaSemanal(12),
        agentes_sugeridos=True,
    )
    assert espaco.nome == NomeDoEspaco("Faculdade")
    assert espaco.tipo is TipoEspaco.ESTUDOS
    assert espaco.meta_semanal == MetaSemanal(12)
    assert espaco.agentes_sugeridos is True
    assert espaco.usuario_id == usuario.id
    assert usuario.espacos[-1] == espaco
    assert len(usuario.espacos) == 2


def test_0040_AC_2_criar_espaco_sem_meta_usa_sugerida_e_sem_agentes() -> None:
    usuario = _usuario_com_primeiro_acesso()
    espaco = usuario.criar_espaco(nome=NomeDoEspaco("Oficina"), tipo=TipoEspaco.HOBBIES)
    assert espaco.meta_semanal == MetaSemanal(8)
    assert espaco.agentes_sugeridos is False


def test_0040_nomes_repetidos_sao_permitidos() -> None:
    usuario = _usuario_com_primeiro_acesso()
    a = usuario.criar_espaco(nome=NomeDoEspaco("Neo"), tipo=TipoEspaco.TRABALHO)
    assert a.nome == usuario.espacos[0].nome
    assert a.id != usuario.espacos[0].id


def test_0040_AC_4_criar_espaco_exige_primeiro_acesso() -> None:
    usuario = Usuario.registrar(IdentidadeExterna("user_pendente"), Email("p@neo.app"))
    with pytest.raises(PrimeiroAcessoPendenteError) as exc_info:
        usuario.criar_espaco(nome=NomeDoEspaco("X"), tipo=TipoEspaco.PESSOAL)
    assert exc_info.value.codigo == "primeiro_acesso_pendente"
    assert usuario.espacos == []


def test_0040_AC_6_espaco_do_primeiro_acesso_nasce_com_meta_sugerida() -> None:
    usuario = Usuario.registrar(IdentidadeExterna("user_pa"), Email("pa@neo.app"))
    espaco = usuario.concluir_primeiro_acesso(
        nome_exibicao=NomeDeExibicao("Ana"),
        nome_espaco=NomeDoEspaco("e" * 100),
        tipo_espaco=TipoEspaco.ESTUDOS,
    )
    assert espaco.meta_semanal == MetaSemanal(10)
    assert espaco.agentes_sugeridos is False
