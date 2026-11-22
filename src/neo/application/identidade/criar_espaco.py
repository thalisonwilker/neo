"""Caso de uso: criar um novo Espaco do Usuario (0040)."""

from __future__ import annotations

import logging

from neo.application.identidade.obter_ou_criar_usuario import ObterOuCriarUsuario
from neo.domain.identidade import (
    DadosInvalidosError,
    Espaco,
    IdentidadeExterna,
    MetaSemanal,
    NomeDoEspaco,
    PrimeiroAcessoPendenteError,
    RepositorioDeUsuarios,
    TipoEspaco,
)

logger = logging.getLogger("neo.application.identidade")

# Os value objects nomeiam o campo como no Primeiro acesso (`espaco.nome`); na criacao avulsa o
# corpo do pedido e plano (`nome`, `tipo`), entao o caso de uso traduz o campo do erro (0040 AC-3).
_CAMPOS_DA_CRIACAO = {"espaco.nome": "nome", "espaco.tipo": "tipo"}


class CriarEspaco:
    """Cria um Espaco para um Usuario que ja concluiu o Primeiro acesso."""

    def __init__(
        self,
        usuarios: RepositorioDeUsuarios,
        obter_ou_criar: ObterOuCriarUsuario,
    ) -> None:
        self._usuarios = usuarios
        self._obter_ou_criar = obter_ou_criar

    async def executar(
        self,
        identidade: IdentidadeExterna,
        nome_bruto: str,
        tipo_bruto: str,
        meta_semanal_bruta: int | None = None,
        agentes_sugeridos: bool = False,
    ) -> Espaco:
        """Valida a entrada, cria o Espaco no agregado Usuario e o persiste."""
        usuario = await self._obter_ou_criar.executar(identidade)
        if not usuario.primeiro_acesso_concluido:
            raise PrimeiroAcessoPendenteError()

        try:
            nome = NomeDoEspaco(nome_bruto)
            tipo = TipoEspaco.parse(tipo_bruto)
        except DadosInvalidosError as exc:
            campo = _CAMPOS_DA_CRIACAO.get(exc.campo or "", exc.campo)
            raise DadosInvalidosError(exc.mensagem, campo=campo) from exc
        meta = MetaSemanal(meta_semanal_bruta) if meta_semanal_bruta is not None else None

        espaco = usuario.criar_espaco(
            nome=nome,
            tipo=tipo,
            meta_semanal=meta,
            agentes_sugeridos=agentes_sugeridos,
        )
        await self._usuarios.adicionar_espaco(espaco)
        # Sem o nome do Espaco nem o e-mail no log (design 0040, observabilidade).
        logger.info(
            "evento=EspacoCriado usuario_id=%s espaco_id=%s tipo=%s",
            usuario.id,
            espaco.id,
            espaco.tipo.value,
        )
        return espaco
