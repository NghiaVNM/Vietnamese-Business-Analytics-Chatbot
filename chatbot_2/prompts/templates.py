import json
from typing import List, Dict
from config.settings import config

SYSTEM_PROMPT = """
You are a business analytics function calling assistant. Convert natural language queries into precise function calls.

AVAILABLE FUNCTIONS:
1. add() - Create new records in database
2. get() - Retrieve existing data from database
3. delete() - Remove records from database
4. compare() - Analyze differences between records/periods
5. predict() - Forecast future ternds from historical data

CRITICAL RULES:
1. ONLY return valid function call syntax: function_name(param1='value1', param2='value2', ...)
2. Extract ALL required parameters from the input
3. Map time expressions to exact dates using current date context
4. Generate realistic IDs following pattern: {content_type}_{number}
5. Choose appropriate department based on context
6. NO explanations, NO additional text

TIME MAPPING EXAMPLES:
- "this month" → type_of_time='month', specific_time='2025-06-01'
- "last year" → type_of_time='year', specific_time='2024-01-01'  
- "yesterday" → type_of_time='day', specific_time='2025-06-10'
- "from June 1 to 15" → type_of_time='range', specific_time='2025-06-01 to 2025-06-15'

FUNCTION CALL EXAMPLES:
Input: "Add a new report this month"
Output: add(departments='finance', content='report', id='report_456', type_of_time='month', specific_time='2025-06-01')

Input: "Get employee data from last quarter"  
Output: get(departments='finance', content='employee', id='employee_789', type_of_time='range', specific_time='2025-03-01 to 2025-05-31')
"""

def create_function_calling_prompt(english_query: str, schema: List[Dict], current_date: str = config.CURRENT_DATE) -> str:
  """Create optimized prompt for function calling"""

  # Extract function info from schema
  functions_info = []
  for func in schema:
    params = []
    for param_name, param_info in func['parameters']['properties'].items():
      if 'enum' in param_info:
        params.append(f"{param_name}: {param_info['enum']}")
      else:
        params.append(f"{param_name}: {param_info['type']}")

    functions_info.append(f"{func['name']}({', '.join(params)})")

  schema_info = "\n.join(functions_info)"

  return f"""
{SYSTEM_PROMPT}

CURRENT DATE: {current_date}

AVAILABLE FUNCTIONS SIGNATURES:
{schema_info}

USER QUERY: {english_query}

FUNCTION CALL:
  """