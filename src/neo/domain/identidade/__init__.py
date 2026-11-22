"""Bounded context Identidade."""

from neo.domain.identidade.entities import EmailAutorizado, Espaco, Usuario
from neo.domain.identidade.errors import (
    AcessoNaoLiberadoError,
    ClerkIndisponivelError,
    DadosInvalidosError,
    EmailAutorizadoNaoEncontradoError,
    ErroDeDominio,
    PrimeiroAcessoJaConcluidoError,
    TokenInvalidoError,
)
from neo.domain.identidade.ports import (
    LeitorDeEmailExterno,
    RepositorioDeListaDePermissao,
    RepositorioDeUsuarios,
    TokenVerificado,
    VerificadorDeToken,
)
from neo.domain.identidade.value_objects import (
    Email,
    IdentidadeExterna,
    NomeDeExibicao,
    NomeDoEspaco,
    TipoEspaco,
)

__all__ = [
    "AcessoNaoLiberadoError",
    "ClerkIndisponivelError",
    "DadosInvalidosError",
    "Email",
    "EmailAutorizado",
    "EmailAutorizadoNaoEncontradoError",
    "ErroDeDominio",
    "Espaco",
    "IdentidadeExterna",
    "LeitorDeEmailExterno",
    "NomeDeExibicao",
    "NomeDoEspaco",
    "PrimeiroAcessoJaConcluidoError",
    "RepositorioDeListaDePermissao",
    "RepositorioDeUsuarios",
    "TipoEspaco",
    "TokenInvalidoError",
    "TokenVerificado",
    "Usuario",
    "VerificadorDeToken",
]
