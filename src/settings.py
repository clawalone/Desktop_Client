import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Settings:
    api_key: str
    model: str = "gemini-1.5-flash"
    app_name: str = "Crow Desktop Agent"

    @staticmethod
    def load() -> "Settings":
        # Load .env if present
        load_dotenv(override=False)
        api_key = os.getenv("GEMINI_API_KEY", "")
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing. Create a .env file with your key.")
        return Settings(api_key=api_key, model=model)
