"""Herramienta para ejecutar comandos del sistema (con seguridad y timeout)."""

import glob
import os
import shutil
import subprocess

import config

from .base import confirm, tool


def _buscar_ejecutable(nombre: str) -> str | None:
    """Busca un ejecutable en el PATH y en los paquetes de winget."""
    ruta = shutil.which(nombre)
    if ruta:
        return ruta
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        enlace = os.path.join(local, "Microsoft", "WinGet", "Links", f"{nombre}.exe")
        if os.path.isfile(enlace):
            return enlace
        patron = os.path.join(
            local, "Microsoft", "WinGet", "Packages", f"*{nombre}*", "**", f"{nombre}.exe"
        )
        hits = glob.glob(patron, recursive=True)
        if hits:
            return hits[0]
    return None


def _buscar_bash() -> str | None:
    """Encuentra Git Bash, incluso si no está en el PATH."""
    ruta = _buscar_ejecutable("bash")
    if ruta:
        return ruta
    candidatos = [
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
    ]
    local = os.environ.get("LOCALAPPDATA", "")
    if local:
        candidatos.append(os.path.join(local, "Programs", "Git", "usr", "bin", "bash.exe"))
    for c in candidatos:
        if os.path.isfile(c):
            return c
    return None


_BASH = _buscar_bash() if os.name == "nt" else None


def _entorno_bash() -> dict | None:
    """Añade al PATH las carpetas de comandos Unix de Git (dir, grep, sed...)."""
    if not _BASH:
        return None
    env = os.environ.copy()
    usr_bin = os.path.dirname(_BASH)
    git_root = os.path.dirname(os.path.dirname(usr_bin))
    extra = [
        usr_bin,
        os.path.join(git_root, "bin"),
        os.path.join(git_root, "usr", "local", "bin"),
        os.path.join(git_root, "mingw64", "bin"),
    ]
    env["PATH"] = os.pathsep.join(extra) + os.pathsep + env.get("PATH", "")
    return env


_BASH_ENV = _entorno_bash()

# lsd: un 'ls' moderno (icono + tamaño + nombre).
_LSD = _buscar_ejecutable("lsd")


def _ls_argv(command: str) -> list[str] | None:
    """Un 'ls' simple -> lsd (tamaño+nombre); con flags -> None (ls normal)."""
    if not _LSD:
        return None
    tokens = command.strip().split()
    if not tokens or tokens[0] != "ls":
        return None
    args = tokens[1:]
    if any(a.startswith("-") for a in args):
        return None
    return [
        _LSD, "-l", "--blocks", "size,name",
        "--icon", "never", "--color", "never", *args,
    ]


# Comandos peligrosos: solo estos piden confirmación.
COMANDOS_PELIGROSOS = {
    "rm", "rmdir", "mv", "cp", "dd",
    "del", "erase", "rd", "move", "format",
    "chmod", "chown", "mkfs",
    "kill", "shutdown", "reboot", "halt",
}


def _es_peligroso(command: str) -> bool:
    limpio = command.replace("|", " ").replace(";", " ").replace("&", " ")
    return any(token.lower() in COMANDOS_PELIGROSOS for token in limpio.split())


@tool(
    name="run_command",
    description=(
        "Ejecuta un comando de shell y devuelve su salida (stdout, stderr y "
        "código de salida). Úsalo para tareas del sistema, scripts, git, etc."
    ),
    parameters={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Comando completo a ejecutar."},
            "timeout": {
                "type": "integer",
                "description": "Segundos máximos de ejecución (por defecto 60).",
            },
        },
        "required": ["command"],
    },
)
def run_command(command: str, timeout: int = 60) -> str:
    if _es_peligroso(command) and not confirm(f"Ejecutar comando PELIGROSO: {command}"):
        return "Cancelado por el usuario."

    cwd = config.ALLOWED_DIRS[0] if config.ALLOWED_DIRS else "."
    argv_ls = _ls_argv(command)

    try:
        if argv_ls:  # 'ls' bonito con lsd
            proceso = subprocess.run(
                argv_ls, cwd=cwd, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout,
            )
        elif _BASH:  # Git Bash: salida Unix
            proceso = subprocess.run(
                [_BASH, "-c", command], cwd=cwd, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=timeout, env=_BASH_ENV,
            )
        elif os.name == "nt":  # Windows sin Git Bash: PowerShell
            proceso = subprocess.run(
                ["powershell", "-NoProfile", "-Command", command], cwd=cwd,
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=timeout,
            )
        else:  # Linux/Mac
            proceso = subprocess.run(
                command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout,
            )
    except subprocess.TimeoutExpired:
        return f"[error] El comando superó el tiempo límite de {timeout}s."
    except Exception as error:  # noqa: BLE001
        return f"[error] No se pudo ejecutar el comando: {error}"

    partes = [f"Código de salida: {proceso.returncode}"]
    if proceso.stdout.strip():
        partes.append(f"--- stdout ---\n{proceso.stdout.strip()}")
    if proceso.stderr.strip():
        partes.append(f"--- stderr ---\n{proceso.stderr.strip()}")
    return "\n".join(partes)
