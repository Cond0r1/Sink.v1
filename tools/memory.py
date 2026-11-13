"""Memoria persistente clave->valor (remember / recall / forget)."""

import json
from pathlib import Path

import config

from .base import ToolError, tool

_MEMORY_PATH = Path(config.MEMORY_FILE)


def _load() -> dict:
    if not _MEMORY_PATH.exists():
        return {}
    try:
        return json.loads(_MEMORY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    _MEMORY_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


@tool(
    name="remember",
    description=(
        "Guarda un dato en la memoria persistente del agente para recordarlo "
        "en el futuro. Si la clave ya existe, la actualiza."
    ),
    parameters={
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Identificador del dato."},
            "value": {"type": "string", "description": "Contenido a recordar."},
        },
        "required": ["key", "value"],
    },
)
def remember(key: str, value: str) -> str:
    data = _load()
    data[key] = value
    _save(data)
    return f"Recordado: '{key}'."


@tool(
    name="recall",
    description=(
        "Recupera un dato de la memoria por su clave. Si no se indica clave, "
        "devuelve todas las claves guardadas."
    ),
    parameters={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Clave a recuperar. Omítela para ver todo.",
            },
        },
        "required": [],
    },
)
def recall(key: str = "") -> str:
    data = _load()
    if not data:
        return "(memoria vacía)"
    if not key:
        lineas = [f"- {k}: {v}" for k, v in data.items()]
        return "\n".join(lineas)
    if key not in data:
        raise ToolError(f"No hay nada guardado con la clave '{key}'.")
    return data[key]


@tool(
    name="forget",
    description="Borra un dato de la memoria persistente por su clave.",
    parameters={
        "type": "object",
        "properties": {
            "key": {"type": "string", "description": "Clave a borrar."},
        },
        "required": ["key"],
    },
)
def forget(key: str) -> str:
    data = _load()
    if key not in data:
        raise ToolError(f"No existe la clave '{key}'.")
    del data[key]
    _save(data)
    return f"Olvidado: '{key}'."
