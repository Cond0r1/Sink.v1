"""Capa de conexión con la API de DeepSeek (compatible con OpenAI)."""

import time
from types import SimpleNamespace

import requests
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)

import config


class LLMError(Exception):
    pass


class LLMClient:
    # Errores temporales que vale la pena reintentar.
    _RETRYABLE = (APIConnectionError, APITimeoutError, RateLimitError)

    def __init__(self, max_retries: int = 3, retry_base_delay: float = 1.0) -> None:
        config.validate()
        self.model = config.MODEL
        self.temperature = config.TEMPERATURE
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay
        self.client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )
        self.last_usage = None

    def get_balance(self) -> dict | None:
        """Saldo de la cuenta: {"currency": "USD", "total": 1.94} o None."""
        try:
            resp = requests.get(
                f"{config.DEEPSEEK_BASE_URL.rstrip('/')}/user/balance",
                headers={"Authorization": f"Bearer {config.DEEPSEEK_API_KEY}"},
                timeout=15,
            )
            resp.raise_for_status()
            datos = resp.json()
        except Exception as error:  # noqa: BLE001
            raise LLMError(f"No se pudo consultar el saldo: {error}") from error

        infos = datos.get("balance_infos") or []
        if not infos:
            return None
        info = infos[0]
        return {
            "currency": info.get("currency", ""),
            "total": float(info.get("total_balance", 0) or 0),
        }

    def _create(self, messages, temperature=None, **kwargs):
        """Llama a la API con reintentos (backoff exponencial)."""
        temp = self.temperature if temperature is None else temperature
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                respuesta = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    **kwargs,
                )
                self.last_usage = getattr(respuesta, "usage", None)
                return respuesta
            except self._RETRYABLE as error:
                last_error = error
                if attempt < self.max_retries:
                    delay = self.retry_base_delay * (2 ** attempt)
                    print(
                        f"[llm] Error temporal ({type(error).__name__}). "
                        f"Reintento {attempt + 1}/{self.max_retries} en {delay:.1f}s..."
                    )
                    time.sleep(delay)
                    continue
                break
            except APIStatusError as error:
                raise LLMError(
                    f"La API de DeepSeek devolvió un error "
                    f"{error.status_code}: {error.message}"
                ) from error
            except Exception as error:  # noqa: BLE001
                raise LLMError(f"Error inesperado al llamar al modelo: {error}") from error

        raise LLMError(
            f"No se pudo contactar con DeepSeek tras "
            f"{self.max_retries} reintentos. Último error: {last_error}"
        ) from last_error

    def chat(self, messages, temperature=None, **kwargs) -> str:
        """Devuelve solo el texto de la respuesta."""
        response = self._create(messages, temperature, **kwargs)
        return response.choices[0].message.content or ""

    def complete(self, messages, tools=None, temperature=None, **kwargs):
        """Devuelve el mensaje completo (.content y .tool_calls)."""
        if tools:
            kwargs["tools"] = tools
        response = self._create(messages, temperature, **kwargs)
        return response.choices[0].message

    def complete_stream(self, messages, tools=None, temperature=None, on_token=None, **kwargs):
        """Como complete(), pero en streaming: llama a on_token() por cada token."""
        if tools:
            kwargs["tools"] = tools
        temp = self.temperature if temperature is None else temperature

        partes_texto: list[str] = []
        slots_tools: dict[int, dict] = {}

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                stream=True,
                stream_options={"include_usage": True},
                **kwargs,
            )
            for chunk in stream:
                if getattr(chunk, "usage", None):
                    self.last_usage = chunk.usage
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if getattr(delta, "content", None):
                    partes_texto.append(delta.content)
                    if on_token:
                        on_token()
                if getattr(delta, "tool_calls", None):
                    for tc in delta.tool_calls:
                        slot = slots_tools.setdefault(
                            tc.index, {"id": None, "name": "", "arguments": ""}
                        )
                        if tc.id:
                            slot["id"] = tc.id
                        if tc.function:
                            if tc.function.name:
                                slot["name"] += tc.function.name
                            if tc.function.arguments:
                                slot["arguments"] += tc.function.arguments
                        if on_token:
                            on_token()
        except APIStatusError as error:
            raise LLMError(
                f"La API de DeepSeek devolvió un error "
                f"{error.status_code}: {error.message}"
            ) from error
        except Exception as error:  # noqa: BLE001
            raise LLMError(f"Error durante el streaming: {error}") from error

        tool_calls = None
        if slots_tools:
            tool_calls = [
                SimpleNamespace(
                    id=s["id"],
                    type="function",
                    function=SimpleNamespace(name=s["name"], arguments=s["arguments"]),
                )
                for _, s in sorted(slots_tools.items())
            ]
        return SimpleNamespace(content="".join(partes_texto) or None, tool_calls=tool_calls)


if __name__ == "__main__":
    cliente = LLMClient()
    respuesta = cliente.chat(
        [
            {"role": "system", "content": "Responde en una sola frase."},
            {"role": "user", "content": "Di 'hola' y confirma que la conexión funciona."},
        ]
    )
    print("Respuesta del modelo:\n", respuesta)
