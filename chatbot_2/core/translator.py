import requests
from typing import Optional
from config.settings import config

class Translator:
  def __init__(self, base_url: 'Optional[str]' = None):
    self.base_url = base_url or config.LLM_BASE_URL

  def vietnamese_to_english(self, vietnamese_text: str) -> str:
    """Translate Vietnamese to English for better LLM processing"""
    prompt = f"""<|im_start|>system
You are a translation API. Your only job is to translate Vietnamese to English. 
Return ONLY the English translation, no greetings, no explanations.
<|im_end|>
<|im_start|>user
"{vietnamese_text}"
<|im_end|>
<|im_start|>assistant
"""

    payload = {
      "model": config.LLM_MODEL,
      "prompt": prompt,
      "stream": False,
      "options": {
        "temperature": 0.1,
        "max_tokens": 50,
        "stop": ["<|im_start|>", "<|im_end|>"]
      }
    }

    try:
      response = requests.post(f"{self.base_url}/api/generate", json = payload)
      result = response.json()
      return result['response'].strip()
    except Exception as e:
      return vietnamese_text