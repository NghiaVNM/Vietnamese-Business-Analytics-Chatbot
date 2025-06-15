from typing import Dict, Any, List
import re

class SchemaValidator:
  def __init__(self, schema: List[Dict]):
    self.schema = schema
    self.function_schemas = {func['name']: func for func in schema}

  def validate_function_call(self, function_call: Dict[str, Any]) -> bool:
    """Validate function call against schema"""
    function_name = function_call.get('name')
    parameters = function_call.get('parameters', {})

    if function_name not in self.function_schemas:
      raise ValueError(f"Unknown function: {function_name}")
    
    func_schema = self.function_schemas[function_name]
    required_params = func_schema['parameters'].get('required', [])
    properties = func_schema['parameters']['properties']

    # Check required parameters
    for param in required_params:
      if param not in parameters:
        raise ValueError(f"Missing required parameter: {param}")
      
    # Validate parameter values
    for param_name, param_value in parameters.items():
      if param_name in properties:
        self._validate_parameter(param_name, param_value, properties[param_name])
  
    return True
  
  def _validate_parameter(self, name: str, value: str, schema: Dict):
    """Validate individual parameter"""
    if 'enum' in schema:
      if value not in schema['enum']:
        raise ValueError(f"Invalid value for {name}: {value}. Must be on of {schema['enum']}")
    
    if 'pattern' in schema:
      if not re.match(schema['pattern'], value):
        raise ValueError(f"Invalid format for {name}: {value}")