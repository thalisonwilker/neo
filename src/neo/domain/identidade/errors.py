"""Excecoes de dominio do bounded context Identidade."""

from __future__ import annotations


class ErroDeDominio(Exception):
    """Base para erros de regra de negocio no contexto Identidade."""

    def __init__(self, codigo: str, mensagem: str, *, campo: str | None = None) -> None:
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem
        self.campo = campo


class DadosInvalidosError(ErroDeDominio):
    """Dados informados violam restricoes de formato ou tamanho."""

    def __init__(self, mensagem: str, *, campo: str | None = None) -> None:
        super().__init__("dados_invalidos", mensagem, campo=campo)


class TokenInvalidoError(ErroDeDominio):
    """Token de sessao ausente, expirado, adulterado ou fora das regras de confianca."""

    def __init__(self, mensagem: str = "Token de autenticação inválido ou ausente.") -> None:
        super().__init__("token_invalido", mensagem)


class AcessoNaoLiberadoError(ErroDeDominio):
    """Identidade valida cujo e-mail nao consta na Lista de permissao."""

    def __init__(self, mensagem: str = "Este e-mail não está autorizado a acessar o Neo.") -> None:
        super().__init__("acesso_nao_liberado", mensagem)


class PrimeiroAcessoJaConcluidoError(ErroDeDominio):
    """Tentativa de repetir o Primeiro acesso de um Usuario que ja o concluiu."""

    def __init__(self, mensagem: str = "O primeiro acesso já foi concluído.") -> None:
        super().__init__("primeiro_acesso_ja_concluido", mensagem)


class PrimeiroAcessoPendenteError(ErroDeDominio):
    """Acao que exige o Primeiro acesso concluido (ex.: criar Espaco) pedida antes dele."""

    def __init__(
        self, mensagem: str = "Conclua o primeiro acesso antes de criar um espaço."
    ) -> None:
        super().__init__("primeiro_acesso_pendente", mensagem)


class ClerkIndisponivelError(ErroDeDominio):
    """Falha ao consultar o provedor externo de identidade."""

    def __init__(
        self, mensagem: str = "Não foi possível consultar o provedor de identidade agora."
    ) -> None:
        super().__init__("clerk_indisponivel", mensagem)


class EmailAutorizadoNaoEncontradoError(ErroDeDominio):
    """E-mail nao localizado na Lista de permissao."""

    def __init__(self, mensagem: str = "E-mail não encontrado na lista de permissão.") -> None:
        super().__init__("email_nao_encontrado", mensagem)
