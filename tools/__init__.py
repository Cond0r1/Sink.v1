"""Paquete de herramientas. Importarlo registra todas las herramientas."""

from .base import REGISTRY, dispatch, get_specs

# Importar cada módulo registra sus herramientas.
from . import files   # noqa: E402,F401
from . import shell   # noqa: E402,F401
from . import web     # noqa: E402,F401
from . import memory  # noqa: E402,F401

__all__ = ["REGISTRY", "dispatch", "get_specs"]
