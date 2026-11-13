"""Núcleo del agente: el bucle de razonamiento."""

import json
import sys

import config
import tools
from llm import LLMClient
from memory import ConversationMemory

# En Windows la consola (cp1252) revienta con emojis; forzamos UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

SYSTEM_PROMPT = """Eres un agente asistente que ayuda al usuario usando herramientas.

- Piensa paso a paso qué necesitas hacer.
- Cuando necesites información o realizar una acción (leer/escribir archivos,
  ejecutar comandos, buscar en la web, recordar datos), USA las herramientas
  disponibles en lugar de inventar la respuesta.
- Cuando ya tengas lo necesario, responde al usuario de forma clara y concisa.
- Trabaja siempre dentro de los directorios permitidos y respeta la seguridad.
- Cuando el usuario SOLO salude (hola, buenas, hey, qué tal...), responde
  únicamente con: «¡Hola! 👋 ¿En qué puedo ayudarte hoy?» y nada más.
  No enumeres tus capacidades ni lo que puedes hacer.
- Cuando el usuario te pida ejecutar un comando concreto, ejecútalo EXACTAMENTE
  como lo escribió, sin añadir, quitar ni cambiar flags u opciones. Si dice
  «ls», ejecuta «ls», nunca «ls -la». Solo añade flags si el usuario los pide.
- Al ejecutar un comando, muestra su salida TAL CUAL, dentro de un bloque de
  código, sin resumirla, reordenarla, reformatearla ni interpretarla. No
  conviertas la salida en listas ni la describas con tus palabras: el usuario
  quiere ver la salida literal del comando, igual que en una terminal.
- ÚNICA excepción: cuando la salida sea un listado de archivos/carpetas (por
  ejemplo de 'ls' o 'dir'), antepón a cada elemento un emoji según su tipo.
  El formato de cada línea debe ser EXACTAMENTE:  <emoji> <resto de la línea>
  es decir, conservas intactos el tamaño y el nombre que devolvió el comando,
  y SOLO añades el emoji al principio. Un elemento por línea. Ejemplo:
    entrada del comando:   4.0 KB __pycache__
    tu salida:             📁 4.0 KB __pycache__
    entrada del comando:   602 B  requirements.txt
    tu salida:             📦 602 B  requirements.txt
  Emojis por tipo: 📁 carpetas/directorios · 🐍 .py · 📄 .txt/.md ·
  ⚙️ .json/.env/config · 📦 requirements.txt · 🖼️ imágenes · 📜 .sh/.bat ·
  🔒 claves/.pem. Para extensiones no listadas, elige un emoji representativo.
  Nunca cambies ni inventes nombres ni tamaños.
"""


class Agent:
    def __init__(self, persist: bool = False) -> None:
        self.llm = LLMClient()
        self.tools = tools.get_specs()
        self.memory = ConversationMemory(SYSTEM_PROMPT)
        self.persist = persist
        if persist:
            self.memory.load()
        self.last_tokens = {"prompt": 0, "completion": 0, "total": 0}
        self.session_tokens = {"prompt": 0, "completion": 0, "total": 0}

    def _assistant_to_dict(self, message) -> dict:
        """Mensaje del modelo -> dict para el historial (con tool_calls)."""
        entry: dict = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            entry["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]
        return entry

    def run_turn(self, user_input: str, on_tokens=None) -> str:
        """Procesa un mensaje y devuelve la respuesta final en texto."""
        # Punto de retorno por si se cancela (Ctrl+C) este turno a medias.
        snapshot = len(self.memory.messages)
        self.memory.add_user(user_input)
        self.last_tokens = {"prompt": 0, "completion": 0, "total": 0}

        tokens_vivos = 0

        def tick() -> None:
            nonlocal tokens_vivos
            tokens_vivos += 1
            if on_tokens:
                on_tokens(tokens_vivos)

        try:
            for _ in range(config.MAX_ITERATIONS):
                message = self.llm.complete_stream(
                    self.memory.get(), tools=self.tools, on_token=tick
                )
                uso = self.llm.last_usage
                if uso is not None:
                    p = getattr(uso, "prompt_tokens", 0) or 0
                    c = getattr(uso, "completion_tokens", 0) or 0
                    t = getattr(uso, "total_tokens", 0) or 0
                    self.last_tokens["prompt"] += p
                    self.last_tokens["completion"] += c
                    self.last_tokens["total"] += t
                    self.session_tokens["prompt"] += p
                    self.session_tokens["completion"] += c
                    self.session_tokens["total"] += t
                self.memory.add_assistant(self._assistant_to_dict(message))

                # Sin tool_calls -> respuesta final.
                if not message.tool_calls:
                    if self.persist:
                        self.memory.save()
                    return message.content or "(respuesta vacía)"

                # Con tool_calls -> ejecutar cada herramienta y volver a preguntar.
                for call in message.tool_calls:
                    nombre = call.function.name
                    try:
                        argumentos = json.loads(call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        resultado = "[error] Argumentos JSON inválidos."
                    else:
                        resultado = tools.dispatch(nombre, argumentos)
                    self.memory.add_tool_result(call.id, resultado)
        except KeyboardInterrupt:
            # Cancelado: descartamos este turno a medias y volvemos al estado
            # previo (memoria limpia, sin pares de herramientas rotos).
            del self.memory.messages[snapshot:]
            raise

        if self.persist:
            self.memory.save()
        return (
            f"[Se alcanzó el límite de {config.MAX_ITERATIONS} iteraciones "
            f"sin una respuesta final.]"
        )
