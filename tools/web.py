"""Herramientas de web: buscar en internet y leer el contenido de una página."""

import requests
from bs4 import BeautifulSoup

from .base import ToolError, tool

# User-Agent genérico (no revela nada del usuario ni del proyecto).
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; AgentBot/1.0; +https://example.com/bot)"
    )
}
_TIMEOUT = 20


@tool(
    name="web_search",
    description=(
        "Busca en internet y devuelve los primeros resultados con título, "
        "enlace y una breve descripción. Útil para encontrar información actual."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Términos de búsqueda."},
            "max_results": {
                "type": "integer",
                "description": "Número de resultados a devolver (por defecto 5).",
            },
        },
        "required": ["query"],
    },
)
def web_search(query: str, max_results: int = 5) -> str:
    try:
        resp = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers=_HEADERS,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as error:
        raise ToolError(f"Fallo al buscar: {error}")

    soup = BeautifulSoup(resp.text, "html.parser")
    resultados = []
    for item in soup.select(".result")[:max_results]:
        titulo_el = item.select_one(".result__a")
        snippet_el = item.select_one(".result__snippet")
        if not titulo_el:
            continue
        titulo = titulo_el.get_text(strip=True)
        enlace = titulo_el.get("href", "")
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
        resultados.append(f"- {titulo}\n  {enlace}\n  {snippet}")

    if not resultados:
        return f"Sin resultados para: {query}"
    return "\n".join(resultados)


@tool(
    name="fetch_url",
    description=(
        "Descarga una página web y devuelve su texto principal, ya limpio de "
        "etiquetas HTML. Útil para leer el contenido de un enlace."
    ),
    parameters={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL completa a leer (http/https)."},
            "max_chars": {
                "type": "integer",
                "description": "Máximo de caracteres a devolver (por defecto 4000).",
            },
        },
        "required": ["url"],
    },
)
def fetch_url(url: str, max_chars: int = 4000) -> str:
    if not url.startswith(("http://", "https://")):
        raise ToolError("La URL debe empezar por http:// o https://")
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as error:
        raise ToolError(f"Fallo al descargar la página: {error}")

    soup = BeautifulSoup(resp.text, "html.parser")
    for etiqueta in soup(["script", "style", "noscript"]):
        etiqueta.decompose()
    texto = soup.get_text(separator="\n")
    lineas = [ln.strip() for ln in texto.splitlines() if ln.strip()]
    texto = "\n".join(lineas)

    if len(texto) > max_chars:
        texto = texto[:max_chars] + "\n...[texto recortado]"
    return texto or "(la página no contiene texto legible)"
