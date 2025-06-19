import re
from typing import Dict, Any, List, Optional
from config.settings import config
from prompts.templates import create_function_calling_prompt
from core.llm_providers import LLMProviderFactory

class LLMHandler:
  def __init__(self, provider_type: Optional[str] = None):
    resolved_provider_type = provider_type or config.LLM_PROVIDER
    self.provider = LLMProviderFactory.create_provider(resolved_provider_type)
    self.provider_type = resolved_provider_type

  def switch_provider(self, provider_type: str):
    """Switch between LLM providers"""
    self.provider = LLMProviderFactory.create_provider(provider_type)
    self.provider_type = provider_type
    print(f"Switched to {provider_type} provider")

  def generate_function_call(self, english_query: str, schema: List[Dict]) -> Dict[str, Any]:
    """Generate function call from English query"""
    prompt = create_function_calling_prompt(english_query, schema)
    
    # Generate response using the current provider
    response = self.provider.generate_response(
      prompt,
      temperature=config.LLM_TEMPERATURE,
      max_tokens=config.LLM_MAX_TOKENS
    )
    
    return self.parse_function_call(response)
  
  def parse_function_call(self, llm_response: str) -> Dict[str, Any]:
    """Parse function call from LLM response"""
    print(f"LLM Response ({self.provider_type}): {llm_response}")
    response = llm_response.strip()

    # Extract function name and parameters
    pattern = r"(\w+)\s*\(\s*(.*?)\s*\)"
    match = re.search(pattern, response)

    if not match:
      raise ValueError(f"Could not parse function call: {response}")

    function_name = match.group(1)
    params_str = match.group(2)

    # Parse Parameters
    parameters = {}
    if params_str:
      param_pairs = re.findall(r"(\w+)=(?:'([^']*)'|\"([^\"]*)\"|([^,]*))", params_str)

      for param_match in param_pairs:
        param_name = param_match[0]
        param_value = param_match[1] or param_match[2] or param_match[3]
        parameters[param_name] = param_value.strip()
    
    return {
      "name": function_name,
      "parameters": parameters
    }