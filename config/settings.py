import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Config:
  # LLM Provider Settings
  LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")

  # LLM Settings
  LLM_BASE_URL: str = "http://localhost:11434"
  LLM_MODEL: str = "llama2:7b"

  # OpenAI Settings
  OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
  OPENAI_MODEL: str = "gpt-3.5-turbo"
  OPENAI_BASE_URL: str = "https://api.openai.com/v1"
  
  # Common LLM Settings
  LLM_TEMPERATURE: float = 0.05
  LLM_MAX_TOKENS: int = 500

  @property
  def CURRENT_DATE(self) -> str:
    """Get current date in Vietnam timezone (UTC+7)"""
    utc_now = datetime.utcnow()
    vietnam_time = utc_now + timedelta(hours=7)
    return vietnam_time.strftime('%Y-%m-%d')
  
  # Schema Settings
  SCHEMA_PATH: str = "config/schema.json"

  # Debug Settings
  DEBUG: bool = False
  LOG_LEVEL: str = "INFO"

config = Config() 