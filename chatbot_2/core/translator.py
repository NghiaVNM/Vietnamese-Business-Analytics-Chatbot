import requests
from typing import Optional
from ..config.settings import config

class Translator:
  def __init__(self, base_url: 'Optional[str]' = None):
    self.base_url = base_url or config.LLM_BASE_URL

  def vietnamese_to_english(self, vietnamese_text: str) -> str:
    """Translate Vietnamese to English for better LLM processing"""
    prompt = f"""
Translate this Vietnamese business query to English.Keep business terms precise.
Vietnamese: {vietnamese_text}
English:
    """

    payload = {
      "model": config.LLM_MODEL,
      "prompt": prompt,
      "stream": False,
      "options": {
        "temperature": config.LLM_TEMPERATURE,
        "max_tokens": config.LLM_MAX_TOKENS
      }
    }

    try:
      response = requests.post(f"{self.base_url}/api/generate", json = payload)
      result = response.json()
      return result['response'].strip()
    except Exception as e:
      return vietnamese_text