"""Adaptadores de integracao com o Clerk (JWKS e Backend API)."""

from neo.infrastructure.clerk.email_reader import LeitorDeEmailClerk
from neo.infrastructure.clerk.token_verifier import VerificadorDeTokenClerk

__all__ = ["LeitorDeEmailClerk", "VerificadorDeTokenClerk"]
