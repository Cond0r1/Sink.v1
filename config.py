"""Carga y valida la configuración del agente desde el archivo .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargamos el .env de ESTA carpeta, sin importar desde dónde se ejecute.
load_dotenv(Path(__file__).with_name(".env"))


def _get_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _get_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, "").strip())
    except (TypeError, ValueError):
        return default


def _get_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, "").strip())
    except (TypeError, ValueError):
        return default


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, "").strip().lower()
    if not value:
        return default
    return value in ("true", "1", "yes", "y", "si", "sí", "on")


def _get_list(name: str, default: list[str] | None = None) -> list[str]:
    value = os.getenv(name, "").strip()
    if not value:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]


# API
DEEPSEEK_API_KEY: str = _get_str("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL: str = _get_str("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL: str = _get_str("MODEL", "deepseek-chat")
AVAILABLE_MODELS: list[str] = _get_list(
    "AVAILABLE_MODELS", ["deepseek-chat", "deepseek-reasoner"]
)
if MODEL and MODEL not in AVAILABLE_MODELS:
    AVAILABLE_MODELS.insert(0, MODEL)

# Límites del agente
MAX_ITERATIONS: int = _get_int("MAX_ITERATIONS", 15)
TEMPERATURE: float = _get_float("TEMPERATURE", 0.7)

# Seguridad
ALLOWED_DIRS: list[str] = _get_list("ALLOWED_DIRS", ["."])
CONFIRM_DANGEROUS: bool = _get_bool("CONFIRM_DANGEROUS", True)

# Memoria
MEMORY_FILE: str = _get_str("MEMORY_FILE", "memory.json")


def validate() -> None:
    if not DEEPSEEK_API_KEY:
        raise ValueError(
            "Falta DEEPSEEK_API_KEY en el archivo .env. "
            "Añade tu clave de la API de DeepSeek antes de ejecutar el agente."
        )
    if not DEEPSEEK_BASE_URL:
        raise ValueError("Falta DEEPSEEK_BASE_URL en el archivo .env.")
    if not MODEL:
        raise ValueError("Falta MODEL en el archivo .env.")
    if MAX_ITERATIONS <= 0:
        raise ValueError("MAX_ITERATIONS debe ser un entero positivo.")
    if not (0.0 <= TEMPERATURE <= 2.0):
        raise ValueError("TEMPERATURE debe estar entre 0.0 y 2.0.")


def summary() -> str:
    key_estado = "definida" if DEEPSEEK_API_KEY else "FALTA"
    return (
        "Configuración del agente:\n"
        f"  - API key:          {key_estado}\n"
        f"  - Base URL:         {DEEPSEEK_BASE_URL}\n"
        f"  - Modelo:           {MODEL}\n"
        f"  - Máx. iteraciones: {MAX_ITERATIONS}\n"
        f"  - Temperatura:      {TEMPERATURE}\n"
        f"  - Directorios OK:   {ALLOWED_DIRS}\n"
        f"  - Confirmar riesgo: {CONFIRM_DANGEROUS}\n"
        f"  - Archivo memoria:  {MEMORY_FILE}"
    )


if __name__ == "__main__":
    try:
        validate()
        print("Configuración válida.\n")
    except ValueError as error:
        print(f"Error de configuración: {error}\n")
    print(summary())
