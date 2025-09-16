import sys
import google.generativeai as genai
import pyautogui
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTextEdit, QPushButton, QLabel, QMessageBox
)

# 🔑 Configure Gemini API (replace with your key)
genai.configure(api_key="AIzaSyDlMFYGfifqfPIEICvfLKOZ1JO9-6wIGY8")


class AIAgent(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Crow Desktop Agent")
        self.setGeometry(200, 200, 500, 400)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Input + output widgets
        self.label = QLabel("Ask Gemini:")
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type your request...")
        self.button = QPushButton("Send to Gemini")
        self.response_box = QTextEdit()
        self.response_box.setReadOnly(True)

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.text_input)
        layout.addWidget(self.button)
        layout.addWidget(QLabel("Response:"))
        layout.addWidget(self.response_box)

        # Connect button
        self.button.clicked.connect(self.ask_gemini)

    def ask_gemini(self):
        user_input = self.text_input.toPlainText().strip()
        if not user_input:
            QMessageBox.warning(self, "Warning", "Please enter a request.")
            return

        # ✅ Use the correct Gemini model
        model = genai.GenerativeModel("gemini-1.5-flash")

        try:
            response = model.generate_content(user_input)
            reply = response.text
        except Exception as e:
            reply = f"Error: {str(e)}"

        # Show in GUI
        self.response_box.setText(reply)

        # 🔹 Example: Simple Automation
        if "open notepad" in user_input.lower():
            pyautogui.press("win")
            pyautogui.typewrite("notepad")
            pyautogui.press("enter")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AIAgent()
    window.show()
    sys.exit(app.exec())
