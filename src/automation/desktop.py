"""Desktop automation using pyautogui, pygetwindow, and webbrowser only."""

import time
import webbrowser
import pyautogui
import pygetwindow as gw

pyautogui.FAILSAFE = True  # Move mouse to top-left to abort


def open_app_via_start(app_name: str):
    """Open an app via Windows Start Menu."""
    pyautogui.press("win")
    time.sleep(0.2)
    pyautogui.typewrite(app_name)
    time.sleep(0.2)
    pyautogui.press("enter")


def focus_window_by_title(partial: str) -> bool:
    """Bring a window with partial title into focus."""
    wins = [w for w in gw.getAllTitles() if partial.lower() in w.lower()]
    if not wins:
        return False
    w = gw.getWindowsWithTitle(wins[0])[0]
    w.activate()
    return True


def type_text(text: str):
    """Type text into the currently focused window."""
    pyautogui.typewrite(text, interval=0.02)


def open_url(url: str):
    """Open a URL in the default browser."""
    webbrowser.open(url)
