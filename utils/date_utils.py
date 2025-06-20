from datetime import datetime, timedelta
import re
from typing import Optional

class VietnamDateUtils:
  @staticmethod
  def get_vietnam_date() -> datetime:
    """Get current date in Vietnam timezone (UTC+7)"""
    utc_now = datetime.utcnow()
    return utc_now + timedelta(hours=7)
  
  @staticmethod
  def get_current_data() -> str:
    """Get current date in Vietnam timezone (YYYY-MM-DD)"""
    return VietnamDateUtils.get_vietnam_date().strftime('%Y-%m-%d')
  
  @staticmethod
  def get_tomorrow() -> str:
    """Get tomorrow's date in Vietnam timezone (YYYY-MM-DD)"""
    tomorrow = VietnamDateUtils.get_vietnam_date() + timedelta(days=1)
    return tomorrow.strftime('%Y-%m-%d')
  
  @staticmethod
  def get_yesterday() -> str:
    """Get yesterday's date in Vietnam timezone (YYYY-MM-DD)"""
    yesterday = VietnamDateUtils.get_vietnam_date() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')
  
  @staticmethod
  def get_next_week_range() -> str:
    """Get next week date rang (7 days from now for 1 week)"""
    vietnam_now = VietnamDateUtils.get_vietnam_date()
    next_week_start = vietnam_now + timedelta(days=7)
    next_week_end = next_week_start + timedelta(days=6)
    return f"{next_week_start.strftime('%Y-%m-%d')} to {next_week_end.strftime('%Y-%m-%d')}"
  
  @staticmethod
  def get_this_month_start() -> str:
      """Get first day of current month"""
      vietnam_now = VietnamDateUtils.get_vietnam_date()
      return vietnam_now.replace(day=1).strftime("%Y-%m-%d")
  
  @staticmethod
  def get_quarter_range(quarter_offset: int = 1, year: Optional[int] = None) -> str:
    current = VietnamDateUtils.get_vietnam_date()
    
    if year is None:
      year = current.year
    
    # Determine current quarter (1-4)
    current_quarter = (current.month - 1) // 3 + 1
    
    # Calculate target quarter
    target_quarter = current_quarter + quarter_offset
    
    # Handle year rollover
    while target_quarter > 4:
      target_quarter -= 4
      year += 1
    while target_quarter < 1:
      target_quarter += 4
      year -= 1
    
    # Get quarter date range
    quarter_ranges = {
      1: (1, 3, 31),   # Q1: Jan-Mar
      2: (4, 6, 30),   # Q2: Apr-Jun  
      3: (7, 9, 30),   # Q3: Jul-Sep
      4: (10, 12, 31)  # Q4: Oct-Dec
    }
    
    start_month, end_month, end_day = quarter_ranges[target_quarter]
    start_date = datetime(year, start_month, 1)
    end_date = datetime(year, end_month, end_day)
    
    return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

  @staticmethod
  def get_next_quarter_range() -> str:
    """Get next quarter date range"""
    return VietnamDateUtils.get_quarter_range(1)

  @staticmethod
  def get_current_quarter_range() -> str:
    """Get current quarter date range"""
    return VietnamDateUtils.get_quarter_range(0)

  @staticmethod
  def get_previous_quarter_range() -> str:
    """Get previous quarter date range"""
    return VietnamDateUtils.get_quarter_range(-1)

  @staticmethod
  def parse_quarter_from_text(text: str) -> str:
    text = text.lower()
    
    # Handle specific quarter and year patterns
    q_pattern = r'q([1-4])\s*(\d{4})?'
    quarter_pattern = r'quý\s*([1-4])\s*(?:năm\s*)?(\d{4})?'
    
    q_match = re.search(q_pattern, text)
    quarter_match = re.search(quarter_pattern, text)
    
    if q_match:
      quarter_num = int(q_match.group(1))
      year = int(q_match.group(2)) if q_match.group(2) else None
      current_quarter = (VietnamDateUtils.get_vietnam_date().month - 1) // 3 + 1
      offset = quarter_num - current_quarter
      return VietnamDateUtils.get_quarter_range(offset, year)
    
    if quarter_match:
      quarter_num = int(quarter_match.group(1))
      year = int(quarter_match.group(2)) if quarter_match.group(2) else None
      current_quarter = (VietnamDateUtils.get_vietnam_date().month - 1) // 3 + 1
      offset = quarter_num - current_quarter
      return VietnamDateUtils.get_quarter_range(offset, year)
    
    # Handle relative quarter terms
    if any(term in text for term in ['quý tới', 'quý sau', 'next quarter']):
      return VietnamDateUtils.get_next_quarter_range()
    elif any(term in text for term in ['quý này', 'current quarter', 'this quarter']):
      return VietnamDateUtils.get_current_quarter_range()
    elif any(term in text for term in ['quý trước', 'quý trước đó', 'previous quarter', 'last quarter']):
      return VietnamDateUtils.get_previous_quarter_range()
    
    # Default to next quarter
    return VietnamDateUtils.get_next_quarter_range()

  @staticmethod
  def get_current_time_string() -> str:
    """Get current time string for logging"""
    return VietnamDateUtils.get_vietnam_date().strftime('%Y-%m-%d %H:%M:%S')