import os
from dataclasses import dataclass

@dataclass
class Config:
  # LLM Settings
  LLM_BASE_URL: str = "http://localhost:11434"
  LLM_MODEL: str = "llama2:7b"
  LLM_TEMPERATURE: float = 0.05
  LLM_MAX_TOKENS: int = 200

  # Current Date
  CURRENT_DATE: str = "2025-06-11"

  # Schema Settings
  SCHEMA_PATH: str = "config/schema.json"

  # Debug Settings
  DEBUG: bool = True
  LOG_LEVEL: str = "INFO"

config = Config() 