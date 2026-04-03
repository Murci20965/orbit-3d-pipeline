import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """The central Configuration Manual for the entire Kitchen."""
    TRIPO_API_KEY = os.getenv("TRIPO_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    PROJECT_NAME = "Orbit-3D Engine"
    VERSION = "1.0.0"

settings = Settings()