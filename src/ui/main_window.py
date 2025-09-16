import logging
import json
import re
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QStatusBar, QMessageBox,
    QLabel, QListWidget, QListWidgetItem, QSplitter,
    QScrollArea, QSizePolicy
)
from src.ai.gemini_client import GeminiClient   # ✅ switched from HuggingFace to Gemini
from src.agent.executor import try_execute_from_text
from datetime import datetime

logger = logging.getLogger(__name__)


# ---------------- Worker Thread ----------------
class WorkerSignals(QObject):
    finished = Signal(str)
    error = Signal(str)


class GenerateWorker(QRunnable):
    def __init__(self, client: GeminiClient, prompt: str):
        super().__init__()
        self.client = client
        self.prompt = prompt
        self.signals = WorkerSignals()

    def run(self):
        try:
            text = self.client.generate(self.prompt)
            self.signals.finished.emit(text)
        except Exception as e:
            self.signals.error.emit(str(e))


# ---------------- Chat Bubble UI ----------------
class ChatBubble(QWidget):
    def __init__(self, who: str, text: str, is_user: bool = False, is_system: bool = False):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)

        # --- Alignment ---
        if is_system:
            layout.setAlignment(Qt.AlignCenter)
        else:
            layout.setAlignment(Qt.AlignRight if is_user else Qt.AlignLeft)

        # Bubble container
        bubble = QWidget()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(12, 8, 12, 8)

        # Message text
        msg = QLabel(text)
        msg.setWordWrap(True)
        msg.setStyleSheet("color: white; font-size: 14px;")
        msg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        msg.setMaximumWidth(500)

        # Timestamp
        time_lbl = QLabel(datetime.now().strftime("%H:%M"))
        time_lbl.setStyleSheet("color: #ddd; font-size: 11px;")
        time_lbl.setAlignment(Qt.AlignRight)

        bubble_layout.addWidget(msg)
        bubble_layout.addWidget(time_lbl)

        # --- Colors ---
        if is_system:
            color = "#555"     # grey
        elif is_user:
            color = "#4CAF50"  # green
        else:
            color = "#673AB7"  # purple

        bubble.setStyleSheet(f"""
            background-color: {color};
            border-radius: 12px;
        """)
        bubble.setMaximumWidth(550)

        layout.addWidget(bubble)


class ChatHistory(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)

    def add_message(self, who: str, text: str, is_user=False, is_system=False):
        bubble = ChatBubble(who, text, is_user, is_system)
        self.layout.addWidget(bubble)


# ---------------- Main Window ----------------
class MainWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.setWindowTitle(settings.app_name if hasattr(settings, "app_name") else "Gemini Desktop Agent")
        self.resize(1100, 650)

        # ✅ Use Gemini AI client
        self.client = GeminiClient(settings.api_key, settings.model)
        self.pool = QThreadPool.globalInstance()

        # --- Sidebar ---
        sidebar = QListWidget()
        sidebar.setFixedWidth(200)
        sidebar.addItem(QListWidgetItem("🏠  Home"))
        sidebar.addItem(QListWidgetItem("💬  Chat"))
        sidebar.addItem(QListWidgetItem("⚙  Settings"))
        sidebar.addItem(QListWidgetItem("ℹ  About"))
        sidebar.setStyleSheet("""
            QListWidget {
                background-color: #222;
                color: #EEE;
                border: none;
                font-size: 16px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 12px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background: #444;
            }
        """)

        # --- Main Chat Area ---
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)

        # Header
        header = QLabel("🤖 Gemini AI Assistant")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("padding: 12px; background:#673AB7; color:white; border-radius:8px;")
        chat_layout.addWidget(header)

        # Chat history (scrollable with bubbles)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.chat_history = ChatHistory()
        scroll.setWidget(self.chat_history)
        chat_layout.addWidget(scroll)

        # Input row
        input_row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message...")
        self.input.setFont(QFont("Segoe UI", 12))
        self.input.returnPressed.connect(self.on_send)
        self.input.setStyleSheet("""
            QLineEdit {
                background:#FFF;
                color:#000;
                border:1px solid #CCC;
                border-radius:20px;
                padding:10px 15px;
            }
        """)

        self.send_btn = QPushButton("➤")
        self.send_btn.setFixedSize(50, 50)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background:#673AB7;
                border-radius:25px;
                color:white;
                font-size:18px;
            }
            QPushButton:hover { background:#512DA8; }
        """)
        self.send_btn.clicked.connect(self.on_send)

        input_row.addWidget(self.input)
        input_row.addWidget(self.send_btn)
        chat_layout.addLayout(input_row)

        # --- Splitter for Sidebar + Chat ---
        splitter = QSplitter()
        splitter.addWidget(sidebar)
        splitter.addWidget(chat_area)
        splitter.setStretchFactor(1, 4)
        self.setCentralWidget(splitter)

        # Status bar
        self.setStatusBar(QStatusBar())
        self.is_dark = True
        self.apply_theme()

    # --- Chat Helpers ---
    def append_message(self, who: str, text: str):
        if who == "System":
            self.chat_history.add_message(who, text, is_system=True)
        else:
            self.chat_history.add_message(who, text, is_user=(who == "You"))

    def on_send(self):
        text = self.input.text().strip()
        if not text:
            return
        self.append_message("You", text)
        self.input.clear()

        worker = GenerateWorker(self.client, text)
        worker.signals.finished.connect(self.on_ai_reply)
        worker.signals.error.connect(lambda e: QMessageBox.critical(self, "Error", e))
        self.pool.start(worker)

    def on_ai_reply(self, text: str):
        """
        Handle Gemini replies. Supports JSON commands or plain text.
        """
        executed = False

        try:
            data = json.loads(text)
            if isinstance(data, list):
                for cmd in data:
                    say, result = try_execute_from_text(json.dumps(cmd))
                    if say:
                        self.append_message("Gemini", say)
                    if result:
                        self.append_message("System", result)
                executed = True
            elif isinstance(data, dict):
                say, result = try_execute_from_text(text)
                if say:
                    self.append_message("Gemini", say)
                if result:
                    self.append_message("System", result)
                executed = True
        except Exception:
            pass

        # Fallback for plain text
        if not executed:
            say, result = try_execute_from_text(text)
            self.append_message("Gemini", say or text)
            if result:
                self.append_message("System", result)

    def closeEvent(self, event):
        # Optional: save memory if implemented later
        if hasattr(self.client, "save_memory"):
            self.client.save_memory()
        super().closeEvent(event)

    def apply_theme(self):
        if self.is_dark:
            self.setStyleSheet("""
                QMainWindow { background-color: #121212; color: #EEE; }
                QScrollArea { background-color: #1E1E1E; border:none; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #F5F5F5; color: #111; }
                QScrollArea { background-color: #FFFFFF; border:1px solid #CCC; }
            """)
