"""Herramientas de archivos: leer, escribir, listar, mover y borrar."""

import shutil

from .base import ToolError, confirm, ensure_allowed, tool


@tool(
    name="read_file",
    description="Lee y devuelve el contenido de texto de un archivo.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Ruta del archivo a leer."},
        },
        "required": ["path"],
    },
)
def read_file(path: str) -> str:
    file = ensure_allowed(path)
    if not file.is_file():
        raise ToolError(f"No existe el archivo: {path}")
    try:
        return file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise ToolError(f"El archivo no es texto UTF-8 legible: {path}")


@tool(
    name="write_file",
    description=(
        "Escribe (o sobrescribe) texto en un archivo. Crea las carpetas "
        "intermedias si no existen."
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Ruta del archivo a escribir."},
            "content": {"type": "string", "description": "Contenido de texto a guardar."},
        },
        "required": ["path", "content"],
    },
)
def write_file(path: str, content: str) -> str:
    file = ensure_allowed(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")
    return f"Escrito {len(content)} caracteres en {file}."


@tool(
    name="list_dir",
    description="Lista los archivos y carpetas dentro de un directorio.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Ruta del directorio. Por defecto el directorio actual.",
            },
        },
        "required": [],
    },
)
def list_dir(path: str = ".") -> str:
    folder = ensure_allowed(path)
    if not folder.is_dir():
        raise ToolError(f"No es un directorio: {path}")
    entradas = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    if not entradas:
        return "(directorio vacío)"
    lineas = []
    for p in entradas:
        marca = "/" if p.is_dir() else ""
        lineas.append(f"{p.name}{marca}")
    return "\n".join(lineas)


@tool(
    name="move_file",
    description="Renombra o mueve un archivo o carpeta de una ruta a otra.",
    parameters={
        "type": "object",
        "properties": {
            "src": {"type": "string", "description": "Ruta de origen."},
            "dst": {"type": "string", "description": "Ruta de destino."},
        },
        "required": ["src", "dst"],
    },
)
def move_file(src: str, dst: str) -> str:
    origen = ensure_allowed(src)
    destino = ensure_allowed(dst)
    if not origen.exists():
        raise ToolError(f"No existe el origen: {src}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(origen), str(destino))
    return f"Movido: {origen} -> {destino}"


@tool(
    name="delete_file",
    description=(
        "Borra un archivo o carpeta. Acción peligrosa: pide confirmación "
        "si CONFIRM_DANGEROUS está activado."
    ),
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Ruta a borrar."},
        },
        "required": ["path"],
    },
)
def delete_file(path: str) -> str:
    objetivo = ensure_allowed(path)
    if not objetivo.exists():
        raise ToolError(f"No existe: {path}")
    if not confirm(f"Borrar '{objetivo}'"):
        return "Cancelado por el usuario."
    if objetivo.is_dir():
        shutil.rmtree(objetivo)
    else:
        objetivo.unlink()
    return f"Borrado: {objetivo}"
