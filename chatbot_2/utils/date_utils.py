from datetime import datetime, timedelta

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
  def get_current_time_string() -> str:
    """Get current time string for logging"""
    return VietnamDateUtils.get_vietnam_date().strftime('%Y-%m-%d %H:%M:%S')