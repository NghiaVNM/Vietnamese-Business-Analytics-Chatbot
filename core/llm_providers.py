import requests
import openai
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from config.settings import config

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from the LLM"""
        pass

class OllamaProvider(LLMProvider):
    """Ollama LLM provider"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.LLM_BASE_URL
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using Ollama API"""
        payload = {
            "model": config.LLM_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", config.LLM_TEMPERATURE),
                "max_tokens": kwargs.get("max_tokens", config.LLM_MAX_TOKENS),
                "stop": kwargs.get("stop", [])
            }
        }
        
        response = requests.post(f"{self.base_url}/api/generate", json=payload)
        result = response.json()
        return result['response'].strip()

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, api_key: str = None):
        self.client = openai.OpenAI(
            api_key=api_key or config.OPENAI_API_KEY
        )
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=kwargs.get("model", config.OPENAI_MODEL),
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", config.LLM_TEMPERATURE),
                max_tokens=kwargs.get("max_tokens", config.LLM_MAX_TOKENS),
                stop=kwargs.get("stop", None)
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    @staticmethod
    def create_provider(provider_type: str = None) -> LLMProvider:
        """Create LLM provider based on configuration"""
        provider_type = provider_type or config.LLM_PROVIDER
        
        if provider_type.lower() == "openai":
            if not config.OPENAI_API_KEY:
                raise ValueError("OpenAI API key is required but not found in environment variables")
            return OpenAIProvider()
        elif provider_type.lower() == "ollama":
            return OllamaProvider()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_type}")