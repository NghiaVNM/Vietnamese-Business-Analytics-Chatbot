from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Config:
  # LLM Settings
  LLM_BASE_URL: str = "http://localhost:11434"
  LLM_MODEL: str = "llama2:7b"
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