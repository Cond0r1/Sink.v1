# Sink · Agente DeepSeek

<img width="1108" height="540" alt="image" src="https://github.com/user-attachments/assets/1fac1900-7ca7-4952-b965-eb58c6e726c1" />



**Idiomas / Languages / 语言:** [Español](#español) · [English](#english) · [中文](#中文)

Un agente de terminal construido sobre la API de DeepSeek: razona en bucle, usa
herramientas reales (archivos, shell, web, memoria), recuerda entre sesiones y
tiene una interfaz cuidada (streaming de tokens en vivo, resaltado, atajos de
teclado y seguridad integrada).

---

## Español

### ¿Qué es?

**Sink** es un agente de inteligencia artificial que corre en la terminal. A
diferencia de un chat normal, no solo conversa: **actúa** en tu equipo usando
herramientas, dentro de límites de seguridad que tú defines.

### Características

- 🧠 **Bucle de razonamiento** con *function calling* de DeepSeek.
- 🧰 **Herramientas reales:** archivos (leer/escribir/mover/borrar), comandos de
  shell, búsqueda y lectura web, y memoria clave-valor.
- 💾 **Memoria persistente:** activa `/persistencia` para recordar la
  conversación entre sesiones; `/persistencia-disable` la apaga y, si quieres,
  borra lo guardado.
- 🧹 **Limpieza del historial:** con `/clih` el agente revisa cada N mensajes y
  te pregunta si recortar o extender el historial (ahorra tokens en charlas
  largas).
- 🌊 **Streaming en vivo:** la respuesta se genera token a token; si tarda más de
  2 s aparece el indicador animado **"Diving"** con una olita, el tiempo
  transcurrido y los tokens recibidos.
- 📊 **Tokens y saldo:** `/tokens` muestra los tokens gastados en la sesión y
  `/tokens_p` consulta el saldo restante de tu cuenta DeepSeek en dinero.
- ⛔ **Cancelable:** `Ctrl+C` corta una respuesta a medias de forma segura y
  deja el historial limpio (sin pares de herramientas rotos).
- 🔒 **Seguridad:** acceso restringido a directorios permitidos y confirmación
  para comandos peligrosos (`rm`, `mv`, `cp`...).
- 🎨 **Interfaz pulida:** banner con logo ASCII (versión, modelo y carpeta
  actual), Markdown renderizado, resaltado de comandos al escribir, y listados
  de archivos con emoji por tipo.
- 🔁 **Multimodelo:** cambia entre modelos (`deepseek-chat`, `deepseek-reasoner`)
  con `Shift+Tab`.
- ⚙️ **Configurable por `.env`:** modelos disponibles, máximo de iteraciones,
  temperatura, directorios permitidos y más.

### Estructura

```
config.py     Configuración (lee el .env)
llm.py        Conexión con DeepSeek: reintentos, streaming y consulta de saldo
memory.py     Historial de la conversación (con persistencia y recorte)
agent.py      Núcleo: el bucle del agente y el conteo de tokens
tools/        Herramientas (base, archivos, shell, web, memoria)
atajos.py     Atajos de teclado
main.py       Interfaz de terminal + arranque
COMANDOS.md   Referencia rápida de comandos y atajos
settings.json Ajustes persistentes (persistencia, intervalo de /clih)
history.json  Conversación guardada (solo si activas la persistencia)
```

### Instalación

```bash
git clone <tu-repo>
cd Sink
pip install -e .         # instala dependencias y el comando 'deepseek'
cp .env.example .env     # y rellena tu DEEPSEEK_API_KEY
deepseek                 # o: python main.py
```

### Configuración (`.env`)

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `DEEPSEEK_API_KEY` | Tu clave de la API (obligatoria) | — |
| `DEEPSEEK_BASE_URL` | URL base de la API | `https://api.deepseek.com` |
| `MODEL` | Modelo inicial | `deepseek-chat` |
| `AVAILABLE_MODELS` | Modelos que rotan con `Shift+Tab` (coma) | `deepseek-chat,deepseek-reasoner` |
| `MAX_ITERATIONS` | Máx. pasos de razonamiento por turno | `15` |
| `TEMPERATURE` | Temperatura del modelo (0.0–2.0) | `0.7` |
| `ALLOWED_DIRS` | Directorios donde puede trabajar (coma) | `.` |
| `CONFIRM_DANGEROUS` | Pedir confirmación en comandos peligrosos | `true` |
| `MEMORY_FILE` | Archivo de la memoria clave-valor | `memory.json` |

### Comandos y atajos

| Comando / Atajo | Acción |
|---|---|
| `/key` (o `/help`) | Muestra los atajos y comandos |
| `/reset` | Borra la conversación |
| `/clear` (o `clear` / `cls`) | Limpia la pantalla |
| `/clih` | Limpieza periódica del historial (pregunta cada N mensajes) |
| `/persistencia` | Guarda la conversación entre sesiones |
| `/persistencia-disable` | Desactiva y pregunta si borrar la memoria |
| `/tokens` | Tokens gastados en esta sesión |
| `/tokens_p` | Saldo restante en dinero |
| `exit` (o `salir` / `quit`) | Termina el programa |
| `Shift+Tab` | Cambia de modelo |
| `Ctrl+N` | Nueva sesión (pestaña) |
| `Ctrl+W` | Renombra la pestaña |
| `Ctrl+C` | Cancela la respuesta en curso |

> **Importante:** nunca subas tu archivo `.env` (contiene tu API key). El
> `.gitignore` ya lo excluye.

---

## English

### What is it?

**Sink** is an AI agent that runs in your terminal. Unlike a regular chatbot, it
doesn't just talk — it **acts** on your machine using tools, within the security
boundaries you define.
<img width="1108" height="540" alt="image" src="https://github.com/user-attachments/assets/d1306d76-54bc-48fb-993d-ee3b07650ef1" />

### Features

- 🧠 **Reasoning loop** using DeepSeek function calling.
- 🧰 **Real tools:** files (read/write/move/delete), shell commands, web search
  and page reading, and key-value memory.
- 💾 **Persistent memory:** turn on `/persistencia` to remember the conversation
  across sessions; `/persistencia-disable` turns it off and optionally wipes
  what was saved.
- 🧹 **History cleanup:** with `/clih` the agent checks every N messages and asks
  whether to trim or extend the history (saves tokens in long chats).
- 🌊 **Live streaming:** the reply is generated token by token; if it takes more
  than 2 s an animated **"Diving"** indicator appears with a wave, the elapsed
  time, and the tokens received.
- 📊 **Tokens and balance:** `/tokens` shows the tokens spent this session and
  `/tokens_p` queries your remaining DeepSeek account balance in money.
- ⛔ **Cancelable:** `Ctrl+C` safely stops a reply mid-way and leaves the history
  clean (no broken tool pairs).
- 🔒 **Security:** access restricted to allowed directories and confirmation for
  dangerous commands (`rm`, `mv`, `cp`...).
- 🎨 **Polished UI:** banner with ASCII logo (version, model, and current
  folder), rendered Markdown, command highlighting as you type, and file
  listings with a per-type emoji.
- 🔁 **Multi-model:** switch models (`deepseek-chat`, `deepseek-reasoner`) with
  `Shift+Tab`.
- ⚙️ **Configurable via `.env`:** available models, max iterations, temperature,
  allowed directories, and more.

### Structure

```
config.py     Configuration (reads .env)
llm.py        DeepSeek connection: retries, streaming, and balance lookup
memory.py     Conversation history (with persistence and trimming)
agent.py      Core: the agent loop and token counting
tools/        Tools (base, files, shell, web, memory)
atajos.py     Keyboard shortcuts
main.py       Terminal UI + startup
COMANDOS.md   Quick reference for commands and shortcuts
settings.json Persistent settings (persistence, /clih interval)
history.json  Saved conversation (only if you enable persistence)
```

### Installation

```bash
git clone <your-repo>
cd Sink
pip install -e .         # installs dependencies and the 'deepseek' command
cp .env.example .env     # then fill in your DEEPSEEK_API_KEY
deepseek                 # or: python main.py
```

### Configuration (`.env`)

| Variable | What it does | Default |
|---|---|---|
| `DEEPSEEK_API_KEY` | Your API key (required) | — |
| `DEEPSEEK_BASE_URL` | API base URL | `https://api.deepseek.com` |
| `MODEL` | Initial model | `deepseek-chat` |
| `AVAILABLE_MODELS` | Models cycled with `Shift+Tab` (comma) | `deepseek-chat,deepseek-reasoner` |
| `MAX_ITERATIONS` | Max reasoning steps per turn | `15` |
| `TEMPERATURE` | Model temperature (0.0–2.0) | `0.7` |
| `ALLOWED_DIRS` | Directories it may work in (comma) | `.` |
| `CONFIRM_DANGEROUS` | Ask for confirmation on dangerous commands | `true` |
| `MEMORY_FILE` | Key-value memory file | `memory.json` |

### Commands and shortcuts

| Command / Shortcut | Action |
|---|---|
| `/key` (or `/help`) | Show shortcuts and commands |
| `/reset` | Clear the conversation |
| `/clear` (or `clear` / `cls`) | Clear the screen |
| `/clih` | Periodic history cleanup (asks every N messages) |
| `/persistencia` | Save the conversation across sessions |
| `/persistencia-disable` | Disable and ask whether to wipe memory |
| `/tokens` | Tokens spent this session |
| `/tokens_p` | Remaining balance in money |
| `exit` (or `salir` / `quit`) | Quit the program |
| `Shift+Tab` | Switch model |
| `Ctrl+N` | New session (tab) |
| `Ctrl+W` | Rename the tab |
| `Ctrl+C` | Cancel the reply in progress |

> **Important:** never commit your `.env` file (it holds your API key). The
> `.gitignore` already excludes it.

---

## 中文

### 这是什么？
<img width="1108" height="540" alt="image" src="https://github.com/user-attachments/assets/33658554-106e-4247-83c9-d66cab606642" />

**Sink** 是一个运行在终端中的 AI 智能体。与普通聊天机器人不同，它不仅会对话，
还能在你设定的安全边界内使用工具**在你的电脑上执行操作**。

### 功能特性

- 🧠 **推理循环**：基于 DeepSeek 的函数调用（function calling）。
- 🧰 **真实工具**：文件（读/写/移动/删除）、Shell 命令、网页搜索与阅读，以及
  键值记忆。
- 💾 **持久记忆**：开启 `/persistencia` 可跨会话记住对话；`/persistencia-disable`
  则关闭它，并可选择删除已保存的内容。
- 🧹 **历史清理**：使用 `/clih`，智能体每隔 N 条消息会询问你是要精简还是扩展
  历史记录（在长对话中节省 token）。
- 🌊 **实时流式输出**：回复逐 token 生成；若超过 2 秒，会出现带波浪的动画指示器
  **"Diving"**，并显示已用时间与收到的 token 数。
- 📊 **Token 与余额**：`/tokens` 显示本次会话消耗的 token，`/tokens_p` 查询你
  DeepSeek 账户剩余的金额余额。
- ⛔ **可取消**：`Ctrl+C` 可安全中断生成中的回复，并保持历史记录干净（不留下
  残缺的工具调用对）。
- 🔒 **安全机制**：仅允许访问指定目录，并对危险命令（`rm`、`mv`、`cp`……）进行
  二次确认。
- 🎨 **精致界面**：带 ASCII Logo 的横幅（版本、模型与当前目录）、Markdown 渲染、
  输入时的命令高亮，以及按类型显示 emoji 的文件列表。
- 🔁 **多模型**：用 `Shift+Tab` 在模型之间切换（`deepseek-chat`、
  `deepseek-reasoner`）。
- ⚙️ **通过 `.env` 配置**：可用模型、最大迭代次数、温度、允许的目录等。

### 项目结构

```
config.py     配置（读取 .env）
llm.py        DeepSeek 连接：重试、流式输出与余额查询
memory.py     对话历史（支持持久化与精简）
agent.py      核心：智能体循环与 token 计数
tools/        工具（基础、文件、Shell、网页、记忆）
atajos.py     键盘快捷键
main.py       终端界面 + 启动
COMANDOS.md   命令与快捷键速查
settings.json 持久化设置（持久化开关、/clih 间隔）
history.json  已保存的对话（仅在开启持久化时）
```

### 安装

```bash
git clone <你的仓库>
cd Sink
pip install -e .         # 安装依赖和 'deepseek' 命令
cp .env.example .env     # 然后填入你的 DEEPSEEK_API_KEY
deepseek                 # 或：python main.py
```

### 配置（`.env`）

| 变量 | 作用 | 默认值 |
|---|---|---|
| `DEEPSEEK_API_KEY` | 你的 API 密钥（必填） | — |
| `DEEPSEEK_BASE_URL` | API 基础 URL | `https://api.deepseek.com` |
| `MODEL` | 初始模型 | `deepseek-chat` |
| `AVAILABLE_MODELS` | 用 `Shift+Tab` 轮换的模型（逗号分隔） | `deepseek-chat,deepseek-reasoner` |
| `MAX_ITERATIONS` | 每轮最大推理步数 | `15` |
| `TEMPERATURE` | 模型温度（0.0–2.0） | `0.7` |
| `ALLOWED_DIRS` | 允许工作的目录（逗号分隔） | `.` |
| `CONFIRM_DANGEROUS` | 危险命令是否需要确认 | `true` |
| `MEMORY_FILE` | 键值记忆文件 | `memory.json` |

### 命令与快捷键

| 命令 / 快捷键 | 操作 |
|---|---|
| `/key`（或 `/help`） | 显示快捷键与命令 |
| `/reset` | 清空对话 |
| `/clear`（或 `clear` / `cls`） | 清屏 |
| `/clih` | 定期清理历史（每 N 条消息询问一次） |
| `/persistencia` | 跨会话保存对话 |
| `/persistencia-disable` | 关闭并询问是否删除记忆 |
| `/tokens` | 本次会话消耗的 token |
| `/tokens_p` | 剩余金额余额 |
| `exit`（或 `salir` / `quit`） | 退出程序 |
| `Shift+Tab` | 切换模型 |
| `Ctrl+N` | 新会话（标签页） |
| `Ctrl+W` | 重命名标签页 |
| `Ctrl+C` | 取消正在生成的回复 |

> **重要：** 切勿提交你的 `.env` 文件（其中包含 API 密钥）。`.gitignore` 已将其
> 排除。

---

### Licencia / License / 许可

MIT
