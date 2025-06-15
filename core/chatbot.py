import json
import logging
from pathlib import Path
from typing import Dict, Any

from core.translator import Translator
from core.llm_handler import LLMHandler
from config.settings import config
from utils.validators import SchemaValidator

class BusinessAnalystChatbot:
  def __init__(self):
    # Setup logging
    self.logger = self._setup_logging()

    # Load schema
    self.schema = self._load_schema()

    # Initialize components
    self.translator = Translator()
    self.llm_handler = LLMHandler()
    self.validator = SchemaValidator(self.schema)

    self.logger.info("BusinessAnalystChatbot initialized")

  def _setup_logging(self):
    logging.basicConfig(
      level = getattr(logging, config.LOG_LEVEL),
      format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)
    
  def _load_schema(self) -> list:
    schema_path = Path(__file__).parent.parent / config.SCHEMA_PATH
    with open(schema_path, 'r', encoding = 'utf-8') as f:
      return json.load(f)
    
  def process_vietnamese_query(self, vietnamese_input: str) -> Dict[str, Any]:
    """Main processing pipeline"""
    try:
      self.logger.info(f"Processing query: {vietnamese_input}")

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
        'vietnamese_query': vietnamese_input,
        'english_query': english_query,
        'function_call': function_call,
      }
    
    except Exception as e:
      self.logger.error(f"Error processing query: {e}")
      return {
        'success': False,
        'error': str(e),
        'vietnamese_query': vietnamese_input,
        'english_query': None,
        'function_call': None,
      }