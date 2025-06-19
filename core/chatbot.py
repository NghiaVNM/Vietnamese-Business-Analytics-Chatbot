import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from core.translator import Translator
from core.llm_handler import LLMHandler
from config.settings import config
from utils.validators import SchemaValidator

class BusinessAnalystChatbot:
  def __init__(self, provider_type: Optional[str] = None):
    # Setup logging
    self.logger = self._setup_logging()

    # Load schema
    self.schema = self._load_schema()

    # Initialize components with provider
    self.current_provider = provider_type or config.LLM_PROVIDER
    self.translator = Translator(self.current_provider)
    self.llm_handler = LLMHandler(self.current_provider)
    self.validator = SchemaValidator(self.schema)

    self.logger.info(f"BusinessAnalystChatbot initialized with {self.current_provider} provider")

  def switch_provider(self, provider_type: str):
    """Switch between LLM providers"""
    try:
      self.translator.switch_provider(provider_type)
      self.llm_handler.switch_provider(provider_type)
      self.current_provider = provider_type
      self.logger.info(f"Switched to {provider_type} provider")
      return True
    except Exception as e:
      self.logger.error(f"Failed to switch provider: {e}")
      return False

  def _setup_logging(self):
    logging.basicConfig(
      level=getattr(logging, config.LOG_LEVEL),
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)
      
  def _load_schema(self) -> list:
    schema_path = Path(__file__).parent.parent / config.SCHEMA_PATH
    with open(schema_path, 'r', encoding='utf-8') as f:
      return json.load(f)
      
  def process_vietnamese_query(self, vietnamese_input: str) -> Dict[str, Any]:
    """Main processing pipeline"""
    try:
      self.logger.info(f"Processing query with {self.current_provider}: {vietnamese_input}")

      # Step 1: Translate to English
      english_query = self.translator.vietnamese_to_english(vietnamese_input)
      self.logger.debug(f"Translated: {english_query}")

      # Step 2: Generate function call
      function_call = self.llm_handler.generate_function_call(
        english_query,
        self.schema
      )
      self.logger.debug(f"Function call: {function_call}")

      # Step 3: Validate function call
      self.validator.validate_function_call(function_call)

      return {
        'success': True,
        'provider': self.current_provider,
        'vietnamese_query': vietnamese_input,
        'english_query': english_query,
        'function_call': function_call,
      }
    
    except Exception as e:
      self.logger.error(f"Error processing query: {e}")
      return {
        'success': False,
        'error': str(e),
        'provider': self.current_provider,
        'vietnamese_query': vietnamese_input,
        'english_query': None,
        'function_call': None,
      }