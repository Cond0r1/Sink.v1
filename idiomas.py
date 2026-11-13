"""Idiomas de la interfaz (i18n).

Aquí vive TODO el texto que ve el usuario, en los tres idiomas disponibles.
Para cambiar lo que dice la interfaz, edita los textos de este archivo; para
añadir un idioma nuevo, agrega su código a ``IDIOMAS`` y su columna a ``TEXTOS``.

El comando ``/l`` abre un menú (flechas ↑/↓ + Enter) que llama a
``elegir_idioma`` y luego fija el idioma con ``set_idioma``. El resto del
programa pide los textos con ``t("clave")`` y siempre recibe la cadena en el
idioma activo.
"""

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style

# Idiomas disponibles: código -> nombre escrito EN SU PROPIA lengua.
IDIOMAS: dict[str, str] = {
    "es": "Español",
    "en": "English",
    "zh": "中文",
}

IDIOMA_POR_DEFECTO = "es"

# Idioma activo en este momento (lo cambia set_idioma).
_estado = {"idioma": IDIOMA_POR_DEFECTO}


def get_idioma() -> str:
    """Código del idioma activo ('es', 'en', 'zh')."""
    return _estado["idioma"]


def set_idioma(codigo: str) -> str:
    """Fija el idioma activo si el código es válido; devuelve el que quedó."""
    if codigo in IDIOMAS:
        _estado["idioma"] = codigo
    return _estado["idioma"]


def nombre_idioma(codigo: str | None = None) -> str:
    """Nombre del idioma (en su propia lengua). Sin argumento, el activo."""
    return IDIOMAS.get(codigo or _estado["idioma"], "")


# --- Textos de la interfaz -------------------------------------------------
# Cada clave trae una traducción por idioma. Los nombres de comandos (/reset,
# /clear, ...) no se traducen; solo cambia lo que está escrito alrededor.

_AYUDA_ES = """\
Atajos y comandos:
  /reset        borra la conversación
  /clear        limpia la pantalla   (también: clear / cls)
  /clih         limpieza periódica del historial (pregunta cada N mensajes)
  /persistencia          guarda la conversación entre sesiones
  /persistencia-disable  desactiva y pregunta si borrar la memoria
  /tokens       tokens gastados (sesión / por este agente)
  /tokens_p     saldo restante en dinero
  /l            cambia el idioma de la interfaz
  /key          muestra esta ayuda
  Ctrl+N        nueva sesión (pestaña)
  Ctrl+W        nombrar la pestaña
  Shift+Tab     cambia de modelo
  exit          termina el programa\
"""

_AYUDA_EN = """\
Shortcuts and commands:
  /reset        clears the conversation
  /clear        clears the screen    (also: clear / cls)
  /clih         periodic history cleanup (asks every N messages)
  /persistencia          saves the conversation across sessions
  /persistencia-disable  disables it and asks whether to wipe memory
  /tokens       tokens spent (session / by this agent)
  /tokens_p     remaining balance in money
  /l            change the interface language
  /key          shows this help
  Ctrl+N        new session (tab)
  Ctrl+W        name the tab
  Shift+Tab     switch model
  exit          quit the program\
"""

_AYUDA_ZH = """\
快捷键与命令：
  /reset        清空对话
  /clear        清屏                 （也可用：clear / cls）
  /clih         定期清理历史（每 N 条消息询问一次）
  /persistencia          跨会话保存对话
  /persistencia-disable  关闭并询问是否删除记忆
  /tokens       消耗的 token（会话 / 本智能体）
  /tokens_p     剩余金额余额
  /l            切换界面语言
  /key          显示此帮助
  Ctrl+N        新会话（标签页）
  Ctrl+W        重命名标签页
  Shift+Tab     切换模型
  exit          退出程序\
"""

TEXTOS: dict[str, dict[str, str]] = {
    "banner_hint": {
        "es": "Escribe /key para ver los atajos y comandos.",
        "en": "Type /key to see shortcuts and commands.",
        "zh": "输入 /key 查看快捷键与命令。",
    },
    "ayuda": {"es": _AYUDA_ES, "en": _AYUDA_EN, "zh": _AYUDA_ZH},
    "cerrando": {
        "es": "[!]Cerrando...",
        "en": "[!]Closing...",
        "zh": "[!]正在关闭……",
    },
    "reset_ok": {
        "es": "[memoria] Conversación borrada.",
        "en": "[memory] Conversation cleared.",
        "zh": "[记忆] 对话已清空。",
    },
    "clih_pregunta": {
        "es": "¿Cada cuántos mensajes reviso para limpiar? (0 = desactivar): ",
        "en": "Every how many messages should I check to clean up? (0 = disable): ",
        "zh": "每隔多少条消息检查一次清理？（0 = 关闭）： ",
    },
    "cancelado": {
        "es": "Cancelado.",
        "en": "Canceled.",
        "zh": "已取消。",
    },
    "clih_cada": {
        "es": "Revisaré cada {n} mensajes.",
        "en": "I'll check every {n} messages.",
        "zh": "我将每隔 {n} 条消息检查一次。",
    },
    "clih_off": {
        "es": "Limpieza periódica desactivada.",
        "en": "Periodic cleanup disabled.",
        "zh": "定期清理已关闭。",
    },
    "persist_on": {
        "es": "Persistencia ACTIVADA: se guardará la conversación.",
        "en": "Persistence ENABLED: the conversation will be saved.",
        "zh": "持久化已开启：对话将被保存。",
    },
    "persist_pregunta_borrar": {
        "es": "¿Borrar la memoria de conversación guardada? (s/n): ",
        "en": "Wipe the saved conversation memory? (y/n): ",
        "zh": "删除已保存的对话记忆吗？（y/n）： ",
    },
    "persist_off_borrada": {
        "es": "Persistencia DESACTIVADA y memoria borrada.",
        "en": "Persistence DISABLED and memory wiped.",
        "zh": "持久化已关闭，记忆已删除。",
    },
    "persist_off_conservada": {
        "es": "Persistencia DESACTIVADA (memoria conservada).",
        "en": "Persistence DISABLED (memory kept).",
        "zh": "持久化已关闭（保留记忆）。",
    },
    "tokens": {
        "es": "Tokens gastados (esta sesión): {n}",
        "en": "Tokens spent (this session): {n}",
        "zh": "消耗的 token（本次会话）：{n}",
    },
    "saldo": {
        "es": "Saldo restante: {total} {currency}",
        "en": "Remaining balance: {total} {currency}",
        "zh": "剩余余额：{total} {currency}",
    },
    "saldo_none": {
        "es": "No hay información de saldo.",
        "en": "No balance information available.",
        "zh": "没有余额信息。",
    },
    "cancelado_resp": {
        "es": "[cancelado]",
        "en": "[canceled]",
        "zh": "[已取消]",
    },
    "error_label": {
        "es": "[error]",
        "en": "[error]",
        "zh": "[错误]",
    },
    "hist_pregunta": {
        "es": "[historial] Van {n} mensajes. ¿Limpiar (l) o extender (e)?: ",
        "en": "[history] {n} messages so far. Trim (l) or extend (e)?: ",
        "zh": "[历史] 已有 {n} 条消息。精简 (l) 还是扩展 (e)？： ",
    },
    "hist_limpiado": {
        "es": "[historial] Limpiado: {n} mensajes eliminados.",
        "en": "[history] Trimmed: {n} messages removed.",
        "zh": "[历史] 已精简：删除了 {n} 条消息。",
    },
    "hist_extendido": {
        "es": "[historial] Extendido.",
        "en": "[history] Extended.",
        "zh": "[历史] 已扩展。",
    },
    "tab_nombre": {
        "es": "Nombre de la pestaña: ",
        "en": "Tab name: ",
        "zh": "标签页名称： ",
    },
    "idioma_cambiado": {
        "es": "Idioma cambiado a {nombre}.",
        "en": "Language changed to {nombre}.",
        "zh": "语言已切换为 {nombre}。",
    },
    "menu_idioma_titulo": {
        "es": "Elige un idioma:",
        "en": "Choose a language:",
        "zh": "选择语言：",
    },
    "menu_idioma_ayuda": {
        "es": "↑/↓ moverte · Enter elegir · Esc cancelar",
        "en": "↑/↓ move · Enter choose · Esc cancel",
        "zh": "↑/↓ 移动 · Enter 选择 · Esc 取消",
    },
}


def t(clave: str, **kwargs) -> str:
    """Texto de ``clave`` en el idioma activo (con relleno opcional .format)."""
    traducciones = TEXTOS.get(clave, {})
    texto = (
        traducciones.get(_estado["idioma"])
        or traducciones.get(IDIOMA_POR_DEFECTO)
        or clave
    )
    if kwargs:
        try:
            texto = texto.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            pass
    return texto


def elegir_idioma(actual: str | None = None) -> str | None:
    """Menú vertical con flechas para elegir idioma.

    Devuelve el código elegido ('es'/'en'/'zh') o ``None`` si se cancela
    (Esc o Ctrl+C). Se mueve con ↑/↓ y se confirma con Enter.
    """
    opciones = list(IDIOMAS.items())  # [("es", "Español"), ...]
    actual = actual or _estado["idioma"]
    seleccion = [0]
    for i, (codigo, _) in enumerate(opciones):
        if codigo == actual:
            seleccion[0] = i
            break
    resultado: list[str | None] = [None]

    kb = KeyBindings()

    @kb.add("up")
    def _arriba(event) -> None:
        seleccion[0] = (seleccion[0] - 1) % len(opciones)

    @kb.add("down")
    def _abajo(event) -> None:
        seleccion[0] = (seleccion[0] + 1) % len(opciones)

    @kb.add("enter")
    def _elegir(event) -> None:
        resultado[0] = opciones[seleccion[0]][0]
        event.app.exit()

    @kb.add("escape")
    @kb.add("c-c")
    @kb.add("q")
    def _cancelar(event) -> None:
        resultado[0] = None
        event.app.exit()

    def contenido():
        lineas = [("class:titulo", t("menu_idioma_titulo") + "\n")]
        for i, (_, nombre) in enumerate(opciones):
            if i == seleccion[0]:
                lineas.append(("class:activo", f" ❯ {nombre}\n"))
            else:
                lineas.append(("", f"   {nombre}\n"))
        lineas.append(("class:ayuda", t("menu_idioma_ayuda")))
        return lineas

    ventana = Window(
        content=FormattedTextControl(contenido, focusable=True),
        height=len(opciones) + 2,
    )
    estilo = Style.from_dict(
        {
            "titulo": "bold",
            "activo": "bold cyan",
            "ayuda": "fg:ansibrightblack",
        }
    )
    app = Application(
        layout=Layout(HSplit([ventana])),
        key_bindings=kb,
        style=estilo,
        full_screen=False,
        mouse_support=False,
    )
    try:
        app.run()
    except (EOFError, KeyboardInterrupt):
        return None
    return resultado[0]
