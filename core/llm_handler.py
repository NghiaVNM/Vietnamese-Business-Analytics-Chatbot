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

    # Try multiple patterns to extract function call
    patterns = [
      # Pattern 1: Inside markdown code block
      r"```(?:\w+)?\s*((?:add|get|delete|compare|predict)\s*\([^)]*\))\s*```",
      # Pattern 2: After "Function call syntax:" or similar
      r"(?:Function call syntax:|Function call:|Output:)?\s*((?:add|get|delete|compare|predict)\s*\([^)]*\))",
      # Pattern 3: Standalone function call
      r"((?:add|get|delete|compare|predict)\s*\([^)]*\))",
    ]

    function_call_text = None
    for pattern in patterns:
      match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
      if match:
        function_call_text = match.group(1).strip()
        break

    if not function_call_text:
      raise ValueError(f"Could not parse function call: {response}")

    # Extract function name and parameters
    func_pattern = r"(\w+)\s*\(\s*(.*?)\s*\)$"
    func_match = re.search(func_pattern, function_call_text)

    if not func_match:
      raise ValueError(f"Could not parse function call format: {function_call_text}")

    function_name = func_match.group(1)
    params_str = func_match.group(2)

    # Parse Parameters - improved regex
    parameters = {}
    if params_str:
      # Split by comma but respect quotes
      param_parts = []
      current_param = ""
      in_quotes = False
      quote_char = None
      
      for char in params_str:
        if char in ['"', "'"] and not in_quotes:
          in_quotes = True
          quote_char = char
          current_param += char
        elif char == quote_char and in_quotes:
          in_quotes = False
          quote_char = None
          current_param += char
        elif char == ',' and not in_quotes:
          param_parts.append(current_param.strip())
          current_param = ""
        else:
          current_param += char
      
      if current_param.strip():
        param_parts.append(current_param.strip())

      # Parse each parameter
      for param_part in param_parts:
        param_match = re.match(r"(\w+)\s*=\s*(.+)", param_part.strip())
        if param_match:
          param_name = param_match.group(1)
          param_value = param_match.group(2).strip()
          
          # Remove quotes if present
          if param_value.startswith('"') and param_value.endswith('"'):
            param_value = param_value[1:-1]
          elif param_value.startswith("'") and param_value.endswith("'"):
            param_value = param_value[1:-1]
          
          parameters[param_name] = param_value
    
    return {
      "name": function_name,
      "parameters": parameters
    }