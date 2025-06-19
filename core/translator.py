from typing import Optional
from config.settings import config
from core.llm_providers import LLMProviderFactory

class Translator:
  def __init__(self, provider_type: Optional[str] = None):
    resolved_provider_type = provider_type or config.LLM_PROVIDER
    self.provider = LLMProviderFactory.create_provider(resolved_provider_type)
    self.provider_type = resolved_provider_type

  def switch_provider(self, provider_type: str):
    """Switch between LLM providers"""
    self.provider = LLMProviderFactory.create_provider(provider_type)
    self.provider_type = provider_type

  def vietnamese_to_english(self, vietnamese_text: str) -> str:
    """Translate Vietnamese to English for better LLM processing"""
    if self.provider_type == "openai":
      prompt = f"""You are a translation API. Your only job is to translate Vietnamese to English. 
Return ONLY the English translation, no greetings, no explanations.

Vietnamese: "{vietnamese_text}"
English:"""
    else:
      # Ollama format
      prompt = f"""<|im_start|>system
You are a translation API. Your only job is to translate Vietnamese to English. 
Return ONLY the English translation, no greetings, no explanations.
<|im_end|>
<|im_start|>user
"{vietnamese_text}"
<|im_end|>
<|im_start|>assistant
"""

    try:
      response = self.provider.generate_response(
        prompt,
        temperature=0.1,
        max_tokens=50,
        stop=["<|im_start|>", "<|im_end|>"] if self.provider_type != "openai" else None
      )
      return response
    except Exception as e:
      print(f"Translation error: {e}")
      return vietnamese_text