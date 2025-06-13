import requests
import re
from typing import Dict, Any, List, Optional
from config.settings import config
from prompts.templates import create_function_calling_prompt

class LLMHandler:
  def __init__(self, base_url: 'Optional[str]' = None):
    self.base_url = base_url or config.LLM_BASE_URL

  def generate_function_call(self, english_query: str, schema: List[Dict]) -> Dict[str, Any]:
    """Generate function call from English query"""

    prompt = create_function_calling_prompt(english_query, schema)

    payload = {
      "model": config.LLM_MODEL,
      "prompt": prompt,
      "stream": False,
      "options": {
        "temperature": config.LLM_TEMPERATURE,
        "max_tokens": config.LLM_MAX_TOKENS,
      }
    }

    response = requests.post(f"{self.base_url}/api/generate", json=payload)
    result = response.json()

    return self.parse_function_call(result['response'])
  
  def parse_function_call(self, llm_response: str) -> Dict[str, Any]:
    """Parse function call from LLM response"""

    print(f"LLM Response: {llm_response}")
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