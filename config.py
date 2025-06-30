# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "gpt-3.5-turbo"
    TEMPERATURE = 0.7
    MAX_TOKENS = 1000

    # Validate required keys
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is required in .env file")


# Test configuration
if __name__ == "__main__":
    config = Config()
    print(f"✅ Configuration loaded successfully")
    print(f"📍 Using model: {config.MODEL_NAME}")