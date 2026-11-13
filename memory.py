"""Historial de la conversación (lista de mensajes), con persistencia en JSON."""

import json
from pathlib import Path

DEFAULT_HISTORY_FILE = "history.json"


class ConversationMemory:
    def __init__(self, system_prompt: str, history_file: str = DEFAULT_HISTORY_FILE) -> None:
        self.system_prompt = system_prompt
        self.history_file = Path(history_file)
        self.messages: list[dict] = [{"role": "system", "content": system_prompt}]

    def add(self, message: dict) -> None:
        self.messages.append(message)

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, message: dict) -> None:
        self.messages.append(message)

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        self.messages.append(
            {"role": "tool", "tool_call_id": tool_call_id, "content": content}
        )

    def get(self) -> list[dict]:
        return self.messages

    def __len__(self) -> int:
        return len(self.messages)

    def reset(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def trim(self, keep_last: int = 6) -> int:
        """
        Recorta el historial: conserva el system prompt + los últimos mensajes.
        Corta en un mensaje 'user' para no dejar resultados de herramientas
        huérfanos. Devuelve cuántos mensajes se eliminaron.
        """
        antes = len(self.messages)
        system = self.messages[:1] if self.messages and self.messages[0].get("role") == "system" else []
        resto = self.messages[len(system):]
        cola = resto[-keep_last:]
        # Avanzamos hasta el primer 'user' para no dejar tool/assistant sueltos.
        while cola and cola[0].get("role") != "user":
            cola = cola[1:]
        self.messages = system + cola
        return antes - len(self.messages)

    def save(self) -> None:
        self.history_file.write_text(
            json.dumps(self.messages, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load(self) -> bool:
        """Carga un historial guardado; True si se cargó, False si no."""
        if not self.history_file.exists():
            return False
        try:
            datos = json.loads(self.history_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        if not isinstance(datos, list) or not datos:
            return False

        self.messages = datos
        # Refrescamos el system prompt actual al principio del historial.
        if self.messages[0].get("role") == "system":
            self.messages[0] = {"role": "system", "content": self.system_prompt}
        else:
            self.messages.insert(0, {"role": "system", "content": self.system_prompt})
        return True
