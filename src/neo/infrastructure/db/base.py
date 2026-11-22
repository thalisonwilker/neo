"""Base declarativa dos modelos ORM do Neo."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base para todas as tabelas gerenciadas via SQLAlchemy."""
