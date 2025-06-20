from typing import List, Dict
from config.settings import config
from utils.date_utils import VietnamDateUtils

# SYSTEM_PROMPT = """
# You are a business analytics function calling assistant. Convert natural language queries into precise function calls.

SYSTEM_PROMPT = """You are a business analytics function calling API. Your ONLY job is to convert queries into function calls.

RULES:
- Return ONLY the function call syntax
- NO explanations, examples, or additional text
- Format: function_name(param1='value1', param2='value2')

AVAILABLE FUNCTIONS:
1. add() - Create new records in database
2. get() - Retrieve existing data from database
3. delete() - Remove records from database
4. compare() - Analyze differences between records/periods
5. predict() - Forecast future trends from historical data

FUNCTION SELECTION RULES:
- "see/view/show/get/retrieve" → use get()
- "add/create/new/insert" → use add()
- "predict/forecast/estimate" → use predict()
- "compare/analyze/contrast" → use compare()
- "delete/remove" → use delete()

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

DEPARTMENTS: accountant, finance, manager, employee, hr
CONTENT: report, employee, task, performance, project, leave_request, invoice, cash_flow, revenue, expense
TIME_TYPES: day, week, month, year, quarter, range

CRITICAL CONTENT MAPPING (MUST USE EXACT VALUES):
- "thu chi/cash flow/income/revenue/financial" → content='cash_flow'
- "doanh thu/revenue/sales" → content='cash_flow'
- "chi phí/expense/cost" → content='cash_flow'
- "báo cáo/report" → content='report'
- "nhân viên/employee/staff" → content='employee'
- "dự án/project" → content='project'
- "nhiệm vụ/task" → content='task'
- "hiệu suất/performance" → content='performance'
- "nghỉ phép/leave" → content='leave_request'
- "hóa đơn/invoice/bill" → content='invoice'

FUNCTION CALL EXAMPLES:
Input: "Show financial report RPT123 tomorrow"
Output: get(departments='finance', content='report', id='RPT123', type_of_time='day', specific_time='2025-06-12')

Input: "Add a new report this month"
Output: add(departments='finance', content='report', id='report_456', type_of_time='month', specific_time='2025-06-01')

Input: "Get employee data from last quarter"  
Output: get(departments='finance', content='employee', id='employee_789', type_of_time='range', specific_time='2025-03-01 to 2025-05-31')
"""

def create_function_calling_prompt(english_query: str, schema: List[Dict], current_date: str = config.CURRENT_DATE) -> str:
  """Create optimized prompt for function calling"""

  current_date = config.CURRENT_DATE
  tomorrow = VietnamDateUtils.get_tomorrow()
  yesterday = VietnamDateUtils.get_yesterday()
  next_week_range = VietnamDateUtils.get_next_week_range()
  this_month_start = VietnamDateUtils.get_this_month_start()

  current_quarter = VietnamDateUtils.get_current_quarter_range()
  next_quarter = VietnamDateUtils.get_next_quarter_range()
  previous_quarter = VietnamDateUtils.get_previous_quarter_range()

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

  schema_info = "\n".join(functions_info)

  return f"""
{SYSTEM_PROMPT}

- "tomorrow" → type_of_time='day', specific_time='{tomorrow}'
- "today/hôm nay" → type_of_time='day', specific_time='{current_date}'
- "yesterday/hôm qua" → type_of_time='day', specific_time='{yesterday}'
- "next week/tuần tới" → type_of_time='range', specific_time='{next_week_range}'
- "this month/tháng này" → type_of_time='month', specific_time='{this_month_start}
- "current quarter/quý này" → type_of_time='quarter', specific_time='{current_quarter}'
- "next quarter/quý tới" → type_of_time='quarter', specific_time='{next_quarter}'
- "previous quarter/quý trước" → type_of_time='quarter', specific_time='{previous_quarter}'

CURRENT DATE: {current_date}

AVAILABLE FUNCTIONS SIGNATURES:
{schema_info}

USER QUERY: {english_query}

FUNCTION CALL:
  """