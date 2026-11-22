"""Testes unitarios dos casos de uso de Identidade (0037 tarefa 3, AC-3 a AC-8, AC-10)."""

from __future__ import annotations

import ast
import logging
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

import pytest

from neo.application.identidade import (
    ConcluirPrimeiroAcesso,
    GerenciarListaDePermissao,
    ObterOuCriarUsuario,
)
from neo.domain.identidade import (
    AcessoNaoLiberadoError,
    ClerkIndisponivelError,
    DadosInvalidosError,
    Email,
    EmailAutorizado,
    EmailAutorizadoNaoEncontradoError,
    Espaco,
    IdentidadeExterna,
    PrimeiroAcessoJaConcluidoError,
    TipoEspaco,
    Usuario,
)


class RepoUsuariosEmMemoria:
    """Repositorio fake de Usuarios em memoria para testes de unidade."""

    def __init__(self) -> None:
        self._por_clerk: dict[str, Usuario] = {}

    async def buscar_por_identidade(self, identidade: IdentidadeExterna) -> Usuario | None:
        usuario = self._por_clerk.get(identidade.clerk_user_id)
        return deepcopy(usuario) if usuario is not None else None

    async def criar_ou_obter_existente(self, usuario: Usuario) -> tuple[Usuario, bool]:
        chave = usuario.identidade.clerk_user_id
        if chave in self._por_clerk:
            return deepcopy(self._por_clerk[chave]), False
        copia = deepcopy(usuario)
        self._por_clerk[chave] = copia
        return deepcopy(copia), True

    async def salvar_primeiro_acesso(self, usuario: Usuario, espaco: Espaco) -> Usuario:
        chave = usuario.identidade.clerk_user_id
        atual = self._por_clerk.get(chave)
        if atual is None:
            raise AssertionError("Usuario precisa existir antes do primeiro acesso")
        if atual.primeiro_acesso_concluido:
            raise PrimeiroAcessoJaConcluidoError()
        copia = deepcopy(usuario)
        self._por_clerk[chave] = copia
        return deepcopy(copia)


class RepoListaEmMemoria:
    """Repositorio fake de Lista de permissao em memoria."""

    def __init__(self) -> None:
        self._itens: dict[str, EmailAutorizado] = {}

    async def esta_autorizado(self, email: Email) -> bool:
        return email.valor in self._itens

    async def adicionar(self, email: Email) -> tuple[EmailAutorizado, bool]:
        if email.valor in self._itens:
            return self._itens[email.valor], False
        item = EmailAutorizado(email=email, criado_em=datetime.now(UTC))
        self._itens[email.valor] = item
        return item, True

    async def listar(self) -> list[EmailAutorizado]:
        return [self._itens[k] for k in sorted(self._itens)]

    async def remover(self, email: Email) -> bool:
        return self._itens.pop(email.valor, None) is not None


class LeitorEmailStub:
    """Stub configuravel para LeitorDeEmailExterno."""

    def __init__(self, mapa: dict[str, str] | None = None, indisponivel: bool = False) -> None:
        self.mapa = mapa or {}
        self.indisponivel = indisponivel
        self.chamadas: list[str] = []

    async def obter_email_principal(self, identidade: IdentidadeExterna) -> Email:
        self.chamadas.append(identidade.clerk_user_id)
        if self.indisponivel:
            raise ClerkIndisponivelError()
        return Email(self.mapa[identidade.clerk_user_id])


def test_application_identidade_depende_apenas_do_dominio() -> None:
    """Regra de dependencias: application/ importa apenas domain/ e stdlib."""
    app_dir = Path(__file__).resolve().parents[3] / "src" / "neo" / "application"
    proibidos = {
        "fastapi",
        "starlette",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "httpx",
        "jwt",
        "typer",
    }
    for py_file in app_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] not in proibidos
                    assert not alias.name.startswith("neo.infrastructure")
                    assert not alias.name.startswith("neo.interfaces")
            elif isinstance(node, ast.ImportFrom) and node.module:
                assert node.module.split(".")[0] not in proibidos
                assert not node.module.startswith("neo.infrastructure")
                assert not node.module.startswith("neo.interfaces")


async def test_AC_3_e_AC_5_primeiro_pedido_autorizado_e_reconhecimento_sem_clerk() -> None:
    """AC-3 e AC-5: cria Usuario na 1a chamada e depois retorna sem consultar Clerk nem lista."""
    repo_usuarios = RepoUsuariosEmMemoria()
    repo_lista = RepoListaEmMemoria()
    leitor = LeitorEmailStub({"user_1": "Thalyson@Gmail.com"})
    gerenciar = GerenciarListaDePermissao(repo_lista)
    await gerenciar.permitir("thalyson@gmail.com")

    uc = ObterOuCriarUsuario(repo_usuarios, repo_lista, leitor)
    identidade = IdentidadeExterna("user_1")

    criado = await uc.executar(identidade)
    assert criado.email == Email("thalyson@gmail.com")
    assert criado.primeiro_acesso_concluido is False
    assert criado.nome_exibicao is None
    assert criado.espacos == []
    assert leitor.chamadas == ["user_1"]

    # Remove da lista de permissao depois — Usuario existente continua reconhecido sem ir ao Clerk
    await gerenciar.remover("thalyson@gmail.com")
    reconhecido = await uc.executar(identidade)
    assert reconhecido.id == criado.id
    assert leitor.chamadas == ["user_1"]


async def test_AC_4_email_fora_da_lista_recusado_e_log_mascarado(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """AC-4 e AC-9: recusa acesso nao autorizado, nao grava Usuario e mascara e-mail no log."""
    repo_usuarios = RepoUsuariosEmMemoria()
    repo_lista = RepoListaEmMemoria()
    leitor = LeitorEmailStub({"user_intruso": "intruso@example.com"})
    uc = ObterOuCriarUsuario(repo_usuarios, repo_lista, leitor)

    with (
        caplog.at_level(logging.WARNING, logger="neo.application.identidade"),
        pytest.raises(AcessoNaoLiberadoError),
    ):
        await uc.executar(IdentidadeExterna("user_intruso"))

    assert await repo_usuarios.buscar_por_identidade(IdentidadeExterna("user_intruso")) is None
    assert "intruso@example.com" not in caplog.text
    assert "i***@example.com" in caplog.text


async def test_clerk_indisponivel_nao_grava_usuario() -> None:
    """Borda: falha no Clerk propaga ClerkIndisponivelError sem criar Usuario."""
    repo_usuarios = RepoUsuariosEmMemoria()
    repo_lista = RepoListaEmMemoria()
    leitor = LeitorEmailStub(indisponivel=True)
    uc = ObterOuCriarUsuario(repo_usuarios, repo_lista, leitor)

    with pytest.raises(ClerkIndisponivelError):
        await uc.executar(IdentidadeExterna("user_1"))
    assert await repo_usuarios.buscar_por_identidade(IdentidadeExterna("user_1")) is None


async def test_concorrencia_primeiro_pedido_retorna_usuario_existente() -> None:
    """Borda: se repositorio ja recebeu Usuario de corrida paralela, nao cria duplicata."""
    repo_lista = RepoListaEmMemoria()
    await repo_lista.adicionar(Email("user@example.com"))
    existente = Usuario.registrar(IdentidadeExterna("user_dup"), Email("user@example.com"))

    class RepoComCorrida(RepoUsuariosEmMemoria):
        async def buscar_por_identidade(self, identidade: IdentidadeExterna) -> Usuario | None:
            return None

        async def criar_ou_obter_existente(self, usuario: Usuario) -> tuple[Usuario, bool]:
            return existente, False

    uc = ObterOuCriarUsuario(
        RepoComCorrida(),
        repo_lista,
        LeitorEmailStub({"user_dup": "user@example.com"}),
    )
    resultado = await uc.executar(IdentidadeExterna("user_dup"))
    assert resultado.id == existente.id


async def test_AC_6_AC_7_AC_8_concluir_primeiro_acesso_e_validacoes() -> None:
    """AC-6, AC-7 e AC-8: conclui primeiro acesso uma vez, valida campos e rejeita repeticao."""
    repo_usuarios = RepoUsuariosEmMemoria()
    repo_lista = RepoListaEmMemoria()
    await repo_lista.adicionar(Email("ok@example.com"))
    leitor = LeitorEmailStub({"user_ok": "ok@example.com"})
    obter_ou_criar = ObterOuCriarUsuario(repo_usuarios, repo_lista, leitor)
    concluir = ConcluirPrimeiroAcesso(repo_usuarios, obter_ou_criar)
    identidade = IdentidadeExterna("user_ok")

    with pytest.raises(DadosInvalidosError) as exc_nome:
        await concluir.executar(identidade, "   ", "Neo", "trabalho")
    assert exc_nome.value.campo == "nome_exibicao"

    with pytest.raises(DadosInvalidosError) as exc_tipo:
        await concluir.executar(identidade, "Thalyson", "Neo", "invalido")
    assert exc_tipo.value.campo == "espaco.tipo"

    salvo = await concluir.executar(identidade, "  Thalyson  ", "  Neo  ", "trabalho")
    assert salvo.primeiro_acesso_concluido is True
    assert salvo.nome_exibicao is not None and salvo.nome_exibicao.valor == "Thalyson"
    assert len(salvo.espacos) == 1
    assert salvo.espacos[0].tipo is TipoEspaco.TRABALHO

    with pytest.raises(PrimeiroAcessoJaConcluidoError):
        await concluir.executar(identidade, "Outro", "Outro", "pessoal")


async def test_AC_10_gerenciar_lista_permissao() -> None:
    """AC-10: adicionar idempotente em minusculas, listar e remover com erro se ausente."""
    repo_lista = RepoListaEmMemoria()
    gerenciar = GerenciarListaDePermissao(repo_lista)

    item1, criado1 = await gerenciar.permitir("  Ana@Example.COM ")
    assert criado1 is True
    assert item1.email == Email("ana@example.com")

    _, criado2 = await gerenciar.permitir("ana@example.com")
    assert criado2 is False

    lista = await gerenciar.listar()
    assert [i.email.valor for i in lista] == ["ana@example.com"]

    removido = await gerenciar.remover("ANA@example.com")
    assert removido == Email("ana@example.com")

    with pytest.raises(EmailAutorizadoNaoEncontradoError):
        await gerenciar.remover("ana@example.com")
