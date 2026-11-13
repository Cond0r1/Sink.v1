"""Atajos de teclado del agente. Para cambiar o añadir uno, edita aquí."""

import os
import shutil
import subprocess
import sys

from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.key_binding import KeyBindings

import config


def abrir_nueva_sesion() -> None:
    """Abre otra sesión del agente en una pestaña/ventana nueva."""
    proyecto = os.path.dirname(os.path.abspath(__file__))
    py = sys.executable
    try:
        if os.name == "nt":
            wt = shutil.which("wt")
            if wt:
                subprocess.Popen([wt, "-w", "0", "new-tab", "-d", proyecto, py, "main.py"])
            else:
                subprocess.Popen(f'start "DeepSeek" "{py}" main.py', shell=True, cwd=proyecto)
        else:
            for term in ("gnome-terminal", "konsole", "xterm"):
                if shutil.which(term):
                    subprocess.Popen([term, "-e", py, "main.py"], cwd=proyecto)
                    break
    except Exception:
        pass


def crear_atajos(agente) -> KeyBindings:
    """Devuelve los atajos de teclado, ligados al agente."""
    kb = KeyBindings()

    @kb.add("s-tab")  # Shift+Tab -> cambia de modelo
    def _cambiar_modelo(event) -> None:
        modelos = config.AVAILABLE_MODELS
        if not modelos:
            return
        actual = agente.llm.model
        try:
            i = modelos.index(actual)
        except ValueError:
            i = -1
        agente.llm.model = modelos[(i + 1) % len(modelos)]
        event.app.invalidate()

    @kb.add("c-n")  # Ctrl+N -> nueva sesión (pestaña)
    def _nueva_sesion(event) -> None:
        abrir_nueva_sesion()

    @kb.add("c-w")  # Ctrl+W -> renombra la pestaña
    def _nombrar_pestana(event) -> None:
        def pedir_nombre() -> None:
            try:
                nombre = input("Nombre de la pestaña: ").strip()
            except (EOFError, KeyboardInterrupt):
                return
            if nombre:
                sys.stdout.write(f"\033]0;{nombre}\007")  # fija el título
                sys.stdout.flush()
                print()
        run_in_terminal(pedir_nombre)

    return kb
