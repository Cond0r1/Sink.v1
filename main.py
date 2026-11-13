"""Punto de entrada: interfaz de terminal + arranque.  Ejecutar: python main.py"""

import json
import math
import os
import re
import time
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text

import config
import idiomas
from agent import Agent
from atajos import crear_atajos
from idiomas import t

console = Console()

# Ajustes persistentes (persistencia del historial e intervalo de /clih).
_SETTINGS = Path("settings.json")


def cargar_settings() -> dict:
    try:
        if _SETTINGS.exists():
            return json.loads(_SETTINGS.read_text())
    except Exception:  # noqa: BLE001
        pass
    return {}


def guardar_settings(data: dict) -> None:
    try:
        _SETTINGS.write_text(json.dumps(data))
    except Exception:  # noqa: BLE001
        pass


# Comandos reconocidos: se resaltan en azul mientras escribes.
COMANDOS_CONOCIDOS = {
    "ls", "pwd", "cd", "cat", "echo", "mkdir", "rmdir", "touch", "rm", "mv",
    "cp", "grep", "find", "head", "tail", "clear", "chmod", "chown", "whoami",
    "date", "df", "du", "ps", "kill", "wget", "curl", "man", "less", "more",
    "sudo", "tar", "zip", "unzip", "ssh", "scp", "ping", "history", "which",
    "tree", "nano", "vim", "code", "node", "npm", "git", "python", "python3",
    "pip", "pip3", "apt", "make", "docker", "awk", "sed", "sort", "uniq", "wc",
    "dir", "cls", "type", "copy", "move", "del", "ren", "cmd", "powershell",
}


class InputLexer(Lexer):
    """Resalta 'exit' solo (rojo) y los comandos conocidos (azul) al escribir."""

    def lex_document(self, document):
        es_exit = document.text == "exit"

        def obtener_linea(numero_linea):
            linea = document.lines[numero_linea]
            if es_exit:
                return [("fg:#990000 bold", linea)]
            fragmentos = []
            for parte in re.split(r"(\s+)", linea):
                if parte and not parte.isspace() and parte.lower() in COMANDOS_CONOCIDOS:
                    fragmentos.append(("fg:#2f7fd1 bold", parte))  # azul
                else:
                    fragmentos.append(("", parte))
            return fragmentos

        return obtener_linea


def crear_sesion(agente: Agent) -> PromptSession:
    atajos = crear_atajos(agente)

    def barra_inferior() -> HTML:
        return HTML(f"<b>{agente.llm.model}</b>")

    # Barra inferior sin fondo: solo texto gris + negrita.
    estilo = Style.from_dict({"bottom-toolbar": "noreverse bg:default fg:ansibrightblack"})

    return PromptSession(
        key_bindings=atajos,
        bottom_toolbar=barra_inferior,
        style=estilo,
        lexer=InputLexer(),
    )


SALIR = {"salir", "exit", "quit"}

# Logo ASCII (columna izquierda del banner).
_LOGO = [
    "      ▄▄████▄▄       ",
    "▄   ▄████████▀██▄    ",
    "▀█▄▄██████████████   ",
    "▄▀   ▀▀█████████▀    ",
]
VERSION = "Sink v1.0"
AUTOR = "by: Condor"

# "Diving": palabra animada mientras responde (ola blanca recorriendo letras).
PALABRA_PENSANDO = "Diving"

# Olita de bloques que fluye, junto a "Diving".
_RAMPA_OLA = "▁▂▃"


def _patron_ola(longitud: int = 16, periodo: int = 8) -> str:
    puntos = []
    for x in range(longitud):
        v = (math.sin(2 * math.pi * x / periodo) + 1) / 2
        puntos.append(_RAMPA_OLA[round(v * (len(_RAMPA_OLA) - 1))])
    return "".join(puntos)


_OLA = _patron_ola()


def texto_pensando(frame: int) -> Text:
    t = Text()
    ciclo = len(PALABRA_PENSANDO) + 3
    cresta = frame % ciclo
    for i, ch in enumerate(PALABRA_PENSANDO):
        distancia = abs(i - cresta)
        if distancia == 0:
            estilo = "bold white"        # cresta
        elif distancia == 1:
            estilo = "bold #87cefa"      # celeste
        else:
            estilo = "bold #1e90ff"      # azul
        t.append(ch, style=estilo)
    t.append("...", style="bold #1e90ff")
    return t


def construir_banner(agente: Agent) -> Text:
    """Logo a la izquierda; a la derecha: versión+autor, modelo y carpeta."""
    banner = Text()
    banner.append(_LOGO[0], style="bold blue")
    banner.append("\n")
    banner.append(_LOGO[1], style="bold blue")
    banner.append(VERSION, style="bold")
    banner.append(f"  {AUTOR}", style="grey50")
    banner.append("\n")
    banner.append(_LOGO[2], style="bold blue")
    banner.append(agente.llm.model, style="bold")
    banner.append("\n")
    banner.append(_LOGO[3], style="bold blue")
    banner.append(os.getcwd(), style="bold")
    banner.append("\n")
    return banner


def mostrar_ayuda() -> None:
    console.print(t("ayuda"), style="grey70")


def elegir_idioma_interactivo(settings: dict) -> None:
    """Abre el menú de idioma (/l), aplica la elección y la guarda."""
    codigo = idiomas.elegir_idioma(idiomas.get_idioma())
    if not codigo:
        console.print(t("cancelado") + "\n", style="grey50")
        return
    if codigo == idiomas.get_idioma():
        return  # mismo idioma: nada que cambiar
    idiomas.set_idioma(codigo)
    settings["idioma"] = codigo
    guardar_settings(settings)
    console.print(
        t("idioma_cambiado", nombre=idiomas.nombre_idioma(codigo)) + "\n",
        style="grey50",
    )


def main() -> None:
    # Trabajamos siempre en la carpeta del proyecto (aunque nos llamen desde otra).
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.system("cls" if os.name == "nt" else "clear")

    try:
        config.validate()
    except ValueError as error:
        print(f"[config] {error}")
        print("Revisa tu archivo .env y vuelve a intentarlo.")
        return

    settings = cargar_settings()
    idiomas.set_idioma(settings.get("idioma", idiomas.IDIOMA_POR_DEFECTO))
    try:
        agente = Agent(persist=settings.get("persist", False))
    except Exception as error:  # noqa: BLE001
        print(f"[error] No se pudo iniciar el agente: {error}")
        return

    console.print(construir_banner(agente))
    console.print(t("banner_hint") + "\n", style="grey50")

    sesion = crear_sesion(agente)

    # Limpieza periódica del historial: 0 = desactivada.
    limpieza_cada = settings.get("limpieza_cada", 0)
    turnos = 0

    while True:
        try:
            entrada_cruda = sesion.prompt("❯ ")
        except (EOFError, KeyboardInterrupt):
            # Ctrl+C / Ctrl+D mientras escribes: salir limpio a la consola.
            os.system("cls" if os.name == "nt" else "clear")
            console.print(Text(t("cerrando"), style="bold yellow"))
            break

        entrada = entrada_cruda.strip()
        if not entrada:
            continue

        # Salir: limpia la pantalla y termina sin dejar rastro.
        if entrada.lower() in SALIR:
            os.system("cls" if os.name == "nt" else "clear")
            break

        # Reimprime el mensaje con fondo gris (calcula cuántas filas ocupó).
        ancho = max(1, console.size.width)
        filas = max(1, -(-(2 + len(entrada_cruda)) // ancho))
        print(f"\033[{filas}A\r\033[J", end="")
        console.print(Text(f"❯ {entrada}", style="black on grey70"))

        # Comandos de la interfaz.
        if entrada.lower() in ("/key", "/help"):
            mostrar_ayuda()
            continue
        if entrada.lower() == "/l":
            elegir_idioma_interactivo(settings)
            continue
        if entrada.lower() == "/reset":
            agente.memory.reset()
            agente.memory.save()
            turnos = 0
            console.print(t("reset_ok") + "\n")
            continue
        if entrada.lower() == "/clih":
            try:
                n = input(t("clih_pregunta")).strip()
                limpieza_cada = max(0, int(n))
            except (ValueError, EOFError, KeyboardInterrupt):
                console.print(t("cancelado") + "\n")
                continue
            turnos = 0
            settings["limpieza_cada"] = limpieza_cada
            guardar_settings(settings)
            if limpieza_cada:
                console.print(t("clih_cada", n=limpieza_cada) + "\n", style="grey50")
            else:
                console.print(t("clih_off") + "\n", style="grey50")
            continue
        if entrada.lower() == "/persistencia":
            agente.persist = True
            agente.memory.save()
            settings["persist"] = True
            guardar_settings(settings)
            console.print(t("persist_on") + "\n", style="grey50")
            continue
        if entrada.lower() == "/persistencia-disable":
            agente.persist = False
            settings["persist"] = False
            guardar_settings(settings)
            try:
                r = input(t("persist_pregunta_borrar")).strip().lower()
            except (EOFError, KeyboardInterrupt):
                r = "n"
            if r in ("s", "si", "sí", "y", "yes"):
                agente.memory.history_file.unlink(missing_ok=True)
                agente.memory.reset()
                console.print(t("persist_off_borrada") + "\n", style="grey50")
            else:
                console.print(t("persist_off_conservada") + "\n", style="grey50")
            continue
        if entrada.lower() in ("/clear", "clear", "cls"):
            os.system("cls" if os.name == "nt" else "clear")
            continue
        if entrada.lower() == "/tokens":
            console.print(t("tokens", n=agente.session_tokens["total"]) + "\n")
            continue
        if entrada.lower() == "/tokens_p":
            try:
                saldo = agente.llm.get_balance()
            except Exception as error:  # noqa: BLE001
                console.print(f"[red]{error}[/red]\n")
                continue
            if saldo:
                console.print(
                    t("saldo", total=f"{saldo['total']:.2f}", currency=saldo["currency"])
                    + "\n"
                )
            else:
                console.print(t("saldo_none") + "\n")
            continue

        # Turno normal. Contador en vivo: solo si tarda >2 s.
        inicio = time.monotonic()
        estado = {"live": None, "mostrado": False}

        def al_recibir_tokens(n: int) -> None:
            if time.monotonic() - inicio < 2:
                return
            if estado["live"] is None:
                estado["live"] = Live(console=console, transient=True, refresh_per_second=12)
                estado["live"].start()
                estado["mostrado"] = True
            segundos = int(time.monotonic() - inicio)
            desplazamiento = n % len(_OLA)
            olas = (_OLA + _OLA)[desplazamiento:desplazamiento + 3]
            linea = texto_pensando(n)
            linea.append(f"  {olas}  ", style="cyan")
            linea.append(f"{segundos}s * Tokens: {n}", style="grey50")
            estado["live"].update(linea)

        try:
            respuesta = agente.run_turn(entrada, on_tokens=al_recibir_tokens)
        except KeyboardInterrupt:
            # Ctrl+C mientras responde: corta la respuesta y vuelve al prompt.
            if estado["live"] is not None:
                estado["live"].stop()
                estado["live"] = None
            console.print(f"[grey50]{t('cancelado_resp')}[/grey50]\n")
            continue
        except Exception as error:  # noqa: BLE001
            if estado["live"] is not None:
                estado["live"].stop()
                estado["live"] = None
            console.print(f"\n[bold red]{t('error_label')}[/bold red] {error}\n")
            continue
        finally:
            if estado["live"] is not None:
                estado["live"].stop()

        console.print()
        console.print(Markdown(respuesta))
        # Al terminar solo queda el tiempo que tardó.
        if estado["mostrado"]:
            total = int(time.monotonic() - inicio)
            console.print(f"[grey50]{total}s[/grey50]")
        console.print()

        # Revisión periódica: al llegar al límite, pregunta antes de limpiar.
        turnos += 1
        if limpieza_cada and turnos >= limpieza_cada:
            try:
                r = input(t("hist_pregunta", n=turnos)).strip().lower()
            except (EOFError, KeyboardInterrupt):
                r = "e"
            if r in ("l", "limpiar"):
                borrados = agente.memory.trim()
                agente.memory.save()
                console.print(t("hist_limpiado", n=borrados) + "\n", style="grey50")
            else:
                console.print(t("hist_extendido") + "\n", style="grey50")
            turnos = 0


if __name__ == "__main__":
    main()
