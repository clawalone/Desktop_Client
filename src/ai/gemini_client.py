import os
import json
import google.generativeai as genai


class GeminiClient:
    """
    Wrapper for Google Gemini Generative AI API.
    Provides text generation, automation commands, and memory persistence.
    """

    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini client.
        Args:
            api_key (str): Google Gemini API key. If None, will read from env var GEMINI_API_KEY.
            model (str): Gemini model name.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY env variable.")

        genai.configure(api_key=self.api_key)
        self.model_name = model

        # 🔹 Force automation instructions
        self.model = genai.GenerativeModel(
            self.model_name,
            system_instruction="""
You are a desktop automation agent.

When the user asks to open apps, type text, open URLs, or download anything,
you MUST return ONLY JSON in the following formats:

Single command example:
{
  "command": "open_app",
  "args": {"app": "Notepad"},
  "say": "Opening Notepad for you."
}

Multi-step example (e.g. "Open Notepad and type hello"):
[
  {
    "command": "open_app",
    "args": {"app": "Notepad"},
    "say": "Opening Notepad for you."
  },
  {
    "command": "type",
    "args": {"text": "hello"},
    "say": "Typing your message."
  }
]

Supported commands:
- open_app {"app": "<application name>"}
- type {"text": "<text to type>"}
- open_url {"url": "<url to open>"}
- download {"item": "<software or file name>"}  # Opens download/search page

⚠️ Rules:
- Never explain. Never say you cannot open apps.
- Always return JSON when automation is possible.
- If the request is purely conversational (not automation), reply normally in plain text.
"""
        )

        # Simple chat history
        self.history = []
        self.memory_file = os.path.join(os.path.dirname(__file__), "gemini_memory.json")
        self._load_memory()

    def generate(self, prompt: str) -> str:
        """
        Generate a response from Gemini.
        Args:
            prompt (str): User input.
        Returns:
            str: AI response text.
        """
        try:
            # Append to history
            self.history.append({"role": "user", "content": prompt})

            response = self.model.generate_content(prompt)

            if hasattr(response, "text"):
                reply = response.text
            elif hasattr(response, "candidates") and response.candidates:
                reply = response.candidates[0].content.parts[0].text
            else:
                reply = str(response)

            # Append AI reply
            self.history.append({"role": "model", "content": reply})

            return reply.strip()
        except Exception as e:
            return f"[Gemini Error] {str(e)}"

    def _load_memory(self):
        """Load previous chat memory if available."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []

    def save_memory(self):
        """Save chat history to file."""
        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving memory: {e}")
