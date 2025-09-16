from dataclasses import dataclass
from typing import Callable, Dict, Any
import pyautogui
import pygetwindow as gw
import time
import subprocess

@dataclass
class Command:
    name: str
    func: Callable[[Dict[str, Any]], str]
    description: str
    schema: Dict[str, Any]

REGISTRY: Dict[str, Command] = {}

def register(cmd: Command):
    REGISTRY[cmd.name] = cmd

# --- Office app paths and aliases ---
APP_PATHS = {
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE"
}

APP_ALIASES = {
    "microsoft word": "word",
    "ms word": "word",
    "word": "word",
    "microsoft excel": "excel",
    "ms excel": "excel",
    "excel": "excel",
    "microsoft powerpoint": "powerpoint",
    "ms powerpoint": "powerpoint",
    "powerpoint": "powerpoint"
}

# --- Helper functions ---
def _wait_for_window(app_name: str, timeout: float = 15) -> bool:
    """Wait until the app window is active and ready."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            windows = gw.getAllTitles()
            matches = [w for w in windows if app_name.lower() in w.lower()]
            if matches:
                gw.getWindowsWithTitle(matches[0])[0].activate()
                time.sleep(0.5)
                return True
        except Exception:
            pass
        time.sleep(0.3)
    return False

def _get_active_office_app() -> str:
    """Detect which Office app is currently active."""
    for app in APP_PATHS:
        if _wait_for_window(app, timeout=0.5):
            return app
    return ""

# --- Natural language parser ---
def parse_natural_command(command_text: str) -> Dict[str, str]:
    """
    Parse natural commands like:
    'open word and type hello and save MyDoc'
    into structured arguments.
    """
    command_text = command_text.lower()
    args = {"app": "", "text": "", "filename": ""}

    # --- Detect app ---
    for alias in APP_ALIASES:
        if alias in command_text:
            args["app"] = APP_ALIASES[alias]
            break

    # --- Detect text to type ---
    if "type" in command_text:
        after_type = command_text.split("type", 1)[1]
        if "save" in after_type:
            after_type = after_type.split("save", 1)[0]
        args["text"] = after_type.replace("and", "").strip()

    # --- Detect filename ---
    if "save" in command_text:
        after_save = command_text.split("save", 1)[1]
        args["filename"] = after_save.replace("and", "").strip()

    return args

# --- Commands ---
def _cmd_open_app(args: Dict[str, Any]) -> str:
    app_input = args.get("app", "").lower()
    app = APP_ALIASES.get(app_input)
    if not app:
        return f"⚠️ Unknown or missing app: '{app_input}'"

    subprocess.Popen([APP_PATHS[app]])
    if not _wait_for_window(app):
        return f"⚠️ Could not detect {app.capitalize()} window."
    return f"✅ Opened {app.capitalize()}"

def _cmd_new_document(args: Dict[str, Any]) -> str:
    app_input = args.get("app", "word").lower()
    app = APP_ALIASES.get(app_input, "word")

    if not _wait_for_window(app, timeout=15):
        return f"⚠️ {app.capitalize()} window not ready."

    pyautogui.hotkey("ctrl", "n")
    time.sleep(2)
    return f"📝 Created a new blank {app.capitalize()} document."

def _cmd_type(args: Dict[str, Any]) -> str:
    text = args.get("text", "")
    if not text:
        return "⚠️ Missing 'text'"

    app = _get_active_office_app()
    if not app:
        return "⚠️ No Office window is active."

    pyautogui.typewrite(text, interval=0.05)
    return f"✍️ Typed in {app.capitalize()}: '{text}'"

def _cmd_save_file(args: Dict[str, Any]) -> str:
    filename = args.get("filename", "")
    if not filename:
        return "⚠️ Missing 'filename'"

    app = _get_active_office_app()
    if not app:
        return "⚠️ No Office window is active."

    pyautogui.hotkey("ctrl", "s")
    time.sleep(0.5)
    pyautogui.typewrite(filename)
    time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(0.5)
    return f"💾 Saved {app.capitalize()} file as: {filename}"

# --- Full automated flow command ---
def _cmd_open_type_save(args: Dict[str, Any]) -> str:
    """Open app, create new document, type text, and optionally save."""
    # Parse if input is raw text
    if "command_text" in args:
        parsed_args = parse_natural_command(args["command_text"])
    else:
        parsed_args = args

    app_input = parsed_args.get("app", "").lower()
    text = parsed_args.get("text", "")
    filename = parsed_args.get("filename", "")

    open_result = _cmd_open_app({"app": app_input})
    if "⚠️" in open_result:
        return open_result

    new_doc_result = _cmd_new_document({"app": app_input})
    if "⚠️" in new_doc_result:
        return new_doc_result

    type_result = ""
    if text:
        type_result = _cmd_type({"text": text})

    save_result = ""
    if filename:
        save_result = _cmd_save_file({"filename": filename})

    return "\n".join(filter(None, [open_result, new_doc_result, type_result, save_result]))

# --- Register commands ---
register(Command("open_app", _cmd_open_app, "Open an Office application", {"app": "str"}))
register(Command("new_document", _cmd_new_document, "Create a new blank document/workbook/presentation", {"app": "str"}))
register(Command("type", _cmd_type, "Type text into the active Office window", {"text": "str"}))
register(Command("save_file", _cmd_save_file, "Save the current document/workbook/presentation", {"filename": "str"}))
register(Command("open_type_save", _cmd_open_type_save, "Open app, create new document, type text, and save", {"app": "str", "text": "str", "filename": "str", "command_text": "str"}))
