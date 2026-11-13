"""Cimiento de las herramientas: registro (@tool), fichas y seguridad."""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import config


class ToolError(Exception):
    pass


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    func: Callable


# Registro global: nombre -> Tool
REGISTRY: dict[str, Tool] = {}


def tool(name: str, description: str, parameters: dict) -> Callable:
    """Decorador que registra una herramienta con su ficha."""
    def decorator(func: Callable) -> Callable:
        if name in REGISTRY:
            raise ValueError(f"Ya existe una herramienta llamada '{name}'.")
        REGISTRY[name] = Tool(name, description, parameters, func)
        return func
    return decorator


def get_specs() -> list[dict]:
    """Fichas de todas las herramientas, en el formato que espera la API."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            },
        }
        for t in REGISTRY.values()
    ]


def dispatch(name: str, arguments: dict) -> str:
    """Ejecuta la herramienta por nombre y devuelve siempre un string."""
    tool_obj = REGISTRY.get(name)
    if tool_obj is None:
        return f"[error] No existe la herramienta '{name}'."
    try:
        return str(tool_obj.func(**arguments))
    except ToolError as error:
        return f"[error] {error}"
    except TypeError as error:
        return f"[error] Argumentos inválidos para '{name}': {error}"
    except Exception as error:  # noqa: BLE001
        return f"[error] Fallo inesperado en '{name}': {error}"


# Seguridad (usan config.ALLOWED_DIRS y config.CONFIRM_DANGEROUS)

def is_path_allowed(path: str) -> bool:
    target = Path(path).resolve()
    for allowed in config.ALLOWED_DIRS:
        try:
            target.relative_to(Path(allowed).resolve())
            return True
        except ValueError:
            continue
    return False


def ensure_allowed(path: str) -> Path:
    if not is_path_allowed(path):
        raise ToolError(
            f"Acceso denegado: '{path}' está fuera de los directorios "
            f"permitidos ({config.ALLOWED_DIRS})."
        )
    return Path(path).resolve()


def confirm(action: str) -> bool:
    if not config.CONFIRM_DANGEROUS:
        return True
    try:
        answer = input(f"[confirmar] {action}  ¿Continuar? (s/n): ").strip().lower()
    except EOFError:
        return False
    return answer in ("s", "si", "sí", "y", "yes")
