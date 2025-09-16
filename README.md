Gemini Desktop Agent

A desktop assistant powered by Google’s Gemini AI that can open applications, type text, and open URLs on your Windows system.
It provides a modern chat interface built with PySide6 and integrates safe desktop automation via pyautogui and pygetwindow.

✨ Features

🤖 AI Assistant using Gemini (gemini-1.5-flash)

💻 Desktop Automation:

Open apps via Windows Start Menu

Type text into the active window

Open URLs in the default browser

🖼️ Modern UI with chat bubbles, sidebar, and dark theme

🔄 Command Execution: Natural language converted to structured commands

🛑 Failsafe: Move mouse to the top-left corner to abort automation

📂 Project Structure
.
├── commands.py       # Command registry and implementations
├── executor.py       # Parses AI responses and executes commands
├── gemini_client.py  # Wrapper for Google Gemini API
├── desktop.py        # Desktop automation functions (pyautogui, pygetwindow)
├── main_window.py    # PySide6 GUI with chat interface

🚀 Getting Started
1. Clone the repository
git clone https://github.com/yourusername/gemini-desktop-agent.git
cd gemini-desktop-agent

2. Create a virtual environment & install dependencies
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

pip install -r requirements.txt


Dependencies include:

pyautogui

pygetwindow

PySide6

google-generativeai

3. Set up API Key

Export your Google Gemini API key as an environment variable:

export GEMINI_API_KEY="your_api_key_here"   # Linux/Mac
setx GEMINI_API_KEY "your_api_key_here"     # Windows

4. Run the app
python -m main_window

🛠️ Usage

Type a natural language request like:

"Open Notepad"

"Type Hello World"

"Open YouTube"

The AI will respond with a structured command and execute it on your desktop.

📸 Screenshots

(Optional: Add screenshots of your chat UI here)

⚠️ Notes

Works on Windows (tested).

Ensure apps you request (like "Word", "Excel", "Notepad") exist in the Start Menu.

Automation may fail if the app takes time to load.

📜 License

MIT License © 2025 [Your Name]

Do you want me to also create a requirements.txt for this repo so the setup is smooth?
