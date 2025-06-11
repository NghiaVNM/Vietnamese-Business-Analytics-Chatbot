import json
import re
from datetime import datetime
import calendar
import requests

# Load schemas from JSON file
def load_function_schemas():
    """Load function schemas from JSON file"""
    try:
        with open('/home/mike/workspace/vcycber/langchain/function_calling_schemas.json', 'r', encoding='utf-8') as f:
            schemas = json.load(f)
        print(f"✅ Loaded {len(schemas)} function schemas from JSON file")
        return schemas
    except Exception as e:
        print(f"❌ Error loading schemas: {e}")
        return []

# Load schemas at startup
FUNCTION_SCHEMAS = load_function_schemas()
SCHEMA_COUNT = len(FUNCTION_SCHEMAS)

def get_schema_by_name(function_name):
    """Get schema by function name"""
    for i, schema in enumerate(FUNCTION_SCHEMAS):
        if schema["name"] == function_name:
            return i + 1, schema  # Return 1-based index and schema
    return None, None

def validate_function_call(function_name, parameters):
    """Validate if function call matches any allowed schema"""
    schema_id, schema = get_schema_by_name(function_name)
    
    if not schema:
        return False, f"Function '{function_name}' not found in allowed schemas"
    
    return True, f"Function '{function_name}' is valid (Schema ID: {schema_id})"

def get_all_function_names():
    """Get list of all allowed function names"""
    return [schema["name"] for schema in FUNCTION_SCHEMAS]

# Import SegmentMapper with fallback
try:
    from segment_mapping import SegmentMapper
    SEGMENT_MAPPER_AVAILABLE = True
    print("✅ SegmentMapper imported successfully")
except ImportError:
    print("⚠️ SegmentMapper not available. Creating fallback...")
    SEGMENT_MAPPER_AVAILABLE = False
    
    # Create a simple fallback SegmentMapper
    class SegmentMapper:
        def __init__(self):
            print("⚠️ Using fallback SegmentMapper")
        
        def get_segment(self, query):
            query_lower = query.lower()
            if any(word in query_lower for word in ['cao cấp', 'premium', 'vip']):
                return 'premium'
            elif any(word in query_lower for word in ['doanh nghiệp', 'enterprise']):
                return 'enterprise'
            elif any(word in query_lower for word in ['khách hàng mới', 'new customer']):
                return 'new_customer'
            return 'all'
        
        def detect_new_customer_intent(self, query):
            query_lower = query.lower()
            return any(word in query_lower for word in ['khách hàng mới', 'new customer', 'khách mới'])

# Translation libraries - import with fallback handling
TRANSLATION_AVAILABLE = False
try:
    from googletrans import Translator
    GOOGLE_TRANSLATOR = Translator()
    TRANSLATION_AVAILABLE = True
    print("✅ Google Translate available")
except ImportError:
    print("⚠️ Google Translate not available. Install with: pip install googletrans==4.0.0-rc1")
    GOOGLE_TRANSLATOR = None

# Alternative translation libraries
DEEP_TRANSLATOR_AVAILABLE = False
try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR = GoogleTranslator(source='vi', target='en')
    DEEP_TRANSLATOR_AVAILABLE = True
    print("✅ Deep Translator available")
except ImportError:
    print("⚠️ Deep Translator not available. Install with: pip install deep-translator")
    DEEP_TRANSLATOR = None

# Microsoft Translator
AZURE_TRANSLATOR_AVAILABLE = False
try:
    import uuid
    # You would need to set up Azure Cognitive Services keys
    AZURE_KEY = None  # Set your Azure key here
    AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
    AZURE_LOCATION = "global"
    if AZURE_KEY:
        AZURE_TRANSLATOR_AVAILABLE = True
        print("✅ Azure Translator available")
except ImportError:
    print("⚠️ Azure Translator not available")

# Định nghĩa bảng metrics (giống như database tables)
METRICS_TABLE = {
    # Business Metrics
    "revenue": {
        "name": "revenue",
        "table": "sales_revenue", 
        "description": "Doanh thu, revenue, sales revenue",
        "keywords": ["doanh thu", "revenue", "sales", "bán hàng", "thu nhập"],
        "unit": "VND"
    },
    "orders": {
        "name": "orders",
        "table": "order_summary",
        "description": "Số đơn hàng, orders, order count",
        "keywords": ["đơn hàng", "orders", "order", "số đơn", "đặt hàng"],
        "unit": "count"
    },
    "profit": {
        "name": "profit",
        "table": "profit_analysis",
        "description": "Lợi nhuận, profit, net income",
        "keywords": ["lợi nhuận", "profit", "net income", "thu nhập ròng"],
        "unit": "VND"
    },
    "visits": {
        "name": "visits",
        "table": "website_analytics",
        "description": "Lượt truy cập website, website visits, traffic",
        "keywords": ["truy cập", "visits", "traffic", "website", "lượt xem", "pageview"],
        "unit": "count"
    },
    "users": {
        "name": "users",
        "table": "user_analytics",
        "description": "Người dùng, users, active users",
        "keywords": ["người dùng", "users", "user", "khách hàng", "customer"],
        "unit": "count"
    },
    "conversion": {
        "name": "conversion",
        "table": "conversion_metrics",
        "description": "Tỷ lệ chuyển đổi, conversion rate",
        "keywords": ["chuyển đổi", "conversion", "tỷ lệ", "rate"],
        "unit": "percentage"
    },
    "transactions": {
        "name": "transactions",
        "table": "transaction_log",
        "description": "Giao dịch, transactions",
        "keywords": ["giao dịch", "transaction", "thanh toán", "payment"],
        "unit": "count"
    }
}

def get_metric_from_question(question):
    """Detect metric from question using the metrics table"""
    question_lower = question.lower()
    
    # Score each metric based on keyword matches
    metric_scores = {}
    
    for metric_name, metric_info in METRICS_TABLE.items():
        score = 0
        keywords = metric_info["keywords"]
        
        for keyword in keywords:
            if keyword in question_lower:
                # Longer keywords get higher scores
                score += len(keyword.split())
        
        if score > 0:
            metric_scores[metric_name] = score
    
    # Return the metric with highest score
    if metric_scores:
        best_metric = max(metric_scores, key=metric_scores.get)
        print(f"📊 Detected metric: {best_metric} (score: {metric_scores[best_metric]})")
        print(f"📋 Table: {METRICS_TABLE[best_metric]['table']}")
        return best_metric
    
    # Default fallback
    print("📊 No specific metric detected, defaulting to 'revenue'")
    return "revenue"

# Định nghĩa các hàm cần sử dụng
def get_total_revenue(start_date, end_date):
    return {"result": 1000000, "unit": "VND", "period": f"{start_date} to {end_date}"}

def get_total_orders(start_date, end_date):
    return {"result": 150, "unit": "orders", "period": f"{start_date} to {end_date}"}

def get_new_customer_revenue(segment, start_date, end_date):
    return {"result": 500000, "segment": segment, "period": f"{start_date} to {end_date}"}

def get_customer_segment_report(segment, start_date, end_date):
    return {"segment": segment, "revenue": 800000, "orders": 120, "period": f"{start_date} to {end_date}"}

def get_sales_report(start_date, end_date):
    return {"total_sales": 2000000, "period": f"{start_date} to {end_date}"}

def get_roi(campaign_id):
    return {"campaign_id": campaign_id, "roi": "25%", "investment": 100000, "return": 125000}

# Define available tools
tools = {
    "get_total_revenue": get_total_revenue,
    "get_total_orders": get_total_orders,
    "get_new_customer_revenue": get_new_customer_revenue,
    "get_customer_segment_report": get_customer_segment_report,
    "get_sales_report": get_sales_report,
    "get_roi": get_roi,
}

class BusinessAnalyticsChatbot:
    def __init__(self):
        """Initialize the chatbot with segment mapper"""
        try:
            self.segment_mapper = SegmentMapper()
            self.tools = tools
            print("🤖 BusinessAnalyticsChatbot initialized")
        except Exception as e:
            print(f"⚠️ Error initializing SegmentMapper: {e}")
            print("🤖 BusinessAnalyticsChatbot initialized with limited functionality")
            self.segment_mapper = None
            self.tools = tools

    def translate_query(self, query):
        """Translate Vietnamese query to English"""
        if not query.strip():
            return None
            
        # Try Google Translate first
        if TRANSLATION_AVAILABLE and GOOGLE_TRANSLATOR:
            try:
                result = GOOGLE_TRANSLATOR.translate(query, src='vi', dest='en')
                if result and result.text:
                    return result.text.lower().strip()
            except Exception as e:
                print(f"Translation error: {e}")
        
        # Fallback to manual translation
        return self._manual_translate(query)

    def _manual_translate(self, query):
        """Manual translation using dictionary"""
        translation_dict = {
            "doanh thu": "revenue",
            "khách hàng mới": "new customer",
            "phân khúc": "segment",
            "báo cáo": "report",
            "năm": "year",
            "tháng": "month",
            "quý": "quarter"
        }
        
        translated = query.lower()
        for vi, en in translation_dict.items():
            translated = translated.replace(vi, en)
        
        return translated

    def _extract_date_range(self, query_lower, year):
        """Extract more precise date ranges from query"""
        import calendar
        
        # Check for "theo tuần" (by week) pattern first
        if any(keyword in query_lower for keyword in ['theo tuần', 'từng tuần', 'mỗi tuần', 'weekly']):
            print("📅 Detected weekly analysis request")
            # For weekly analysis, we still need the full period to analyze
            # The actual weekly breakdown will be handled by the function
        
        # Check for comparison queries with two date ranges first
        if any(keyword in query_lower for keyword in ['so sánh', 'compare']) and 'và' in query_lower:
            # Enhanced patterns for two date ranges in comparison
            comparison_patterns = [
                # Pattern: 15/08/2021 - 01/06/2022 và 15/08/2023 - 01/06/2024
                r'(\d{1,2})/(\d{1,2})/(\d{4})\s*-\s*(\d{1,2})/(\d{1,2})/(\d{4})\s+và\s+(\d{1,2})/(\d{1,2})/(\d{4})\s*-\s*(\d{1,2})/(\d{1,2})/(\d{4})',
                # Pattern: từ 15/08/2021 đến 01/06/2022 và từ 15/08/2023 đến 01/06/2024
                r'từ\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+đến\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+và\s+từ\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+đến\s+(\d{1,2})/(\d{1,2})/(\d{4})',
                # Pattern: 15/08/2021-01/06/2022 và 15/08/2023-01/06/2024
                r'(\d{1,2})/(\d{1,2})/(\d{4})-(\d{1,2})/(\d{1,2})/(\d{4})\s+và\s+(\d{1,2})/(\d{1,2})/(\d{4})-(\d{1,2})/(\d{1,2})/(\d{4})'
            ]
            
            for pattern in comparison_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    groups = match.groups()
                    if len(groups) == 12:  # Two complete date ranges
                        # First period
                        start1_day, start1_month, start1_year, end1_day, end1_month, end1_year = groups[:6]
                        # Second period  
                        start2_day, start2_month, start2_year, end2_day, end2_month, end2_year = groups[6:]
                        
                        period1_start = f"{start1_year}-{int(start1_month):02d}-{int(start1_day):02d}"
                        period1_end = f"{end1_year}-{int(end1_month):02d}-{int(end1_day):02d}"
                        period2_start = f"{start2_year}-{int(start2_month):02d}-{int(start2_day):02d}"
                        period2_end = f"{end2_year}-{int(end2_month):02d}-{int(end2_day):02d}"
                        
                        print(f"📅 Extracted comparison date ranges:")
                        print(f"   Period 1: {period1_start} to {period1_end}")
                        print(f"   Period 2: {period2_start} to {period2_end}")
                        
                        # Return a special indicator for comparison queries
                        return f"COMPARISON:{period1_start}|{period1_end}|{period2_start}|{period2_end}", None
        
        # Check for specific date patterns first
        date_patterns = [
            r'từ\s+ngày\s+(\d{1,2})/(\d{1,2})\s+đến\s+(\d{1,2})/(\d{1,2})\s+năm\s+(\d{4})',  # từ ngày 1/1 đến 31/3 năm 2023
            r'từ\s+(\d{1,2})/(\d{1,2})/(\d{4})\s+đến\s+(\d{1,2})/(\d{1,2})/(\d{4})',  # từ 1/1/2023 đến 31/3/2023
            r'(\d{1,2})/(\d{1,2})/(\d{4})\s*-\s*(\d{1,2})/(\d{1,2})/(\d{4})',  # 1/1/2023 - 31/3/2023
            r'từ\s+(\d{1,2})/(\d{1,2})\s+đến\s+(\d{1,2})/(\d{1,2})/(\d{4})',  # từ 1/1 đến 31/3/2023
            r'trong\s+khoảng\s+từ\s+(\d{1,2})/(\d{1,2})\s+đến\s+(\d{1,2})/(\d{1,2})/(\d{4})',  # trong khoảng từ 1/1 đến 31/3/2023
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, query_lower)
            if match:
                groups = match.groups()
                if len(groups) == 5 and groups[4]:  # Pattern 1: từ ngày D/M đến D/M năm YYYY
                    start_day, start_month, end_day, end_month, year_str = groups
                    start_date = f"{year_str}-{int(start_month):02d}-{int(start_day):02d}"
                    end_date = f"{year_str}-{int(end_month):02d}-{int(end_day):02d}"
                elif len(groups) == 6:  # Pattern 2 & 3: full dates
                    start_day, start_month, start_year, end_day, end_month, end_year = groups
                    start_date = f"{start_year}-{int(start_month):02d}-{int(start_day):02d}"
                    end_date = f"{end_year}-{int(end_month):02d}-{int(end_day):02d}"
                elif len(groups) == 5 and not groups[4]:  # Pattern 4 & 5: từ D/M đến D/M/YYYY
                    start_day, start_month, end_day, end_month, end_year = groups
                    start_date = f"{end_year}-{int(start_month):02d}-{int(start_day):02d}"
                    end_date = f"{end_year}-{int(end_month):02d}-{int(end_day):02d}"
                
                print(f"📅 Extracted specific date range: {start_date} to {end_date}")
                return start_date, end_date
        
        # Then check for enhanced week patterns with more variations
        week_patterns = [
            ('tuần đầu', 'tuần 1', 'tuần một', 'week 1', 'first week'),
            ('tuần thứ hai', 'tuần thứ 2', 'tuần 2', 'tuần hai', 'week 2', 'second week'),
            ('tuần thứ ba', 'tuần thứ 3', 'tuần 3', 'tuần ba', 'week 3', 'third week'),
            ('tuần cuối', 'tuần 4', 'tuần tư', 'week 4', 'last week')
        ]
        
        # First, check for specific week patterns across the entire query
        for week_idx, week_keywords in enumerate(week_patterns):
            if any(keyword in query_lower for keyword in week_keywords):
                print(f"🔍 Found week pattern: {[k for k in week_keywords if k in query_lower]}")
                
                # Now find which month this week belongs to
                for month_text, month_num in {
                    'tháng 1': 1, 'tháng một': 1, 'january': 1, 'jan': 1,
                    'tháng 2': 2, 'tháng hai': 2, 'february': 2, 'feb': 2,
                    'tháng 3': 3, 'tháng ba': 3, 'march': 3, 'mar': 3,
                    'tháng 4': 4, 'tháng tư': 4, 'april': 4, 'apr': 4,
                    'tháng 5': 5, 'tháng năm': 5, 'may': 5,
                    'tháng 6': 6, 'tháng sáu': 6, 'june': 6, 'jun': 6,
                    'tháng 7': 7, 'tháng bảy': 7, 'july': 7, 'jul': 7,
                    'tháng 8': 8, 'tháng tám': 8, 'august': 8, 'aug': 8,
                    'tháng 9': 9, 'tháng chín': 9, 'september': 9, 'sep': 9,
                    'tháng 10': 10, 'tháng mười': 10, 'october': 10, 'oct': 10,
                    'tháng 11': 11, 'tháng mười một': 11, 'november': 11, 'nov': 11,
                    'tháng 12': 12, 'tháng mười hai': 12, 'december': 12, 'dec': 12
                }.items():
                    if month_text in query_lower:
                        # Calculate specific week dates
                        if week_idx == 0:  # First week
                            start_date = f"{year:04d}-{month_num:02d}-01"
                            end_date = f"{year:04d}-{month_num:02d}-07"
                        elif week_idx == 1:  # Second week
                            start_date = f"{year:04d}-{month_num:02d}-08"
                            end_date = f"{year:04d}-{month_num:02d}-14"
                        elif week_idx == 2:  # Third week
                            start_date = f"{year:04d}-{month_num:02d}-15"
                            end_date = f"{year:04d}-{month_num:02d}-21"
                        else:  # Last week
                            last_day = calendar.monthrange(year, month_num)[1]
                            start_date = f"{year:04d}-{month_num:02d}-22"
                            end_date = f"{year:04d}-{month_num:02d}-{last_day:02d}"
                        
                        print(f"📅 Detected week {week_idx + 1} of month {month_num}: {start_date} to {end_date}")
                        return start_date, end_date
        
        # Then check for month + week combinations (fallback)
        for month_text, month_num in {
            'tháng 1': 1, 'tháng một': 1, 'january': 1, 'jan': 1,
            'tháng 2': 2, 'tháng hai': 2, 'february': 2, 'feb': 2,
            'tháng 3': 3, 'tháng ba': 3, 'march': 3, 'mar': 3,
            'tháng 4': 4, 'tháng tư': 4, 'april': 4, 'apr': 4,
            'tháng 5': 5, 'tháng năm': 5, 'may': 5,
            'tháng 6': 6, 'tháng sáu': 6, 'june': 6, 'jun': 6,
            'tháng 7': 7, 'tháng bảy': 7, 'july': 7, 'jul': 7,
            'tháng 8': 8, 'tháng tám': 8, 'august': 8, 'aug': 8,
            'tháng 9': 9, 'tháng chín': 9, 'september': 9, 'sep': 9,
            'tháng 10': 10, 'tháng mười': 10, 'october': 10, 'oct': 10,
            'tháng 11': 11, 'tháng mười một': 11, 'november': 11, 'nov': 11,
            'tháng 12': 12, 'tháng mười hai': 12, 'december': 12, 'dec': 12
        }.items():
            if month_text in query_lower:
                # Check for "theo tuần" with month
                if any(keyword in query_lower for keyword in ['theo tuần', 'từng tuần', 'mỗi tuần', 'weekly']):
                    # Return full month for weekly breakdown
                    last_day = calendar.monthrange(year, month_num)[1]
                    start_date = f"{year:04d}-{month_num:02d}-01"
                    end_date = f"{year:04d}-{month_num:02d}-{last_day:02d}"
                    print(f"📅 Weekly analysis for month {month_num}: {start_date} to {end_date}")
                    return start_date, end_date
                
                # No specific week, return full month
                last_day = calendar.monthrange(year, month_num)[1]
                start_date = f"{year:04d}-{month_num:02d}-01"
                end_date = f"{year:04d}-{month_num:02d}-{last_day:02d}"
                print(f"📅 Full month {month_num}: {start_date} to {end_date}")
                return start_date, end_date
        
        # Check for quarters
        quarter_patterns = {
            'quý 1': (1, 3), 'quý một': (1, 3), 'q1': (1, 3),
            'quý 2': (4, 6), 'quý hai': (4, 6), 'q2': (4, 6),
            'quý 3': (7, 9), 'quý ba': (7, 9), 'q3': (7, 9),
            'quý 4': (10, 12), 'quý tư': (10, 12), 'q4': (10, 12)
        }
        
        for quarter_text, (start_month, end_month) in quarter_patterns.items():
            if quarter_text in query_lower:
                start_date = f"{year:04d}-{start_month:02d}-01"
                last_day = calendar.monthrange(year, end_month)[1]
                end_date = f"{year:04d}-{end_month:02d}-{last_day:02d}"
                return start_date, end_date
        
        # Default to full year
        start_date = f"{year:04d}-01-01"
        end_date = f"{year:04d}-12-31"
        return start_date, end_date

    def analyze_query_with_pattern_matching(self, query):
        """Phân tích câu hỏi bằng pattern matching - adapted for new schemas"""
        query_lower = query.lower()
        
        # Detect year - but ignore order IDs and other non-year patterns
        # Fixed regex: avoid variable-width lookbehind
        year_candidates = re.findall(r'\b(\d{4})\b', query_lower)
        year = 2024  # default
        
        for candidate in year_candidates:
            candidate_int = int(candidate)
            # Only accept realistic years and avoid order IDs
            if 1900 <= candidate_int <= 2100:
                # Check if this number is part of an order ID
                order_pattern = r'(?:ord|order|đơn)\s*\w*' + candidate
                if not re.search(order_pattern, query_lower):
                    year = candidate_int
                    break
        
        # Detect month and quarter for more precise date ranges
        start_date, end_date = self._extract_date_range(query_lower, year)
        
        # Detect segment first
        segment = self._detect_segment_from_query(query_lower)
        
        print(f"🔍 Pattern analysis: segment={segment}, dates={start_date} to {end_date}")
        
        # Extract product name if this is a product query
        product_name = "unknown"
        if any(keyword in query_lower for keyword in ['sản phẩm', 'product']):
            # Try to extract product name/ID from the query
            product_patterns = [
                r'sản phẩm\s+([a-zA-Z0-9\s]+?)(?:\s+từ|\s+trong|\s*$)',  # sản phẩm X từ
                r'product\s+([a-zA-Z0-9\s]+?)(?:\s+from|\s+in|\s*$)',    # product X from
                r'(?:sản phẩm|product)\s+([a-zA-Z0-9]+)',                # sản phẩm Z
            ]
            
            for pattern in product_patterns:
                match = re.search(pattern, query_lower)
                if match:
                    product_name = match.group(1).strip()
                    print(f"📦 Extracted product name: {product_name}")
                    break
        
        # Detect patterns for different function types
        
        # Product patterns - MOVE TO TOP PRIORITY
        if any(keyword in query_lower for keyword in ['sản phẩm', 'product']):
            # Check for best selling product queries FIRST - ENHANCED PATTERNS
            best_selling_keywords = [
                'bán chạy nhất', 'bán chạy', 'best selling', 'best-selling', 
                'phổ biến nhất', 'phổ biến', 'popular', 'top selling', 'top-selling',
                'nhiều nhất', 'cao nhất', 'hàng đầu', 'đứng đầu',
                'top', 'leading', 'hot nhất', 'hot'
            ]
            
            if any(keyword in query_lower for keyword in best_selling_keywords):
                print("🎯 Detected: Best selling product query")
                print(f"   🔍 Matched keywords: {[k for k in best_selling_keywords if k in query_lower]}")
                return {
                    "function": "get_top_selling_product",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            # Check for product revenue
            elif any(keyword in query_lower for keyword in ['doanh thu', 'revenue']):
                return {
                    "function": "get_revenue_by_product",
                    "parameters": {
                        "product_name": product_name,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            # Check for products in specific order
            elif (any(keyword in query_lower for keyword in ['liệt kê', 'danh sách', 'trong đơn']) 
                  and re.search(r'ord\d+|order[\s#]?\d+|\b\w*\d{6,}', query_lower)):
                # Extract order ID for product listing
                order_id_match = re.search(r'(ord\d+|order[\s#]?(\d+)|\b([a-z]*\d{6,}))', query_lower)
                order_id = order_id_match.group(0) if order_id_match else "unknown"
                return {
                    "function": "get_products_in_order",
                    "parameters": {
                        "order_id": order_id
                    }
                }
        
        # Customer segment report patterns (highest priority for segment queries)
        elif any(keyword in query_lower for keyword in ['phân khúc', 'segment']) and any(keyword in query_lower for keyword in ['báo cáo', 'report']):
            return {
                "function": "get_customer_segment_report",
                "parameters": {
                    "segment": segment,
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
        
        # Customer history patterns (HIGH PRIORITY - before order patterns)
        elif ((any(keyword in query_lower for keyword in ['lịch sử', 'history']) and 
               any(keyword in query_lower for keyword in ['khách hàng', 'customer', 'khách'])) or
              re.search(r'cust\d+|customer[\s#]?\d+', query_lower, re.IGNORECASE)):
            # Extract customer ID from query - improved pattern
            customer_id_match = re.search(r'(cust\d+|customer[\s#]?\d+)', query_lower, re.IGNORECASE)
            customer_id = customer_id_match.group(0) if customer_id_match else "unknown"
            return {
                "function": "get_customer_history",
                "parameters": {
                    "customer_id": customer_id
                }
            }
        
        # Revenue patterns - ENHANCED BRANCH DETECTION
        elif any(keyword in query_lower for keyword in ['doanh thu', 'revenue']):
            # Check for quarterly reporting FIRST (highest priority)
            if any(keyword in query_lower for keyword in ['theo quý', 'từng quý', 'mỗi quý', 'quarterly', 'by quarter']):
                print("🎯 Detected: Quarterly revenue report")
                return {
                    "function": "get_total_revenue",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            # Check for branch revenue queries (existing)
            elif any(keyword in query_lower for keyword in ['chi nhánh', 'branch', 'các chi nhánh']):
                # Distinguish between comparison and report
                if any(keyword in query_lower for keyword in ['so sánh', 'compare']):
                    print("🎯 Detected: Branch revenue comparison")
                    return {
                        "function": "compare_revenue_by_branch",
                        "parameters": {
                            "start_date": start_date,
                            "end_date": end_date
                        }
                    }
                else:
                    print("🎯 Detected: Branch revenue report")
                    return {
                        "function": "get_total_revenue_by_branch",
                        "parameters": {
                            "start_date": start_date,
                            "end_date": end_date
                        }
                    }
            # Check for segment-specific revenue
            elif segment != 'all' and any(keyword in query_lower for keyword in ['phân khúc', 'segment', 'doanh nghiệp', 'enterprise', 'vip', 'cao cấp', 'khách hàng']):
                return {
                    "function": "get_customer_segment_report",
                    "parameters": {
                        "segment": segment,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            elif any(keyword in query_lower for keyword in ['so sánh', 'compare']):
                # Check if we have extracted comparison date ranges
                comparison_dates = self._extract_date_range(query_lower, year)
                if isinstance(comparison_dates, tuple) and comparison_dates[0] and comparison_dates[0].startswith("COMPARISON:"):
                    print("🎯 Detected: Custom date range comparison")
                    
                    # Parse the comparison dates
                    date_parts = comparison_dates[0].replace("COMPARISON:", "").split("|")
                    if len(date_parts) == 4:
                        period1_start, period1_end, period2_start, period2_end = date_parts
                        return {
                            "function": "compare_revenue",
                            "parameters": {
                                "period1_start": period1_start,
                                "period1_end": period1_end,
                                "period2_start": period2_start,
                                "period2_end": period2_end
                            }
                        }
                
                # Enhanced comparison detection for month-to-month periods
                month_comparison_pattern = r'tháng\s+(\d{1,2})\s+và\s+tháng\s+(\d{1,2})'
                if re.search(month_comparison_pattern, query_lower):
                    print("🎯 Detected: Month-to-month revenue comparison")
                    
                    month_match = re.search(month_comparison_pattern, query_lower)
                    if month_match:
                        month1, month2 = month_match.groups()
                        month1, month2 = int(month1), int(month2)
                        
                        # Extract year for month comparison
                        year_match = re.search(r'năm\s+(\d{4})', query_lower)
                        comp_year = int(year_match.group(1)) if year_match else year
                        
                        # Calculate month ranges
                        import calendar
                        month1_last_day = calendar.monthrange(comp_year, month1)[1]
                        month2_last_day = calendar.monthrange(comp_year, month2)[1]
                        
                        return {
                            "function": "compare_revenue",
                            "parameters": {
                                "period1_start": f"{comp_year}-{month1:02d}-01",
                                "period1_end": f"{comp_year}-{month1:02d}-{month1_last_day:02d}",
                                "period2_start": f"{comp_year}-{month2:02d}-01",
                                "period2_end": f"{comp_year}-{month2:02d}-{month2_last_day:02d}"
                            }
                        }
                
                # Enhanced comparison detection for half-year periods
                elif any(keyword in query_lower for keyword in ['nửa đầu', 'nửa cuối', 'first half', 'second half', '6 tháng đầu', '6 tháng cuối']):
                    print("🎯 Detected: Half-year revenue comparison")
                    
                    # Extract year for half-year comparison
                    year_match = re.search(r'năm\s+(\d{4})', query_lower)
                    comp_year = int(year_match.group(1)) if year_match else year
                    
                    return {
                        "function": "compare_revenue",
                        "parameters": {
                            "period1_start": f"{comp_year}-01-01",  # First half
                            "period1_end": f"{comp_year}-06-30",
                            "period2_start": f"{comp_year}-07-01",  # Second half
                            "period2_end": f"{comp_year}-12-31"
                        }
                    }
                # Enhanced comparison detection for quarterly periods
                elif any(keyword in query_lower for keyword in ['quý 1', 'quý 2', 'quý 3', 'quý 4', 'q1', 'q2', 'q3', 'q4']):
                    print("🎯 Detected: Quarterly revenue comparison")
                    
                    # Extract specific quarters mentioned
                    quarters_mentioned = []
                    quarter_mapping = {
                        'quý 1': 1, 'q1': 1, 'quý một': 1,
                        'quý 2': 2, 'q2': 2, 'quý hai': 2,
                        'quý 3': 3, 'q3': 3, 'quý ba': 3,
                        'quý 4': 4, 'q4': 4, 'quý tư': 4
                    }
                    
                    for quarter_text, quarter_num in quarter_mapping.items():
                        if quarter_text in query_lower:
                            quarters_mentioned.append(quarter_num)
                    
                    # If exactly 2 quarters mentioned, compare them
                    if len(quarters_mentioned) == 2:
                        q1, q2 = sorted(quarters_mentioned)
                        
                        # Calculate quarter date ranges
                        q1_start_month = (q1 - 1) * 3 + 1
                        q1_end_month = q1 * 3
                        q2_start_month = (q2 - 1) * 3 + 1
                        q2_end_month = q2 * 3
                        
                        import calendar
                        q1_end_day = calendar.monthrange(year, q1_end_month)[1]
                        q2_end_day = calendar.monthrange(year, q2_end_month)[1]
                        
                        return {
                            "function": "compare_revenue",
                            "parameters": {
                                "period1_start": f"{year}-{q1_start_month:02d}-01",
                                "period1_end": f"{year}-{q1_end_month:02d}-{q1_end_day:02d}",
                                "period2_start": f"{year}-{q2_start_month:02d}-01",
                                "period2_end": f"{year}-{q2_end_month:02d}-{q2_end_day:02d}"
                            }
                        }
                    else:
                        # Default quarterly comparison (Q1 vs Q2 if no specific quarters)
                        return {
                            "function": "compare_revenue",
                            "parameters": {
                                "period1_start": f"{year}-01-01",  # Q1
                                "period1_end": f"{year}-03-31",
                                "period2_start": f"{year}-04-01",  # Q2
                                "period2_end": f"{year}-06-30"
                            }
                        }
                # Enhanced comparison detection for yearly periods
                elif re.search(r'năm\s+(\d{4})\s+và\s+năm\s+(\d{4})', query_lower):
                    print("🎯 Detected: Year-to-year revenue comparison")
                    year_match = re.search(r'năm\s+(\d{4})\s+và\s+năm\s+(\d{4})', query_lower)
                    if year_match:
                        year1, year2 = year_match.groups()
                        return {
                            "function": "compare_revenue",
                            "parameters": {
                                "period1_start": f"{year1}-01-01",
                                "period1_end": f"{year1}-12-31",
                                "period2_start": f"{year2}-01-01",
                                "period2_end": f"{year2}-12-31"
                            }
                        }
                # Default comparison (current period vs previous year)
                else:
                    return {
                        "function": "compare_revenue",
                        "parameters": {
                            "period1_start": start_date,
                            "period1_end": end_date,
                            "period2_start": "2022-01-01",  # Previous year as default
                            "period2_end": "2022-12-31"
                        }
                    }
            # Default revenue query
            else:
                print("🎯 Detected: General revenue query")
                return {
                    "function": "get_total_revenue",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
        
        # Profit patterns - NEW: Handle profit queries
        elif any(keyword in query_lower for keyword in ['lợi nhuận', 'profit', 'thu nhập ròng', 'net income']):
            print("🎯 Detected: Profit query")
            
            # Check for monthly/quarterly breakdowns
            if any(keyword in query_lower for keyword in ['theo tháng', 'từng tháng', 'mỗi tháng', 'monthly', 'trung bình theo tháng', 'hàng tháng']):
                print("   📊 Monthly profit analysis detected")
                return {
                    "function": "get_avg_profit_by_month",  # Use specific monthly profit function
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            elif any(keyword in query_lower for keyword in ['theo quý', 'từng quý', 'mỗi quý', 'quarterly', 'trung bình theo quý']):
                print("   📊 Quarterly profit analysis detected")
                return {
                    "function": "get_avg_profit_by_quarter",  # Use specific quarterly profit function
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            elif any(keyword in query_lower for keyword in ['so sánh', 'compare']):
                print("   📊 Profit comparison detected")
                
                # Check for month-to-month comparison
                month_comparison_pattern = r'tháng\s+(\d{1,2})\s+và\s+tháng\s+(\d{1,2})'
                if re.search(month_comparison_pattern, query_lower):
                    month_match = re.search(month_comparison_pattern, query_lower)
                    if month_match:
                        month1, month2 = month_match.groups()
                        month1, month2 = int(month1), int(month2)
                        
                        year_match = re.search(r'năm\s+(\d{4})', query_lower)
                        comp_year = int(year_match.group(1)) if year_match else year
                        
                        import calendar
                        month1_last_day = calendar.monthrange(comp_year, month1)[1]
                        month2_last_day = calendar.monthrange(comp_year, month2)[1]
                        
                        return {
                            "function": "compare_profit",  # Use profit comparison function
                            "parameters": {
                                "period1_start": f"{comp_year}-{month1:02d}-01",
                                "period1_end": f"{comp_year}-{month1:02d}-{month1_last_day:02d}",
                                "period2_start": f"{comp_year}-{month2:02d}-01",
                                "period2_end": f"{comp_year}-{month2:02d}-{month2_last_day:02d}"
                            }
                        }
                
                # Default profit comparison
                return {
                    "function": "compare_profit",  # Use profit comparison function
                    "parameters": {
                        "period1_start": start_date,
                        "period1_end": end_date,
                        "period2_start": "2020-01-01",  # Previous year as default
                        "period2_end": "2020-12-31"
                    }
                }
            else:
                # General profit query
                print("   📊 General profit query")
                return {
                    "function": "get_total_profit",  # Use total profit function
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
        
        # Order patterns
        elif any(keyword in query_lower for keyword in ['đơn hàng', 'order']):
            if any(keyword in query_lower for keyword in ['vip']):
                return {
                    "function": "get_vip_orders",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            elif any(keyword in query_lower for keyword in ['trên', 'lớn hơn', 'cao hơn', 'greater than', 'above', 'over']) and any(keyword in query_lower for keyword in ['triệu', 'million', 'đồng', 'vnd']):
                # High value orders pattern
                # Extract value if possible
                value_pattern = r'(\d+)\s*(?:triệu|million)'
                value_match = re.search(value_pattern, query_lower)
                min_value = float(value_match.group(1)) * 1000000 if value_match else 1000000  # Convert to VND
                return {
                    "function": "get_orders_above_value",
                    "parameters": {
                        "min_value": min_value,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            elif (any(keyword in query_lower for keyword in ['giá trị cao nhất', 'highest value', 'cao nhất', 'lớn nhất', 'maximum', 'max']) or
                  (any(keyword in query_lower for keyword in ['cao nhất', 'lớn nhất', 'highest', 'maximum', 'max']) and 
                   any(keyword in query_lower for keyword in ['giá trị', 'value', 'tiền', 'amount']))):
                print("🎯 Detected: Highest value order query")
                return {
                    "function": "get_top_order",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            elif (any(keyword in query_lower for keyword in ['sản phẩm', 'product', 'liệt kê', 'danh sách']) 
                  and re.search(r'ord\d+|order[\s#]?\d+|\b\w*\d{6,}', query_lower)):
                # Extract order ID for product listing
                order_id_match = re.search(r'(ord\d+|order[\s#]?(\d+)|\b([a-z]*\d{6,}))', query_lower)
                order_id = order_id_match.group(0) if order_id_match else "unknown"
                return {
                    "function": "get_products_in_order",
                    "parameters": {
                        "order_id": order_id
                    }
                }
            elif any(keyword in query_lower for keyword in ['chi tiết', 'detail', 'thông tin']) and re.search(r'ord\d+|order[\s#]?\d+|\b\w*\d{6,}', query_lower):
                # Extract order ID for order details
                order_id_match = re.search(r'(ord\d+|order[\s#]?(\d+)|\b([a-z]*\d{6,}))', query_lower)
                order_id = order_id_match.group(0) if order_id_match else "unknown"
                return {
                    "function": "get_order_detail",
                    "parameters": {
                        "order_id": order_id
                    }
                }
            elif any(keyword in query_lower for keyword in ['hoàn thành', 'completion']):
                return {
                    "function": "get_order_completion_rate",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            else:
                return {
                    "function": "get_total_orders",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
        
        # Customer patterns (remaining customer queries)
        elif any(keyword in query_lower for keyword in ['khách hàng', 'customer', 'khách']):
            if any(keyword in query_lower for keyword in ['mới', 'new']):
                return {
                    "function": "get_new_customer_count",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            elif any(keyword in query_lower for keyword in ['phân khúc', 'segment']):
                return {
                    "function": "get_customer_segment_report",
                    "parameters": {
                        "segment": segment,
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
        
        # ROI pattern
        elif any(keyword in query_lower for keyword in ['roi', 'return on investment']):
            # Try to extract campaign ID from query
            campaign_id = self._extract_campaign_id(query_lower)
            return {
                "function": "get_roi",
                "parameters": {
                    "campaign_id": campaign_id
                }
            }
        
        # Traffic pattern
        elif any(keyword in query_lower for keyword in ['traffic', 'truy cập', 'website']):
            return {
                "function": "get_traffic_stats",
                "parameters": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
        
        # Comprehensive report pattern - NEW: map to available functions
        elif any(keyword in query_lower for keyword in ['báo cáo tổng hợp', 'tổng hợp', 'comprehensive report']):
            print("🎯 Detected: Comprehensive report query")
            # For comprehensive reports, use total revenue as primary metric
            # since it's the most common business summary metric
            return {
                "function": "get_total_revenue",
                "parameters": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
        
        # Generic report pattern - fallback for other report types  
        elif any(keyword in query_lower for keyword in ['báo cáo', 'report']) and not any(keyword in query_lower for keyword in ['phân khúc', 'segment']):
            # Check if it's a quarterly report
            if any(keyword in query_lower for keyword in ['theo quý', 'từng quý', 'mỗi quý', 'quarterly']):
                print("🎯 Detected: Quarterly report query, defaulting to revenue")
                return {
                    "function": "get_total_revenue",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            else:
                print("🎯 Detected: Generic report query, defaulting to revenue")
                return {
                    "function": "get_total_revenue",
                    "parameters": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
        
        return None

    def _detect_segment_from_query(self, query_lower):
        """Detect customer segment from query - enhanced"""
        segment_patterns = {
            'enterprise': ['doanh nghiệp', 'enterprise', 'công ty', 'tổ chức', 'corporate', 'business'],
            'vip': ['vip', 'cao cấp', 'premium', 'thượng hạng', 'luxury'],
            'regular': ['thường', 'regular', 'standard', 'bình thường'],
            'new': ['mới', 'new', 'khách hàng mới', 'khách mới'],
            'returning': ['cũ', 'returning', 'quay lại', 'trung thành', 'thân thiết'],
            'casual': ['vãng lai', 'occasional', 'thỉnh thoảng', 'không thường xuyên', 'bình thường']
        }
        
        # Score each segment
        segment_scores = {}
        for segment_name, keywords in segment_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    # Give exact matches higher scores
                    if keyword == query_lower.strip():
                        score += len(keyword.split()) * 2
                    else:
                        score += len(keyword.split())
            if score > 0:
                segment_scores[segment_name] = score
        
        # Return segment with highest score
        if segment_scores:
            best_segment = max(segment_scores, key=segment_scores.get)
            print(f"🎯 Detected segment: {best_segment} (score: {segment_scores[best_segment]})")
            
            # Debug: show all detected segments
            if len(segment_scores) > 1:
                print(f"🔍 All segments found: {segment_scores}")
            
            return best_segment
        
        print("🔍 No specific segment detected, using 'all'")
        return 'all'

    def call_llm(self, prompt):
        """Call LLM for function detection - enhanced"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2:7b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Slightly higher for better creativity
                        "top_p": 0.9,
                        "num_predict": 300,  # More tokens for better responses
                        "stop": ["\n\n", "User:", "Question:"]  # Stop tokens
                    }
                },
                timeout=45  # Longer timeout
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "")
                if result.strip():
                    return self._parse_llm_response(result)
                else:
                    print("❌ Empty LLM response")
                    return None
            else:
                print(f"❌ LLM API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ LLM request timeout")
            return None
        except Exception as e:
            print(f"❌ Error calling LLM: {e}")
            return None

    def _parse_llm_response(self, response):
        """Parse LLM response to extract function and parameters - enhanced"""
        if not response:
            return None
        
        print(f"🔍 Raw LLM response: {response[:200]}...")  # Debug: show first 200 chars
        
        try:
            # Method 1: Try to find JSON block first
            json_match = re.search(r'\{[^}]*"function"[^}]*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                print(f"🔍 Found JSON: {json_str}")
                result = json.loads(json_str)
                if result.get("function"):
                    return result
            
            # Method 2: Try to find any JSON-like structure
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # Clean up common LLM formatting issues
                json_str = json_str.replace('\n', ' ').replace('  ', ' ')
                print(f"🔍 Trying to parse: {json_str}")
                try:
                    result = json.loads(json_str)
                    if result.get("function"):
                        return result
                except json.JSONDecodeError:
                    pass  # Continue to next method
            
            # Method 3: Manual extraction if JSON parsing fails
            function_match = re.search(r'"function":\s*"([^"]+)"', response)
            if function_match:
                function_name = function_match.group(1)
                
                # Try to extract parameters
                params = {}
                segment_match = re.search(r'"segment":\s*"([^"]+)"', response)
                if segment_match:
                    params["segment"] = segment_match.group(1)
                
                start_date_match = re.search(r'"start_date":\s*"([^"]+)"', response)
                if start_date_match:
                    params["start_date"] = start_date_match.group(1)
                
                end_date_match = re.search(r'"end_date":\s*"([^"]+)"', response)
                if end_date_match:
                    params["end_date"] = end_date_match.group(1)
                
                print(f"🔍 Manual extraction: function={function_name}, params={params}")
                return {"function": function_name, "parameters": params}
            
            # Method 4: Look for function names directly in text - ENHANCED
            function_candidates = []
            for schema in FUNCTION_SCHEMAS:
                if schema["name"] in response:
                    function_candidates.append(schema["name"])
                    print(f"🔍 Found function name in text: {schema['name']}")
            
            # If multiple candidates, prefer more specific ones
            if function_candidates:
                # Prioritize longer/more specific function names
                best_function = max(function_candidates, key=len)
                print(f"🔍 Selected best function candidate: {best_function}")
                return {"function": best_function, "parameters": {}}
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
        except Exception as e:
            print(f"❌ Error parsing LLM response: {e}")
        
        print("❌ Could not parse LLM response")
        return None

    def execute_function(self, function_name, parameters):
        """Execute the identified function with parameters"""
        if function_name not in self.tools:
            return {"error": f"Function {function_name} not found"}
        
        try:
            func = self.tools[function_name]
            
            # Call function with appropriate parameters
            if function_name in ["get_new_customer_revenue", "get_customer_segment_report"]:
                result = func(
                    parameters.get("segment", "all"),
                    parameters.get("start_date", "2024-01-01"),
                    parameters.get("end_date", "2024-12-31")
                )
            elif function_name == "get_roi":
                result = func(parameters.get("campaign_id", "default"))
            else:
                result = func(
                    parameters.get("start_date", "2024-01-01"),
                    parameters.get("end_date", "2024-12-31")
                )
            
            return result
            
        except Exception as e:
            return {"error": f"Error executing {function_name}: {str(e)}"}

    def create_improved_prompt(self, query):
        """Tạo prompt cải thiện cho LLM với schemas từ JSON file - optimized for Llama"""
        
        # Create a detailed schema list for better LLM understanding
        schema_descriptions = []
        for i, schema in enumerate(FUNCTION_SCHEMAS):
            params_desc = []
            for param_name, param_info in schema["parameters"]["properties"].items():
                param_desc = f"{param_name} ({param_info.get('type', 'string')})"
                if param_name in schema["parameters"]["required"]:
                    param_desc += " [REQUIRED]"
                params_desc.append(param_desc)
            
            schema_descriptions.append({
                "id": i + 1,
                "name": schema["name"],
                "description": schema["description"],
                "parameters": ", ".join(params_desc),
                "examples": self._get_function_examples(schema["name"])
            })
        
        return f"""You are a Vietnamese business analytics expert. Your job is to identify the correct function from exactly {SCHEMA_COUNT} predefined functions.

AVAILABLE FUNCTIONS ({SCHEMA_COUNT} functions):
{self._format_schemas_for_llm(schema_descriptions)}

ANALYSIS RULES:
1. READ the user query carefully in Vietnamese
2. IDENTIFY the main business intent (revenue, orders, customers, v.v.)
3. CHOOSE exactly ONE function from the {SCHEMA_COUNT} functions above
4. RETURN only JSON format with "function" and "parameters"

QUERY INTENT MAPPING:
- "doanh thu tổng" → get_total_revenue
- "lợi nhuận tổng" → get_total_profit
- "lợi nhuận trung bình theo tháng" → get_avg_profit_by_month
- "lợi nhuận trung bình theo quý" → get_avg_profit_by_quarter
- "so sánh lợi nhuận" → compare_profit
- "doanh thu phân khúc" → get_customer_segment_report  
- "báo cáo phân khúc" → get_customer_segment_report
- "khách hàng mới" → get_new_customer_count
- "đơn hàng" → get_total_orders
- "đơn hàng trên X triệu" → get_orders_above_value
- "đơn hàng VIP" → get_vip_orders
- "chi tiết đơn hàng ORD123" → get_order_detail
- "lịch sử khách CUST123" → get_customer_history
- "so sánh doanh thu" → compare_revenue (time periods)
- "so sánh doanh thu các chi nhánh" → compare_revenue_by_branch (branches)
- "doanh thu các chi nhánh" → get_total_revenue_by_branch (branch report)
- "doanh thu sản phẩm X" → get_revenue_by_product
- "ROI" → get_roi
- "traffic/truy cập" → get_traffic_stats

PROFIT QUERY HANDLING:
- "lợi nhuận" + "trung bình theo tháng" → get_avg_profit_by_month
- "lợi nhuận" + "trung bình theo quý" → get_avg_profit_by_quarter  
- "lợi nhuận" + "so sánh" → compare_profit
- "lợi nhuận" (general) → get_total_profit

COMPARISON FUNCTIONS - IMPORTANT DISTINCTION:
- compare_revenue: So sánh doanh thu giữa HAI KHOẢNG THỜI GIAN khác nhau
- compare_profit: So sánh lợi nhuận giữa HAI KHOẢNG THỜI GIAN khác nhau
- compare_revenue_by_branch: So sánh doanh thu giữa CÁC CHI NHÁNH trong cùng thời gian
- get_total_revenue_by_branch: Báo cáo doanh thu các chi nhánh (không so sánh)

USER QUERY: "{query}"

Think step by step:
1. What is the main business metric? (revenue/profit/orders/customers)
2. Is this about profit analysis by time period? → Use get_avg_profit_by_month/quarter
3. Is this comparing profit between periods? → Use compare_profit
4. Is there a specific segment mentioned?
5. Which function matches best?

Return ONLY this JSON format:
{{"function": "function_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}"""

    def _get_function_examples(self, function_name):
        """Get examples for specific functions"""
        examples = {
            "get_total_revenue": "tổng doanh thu, doanh thu tháng",
            "get_total_profit": "tổng lợi nhuận, lợi nhuận năm",
            "get_avg_profit_by_month": "lợi nhuận trung bình theo tháng, lợi nhuận từng tháng",
            "get_avg_profit_by_quarter": "lợi nhuận trung bình theo quý, lợi nhuận từng quý",
            "compare_profit": "so sánh lợi nhuận, profit comparison",
            "get_customer_segment_report": "báo cáo phân khúc, doanh thu VIP",
            "get_new_customer_count": "khách hàng mới, số lượng khách mới",
            "get_total_orders": "đơn hàng, số đơn",
            "get_orders_above_value": "đơn hàng trên 100 triệu, orders above value",
            "get_vip_orders": "đơn hàng VIP, VIP orders",
            "get_order_detail": "chi tiết đơn hàng ORD123",
            "get_customer_history": "lịch sử khách CUST123",
            "compare_revenue": "so sánh doanh thu",
            "get_roi": "ROI, return on investment"
        }
        return examples.get(function_name, "")

    def _format_schemas_for_llm(self, schema_descriptions):
        """Format schemas in a clear way for LLM"""
        formatted = []
        for schema in schema_descriptions:
            formatted.append(f"""
{schema['id']}. {schema['name']}
   Mô tả: {schema['description']}
   Tham số: {schema['parameters']}
   Ví dụ: {schema['examples']}""")
        return "\n".join(formatted)

    def validate_and_map_to_schema(self, function_name, parameters):
        """Validate function call against predefined schemas and return schema ID"""
        schema_id, schema = get_schema_by_name(function_name)
        
        if not schema:
            print(f"❌ Function '{function_name}' not found in allowed schemas")
            return None
        
        # Validate and clean parameters
        schema_params = schema["parameters"]["properties"]
        required_params = schema["parameters"]["required"]
        validated_params = {}
        
        # Check required parameters
        for param_name in required_params:
            if param_name in parameters:
                validated_params[param_name] = parameters[param_name]
            elif param_name in ["start_date", "end_date"]:
                # Set default dates if missing
                if param_name == "start_date":
                    validated_params[param_name] = "2024-01-01"
                else:
                    validated_params[param_name] = "2024-12-31"
            else:
                print(f"⚠️ Missing required parameter: {param_name}")
        
        # Add optional parameters if present
        for param_name in schema_params:
            if param_name in parameters and param_name not in validated_params:
                validated_params[param_name] = parameters[param_name]
        
        print(f"✅ Matched Schema ID: {schema_id}")
        print(f"📋 Schema Description: {schema['description']}")
        
        return {
            "schema_id": schema_id,
            "function": function_name,
            "parameters": validated_params,
            "description": schema["description"]
        }

    def process_query(self, query):
        """Xử lý câu hỏi: LLM chọn function trước, pattern matching cải thiện parameters"""
        print(f"\n🙋 Bạn: {query}")
        print(f"🔍 Đang phân tích câu hỏi: '{query}'")
        
        # Skip very short inputs
        if len(query.strip()) < 3:
            print("⚠️ Câu hỏi quá ngắn. Vui lòng nhập câu hỏi cụ thể hơn.")
            return {"error": "Query too short"}
        
        # Step 1: LLM chọn function (PRIMARY METHOD)
        print("🤖 Sử dụng LLM để chọn function...")
        
        # Use original Vietnamese query for better understanding
        improved_prompt = self.create_improved_prompt(query)
        llm_result = self.call_llm(improved_prompt)
        
        if llm_result:
            function_name = llm_result.get("function")
            llm_parameters = llm_result.get("parameters", {})
            
            print(f"✅ LLM selected function: {function_name}")
            print(f"📋 LLM parameters: {json.dumps(llm_parameters, indent=2, ensure_ascii=False)}")
            
            # Step 1.5: Validate function against schemas
            schema_result = self.validate_and_map_to_schema(function_name, llm_parameters)
            
            if schema_result:
                # Step 2: Pattern matching để cải thiện parameters (dates, segments)
                print("🔍 Sử dụng pattern matching để cải thiện parameters...")
                
                pattern_result = self.analyze_query_with_pattern_matching(query)
                
                if pattern_result and pattern_result["function"] == function_name:
                    # Same function: merge parameters with pattern taking priority for dates/segments
                    print("✅ Pattern matching confirms function choice")
                    
                    final_params = schema_result["parameters"].copy()
                    pattern_params = pattern_result["parameters"]
                    
                    # Use pattern matching for more accurate dates
                    if "start_date" in pattern_params and "end_date" in pattern_params:
                        final_params["start_date"] = pattern_params["start_date"]
                        final_params["end_date"] = pattern_params["end_date"]
                        print("   📅 Using pattern matching dates (more accurate)")
                    
                    # Use pattern matching for campaign_id if available
                    if "campaign_id" in pattern_params and pattern_params["campaign_id"] != "unknown":
                        final_params["campaign_id"] = pattern_params["campaign_id"]
                        print("   🎯 Using pattern matching campaign ID (more accurate)")
                    
                      # Use pattern matching for customer_id if available
                    if "customer_id" in pattern_params and pattern_params["customer_id"] != "unknown":
                        final_params["customer_id"] = pattern_params["customer_id"]
                        print("   👤 Using pattern matching customer ID (more accurate)")
                    
                    # Use pattern matching for order_id if available
                    if "order_id" in pattern_params and pattern_params["order_id"] != "unknown":
                        final_params["order_id"] = pattern_params["order_id"]
                        print("   📦 Using pattern matching order ID (more accurate)")
                    
                    # Use pattern matching for segments
                    if "segment" in pattern_params and "segment" in final_params:
                        final_params["segment"] = pattern_params["segment"]
                        print("   👥 Using pattern matching segment (more accurate)")
                    elif "segment" in pattern_params:
                        # Add segment if it's missing from LLM but detected by pattern matching
                        final_params["segment"] = pattern_params["segment"]
                        print("   👥 Adding missing segment from pattern matching")

                    schema_result["parameters"] = final_params
                    method = "llm_function_with_pattern_params"
                elif pattern_result:
                    # Different functions: check if pattern matching is more appropriate
                    pattern_function = pattern_result["function"]
                    llm_function = function_name
                    
                    # Special case: LLM chose general function but pattern detected segment-specific query
                    if (llm_function == "get_total_revenue" and 
                        pattern_function == "get_customer_segment_report" and
                        pattern_result["parameters"].get("segment") != "all"):
                        
                        print("🔄 Pattern matching detected segment-specific query, overriding LLM choice")
                        print(f"   LLM chose: {llm_function}")
                        print(f"   Pattern chose: {pattern_function} (better for segment queries)")
                        
                        # Use pattern matching result instead
                        override_result = self.validate_and_map_to_schema(
                            pattern_function, 
                            pattern_result["parameters"]
                        )
                        
                        if override_result:
                            return {
                                "schema_id": override_result["schema_id"],
                                "function": override_result["function"],
                                "parameters": override_result["parameters"],
                                "description": override_result["description"],
                                "status": "ready_to_execute",
                                "method": "pattern_override_llm"
                            }
                    
                    # Special case: LLM chose wrong function but pattern detected best selling product query
                    elif (pattern_function == "get_top_selling_product" and
                          any(keyword in query.lower() for keyword in ['sản phẩm', 'product']) and
                          any(keyword in query.lower() for keyword in ['bán chạy nhất', 'best selling', 'phổ biến nhất', 'popular', 'top selling', 'nhiều nhất'])):
                        
                        print("🔄 Pattern matching detected best selling product query, overriding LLM choice")
                        print(f"   LLM chose: {llm_function} (wrong for best selling product queries)")
                        print(f"   Pattern chose: {pattern_function} (correct for best selling product)")
                        
                        # Use pattern matching result instead
                        override_result = self.validate_and_map_to_schema(
                            pattern_function, 
                            pattern_result["parameters"]
                        )
                        
                        if override_result:
                            return {
                                "schema_id": override_result["schema_id"],
                                "function": override_result["function"],
                                "parameters": override_result["parameters"],
                                "description": override_result["description"],
                                "status": "ready_to_execute",
                                "method": "pattern_override_llm_best_selling_product"
                            }
                    
                    # Special case: LLM chose revenue but pattern detected clear order query
                    elif (llm_function == "get_total_revenue" and 
                          pattern_function == "get_total_orders" and
                          any(keyword in query.lower() for keyword in ['đơn hàng', 'orders', 'order', 'bao nhiêu đơn', 'số đơn'])):
                        
                        print("🔄 Pattern matching detected order query, overriding LLM choice")
                        print(f"   LLM chose: {llm_function} (wrong for order queries)")
                        print(f"   Pattern chose: {pattern_function} (correct for order count)")
                        
                        # Use pattern matching result instead
                        override_result = self.validate_and_map_to_schema(
                            pattern_function, 
                            pattern_result["parameters"]
                        )
                        
                        if override_result:
                            return {
                                "schema_id": override_result["schema_id"],
                                "function": override_result["function"],
                                "parameters": override_result["parameters"],
                                "description": override_result["description"],
                                "status": "ready_to_execute",
                                "method": "pattern_override_llm_order_query"
                            }
                    
                    # Special case: LLM chose monthly profit function but pattern detected general profit
                    elif (llm_function == "get_avg_profit_by_month" and 
                          pattern_function == "get_total_profit"):
                        
                        print("🔄 LLM chose monthly profit, pattern chose general profit - using LLM choice (more specific)")
                        print(f"   LLM chose: {llm_function} (more specific for monthly analysis)")
                        print(f"   Pattern chose: {pattern_function} (too general)")
                        
                        # Use LLM function but pattern dates (LLM choice takes priority)
                        final_params = schema_result["parameters"].copy()
                        pattern_params = pattern_result["parameters"]
                        
                        if "start_date" in pattern_params and "end_date" in pattern_params:
                            final_params["start_date"] = pattern_params["start_date"]
                            final_params["end_date"] = pattern_params["end_date"]
                            print("   📅 Using pattern matching dates (more accurate)")
                        
                        schema_result["parameters"] = final_params
                        method = "llm_function_with_pattern_dates_profit_override"

                    # Special case: Both chose same function type but different specificity (product queries)
                    elif (llm_function == "get_top_selling_product" and 
                          pattern_function == "get_top_selling_product"):
                        
                        print("✅ Both LLM and pattern chose same function, using pattern dates")
                        
                        # Use LLM function but pattern dates
                        final_params = schema_result["parameters"].copy()
                        pattern_params = pattern_result["parameters"]
                        
                        if "start_date" in pattern_params and "end_date" in pattern_params:
                            final_params["start_date"] = pattern_params["start_date"]
                            final_params["end_date"] = pattern_params["end_date"]
                            print("   📅 Using pattern matching dates (more accurate)")
                        
                        schema_result["parameters"] = final_params
                        method = "llm_function_with_pattern_dates_same_function"
                    
                    # Default case: different functions - trust LLM choice but use pattern dates
                    else:
                        print(f"🔄 Different functions detected - LLM: {llm_function}, Pattern: {pattern_function}")
                        print(f"   Using LLM choice but enhancing with pattern dates")
                        
                        # Use LLM function but pattern dates
                        final_params = schema_result["parameters"].copy()
                        pattern_params = pattern_result["parameters"]
                        
                        if "start_date" in pattern_params and "end_date" in pattern_params:
                            final_params["start_date"] = pattern_params["start_date"]
                            final_params["end_date"] = pattern_params["end_date"]
                            print("   📅 Using pattern matching dates (more accurate)")
                        
                        schema_result["parameters"] = final_params
                        method = "llm_function_with_pattern_dates_different_functions"
                else:
                    # No pattern match: trust LLM completely but try to enhance dates
                    print("ℹ️ No pattern matching function, but trying to enhance dates...")
                    
                    # Try to extract dates from query using pattern matching logic
                    query_lower = query.lower()
                    year_candidates = re.findall(r'\b(\d{4})\b', query_lower)
                    year = 2024  # default
                    
                    for candidate in year_candidates:
                        candidate_int = int(candidate)
                        if 1900 <= candidate_int <= 2100:
                            order_pattern = r'(?:ord|order|đơn)\s*\w*' + candidate
                            if not re.search(order_pattern, query_lower):
                                year = candidate_int
                                break
                    
                    # Extract month if present
                    month_detected = False
                    for month_text, month_num in {
                        'tháng 1': 1, 'tháng một': 1, 'january': 1, 'jan': 1,
                        'tháng 2': 2, 'tháng hai': 2, 'february': 2, 'feb': 2,
                        'tháng 3': 3, 'tháng ba': 3, 'march': 3, 'mar': 3,
                        'tháng 4': 4, 'tháng tư': 4, 'april': 4, 'apr': 4,
                        'tháng 5': 5, 'tháng năm': 5, 'may': 5,
                        'tháng 6': 6, 'tháng sáu': 6, 'june': 6, 'jun': 6,
                        'tháng 7': 7, 'tháng bảy': 7, 'july': 7, 'jul': 7,
                        'tháng 8': 8, 'tháng tám': 8, 'august': 8, 'aug': 8,
                        'tháng 9': 9, 'tháng chín': 9, 'september': 9, 'sep': 9,
                        'tháng 10': 10, 'tháng mười':  10, 'october': 10, 'oct': 10,
                        'tháng 11': 11, 'tháng mười một': 11, 'november': 11, 'nov': 11,
                        'tháng 12': 12, 'tháng mười hai': 12, 'december': 12, 'dec': 12
                    }.items():
                        if month_text in query_lower:
                            import calendar
                            last_day = calendar.monthrange(year, month_num)[1]
                            start_date = f"{year:04d}-{month_num:02d}-01"
                            end_date = f"{year:04d}-{month_num:02d}-{last_day:02d}"
                            
                            final_params = schema_result["parameters"].copy()
                            final_params["start_date"] = start_date
                            final_params["end_date"] = end_date
                            print(f"   📅 Enhanced dates from query: {start_date} to {end_date}")
                            schema_result["parameters"] = final_params
                            method = "llm_primary_with_enhanced_dates"
                            month_detected = True
                            break
                    
                    if not month_detected:
                        method = "llm_primary"

                return {
                    "schema_id": schema_result["schema_id"],
                    "function": schema_result["function"],
                    "parameters": schema_result["parameters"],
                    "description": schema_result["description"],
                    "status": "ready_to_execute",
                    "method": method
                }
            else:
                print("❌ LLM selected invalid function, trying pattern matching fallback...")
        else:
            print("❌ LLM failed, trying pattern matching fallback...")
        
        # Step 3: Fallback to pattern matching if LLM fails completely
        print("🔍 Fallback: Sử dụng pattern matching...")
        
        pattern_result = self.analyze_query_with_pattern_matching(query)
        
        if pattern_result:
            function_name = pattern_result["function"]
            parameters = pattern_result["parameters"]
            
            schema_result = self.validate_and_map_to_schema(function_name, parameters)
            
            if schema_result:
                # Fix date parameters to use pattern matching dates
                final_params = schema_result["parameters"].copy()
                if "start_date" in parameters and "end_date" in parameters:
                    final_params["start_date"] = parameters["start_date"]
                    final_params["end_date"] = parameters["end_date"]
                    print(f"   📅 Using pattern matching dates: {parameters['start_date']} to {parameters['end_date']}")
                
                return {
                    "schema_id": schema_result["schema_id"],
                    "function": schema_result["function"],
                    "parameters": final_params,
                    "description": schema_result["description"],
                    "status": "ready_to_execute",
                    "method": "pattern_fallback"
                }
        
        return {"error": f"Could not map query to any of the {SCHEMA_COUNT} predefined schemas"}

    def _extract_campaign_id(self, query_lower):
        """Extract campaign ID from query for ROI functions"""
        # First try to use campaign mapping for better detection
        mapped_campaign = get_campaign_from_query(query_lower)
        if mapped_campaign:
            return mapped_campaign
        
        # Common campaign patterns
        campaign_patterns = [
            r'chiến dịch\s+([a-zA-Z0-9_\-]+)',  # "chiến dịch campaign_name"
            r'campaign\s+([a-zA-Z0-9_\-]+)',    # "campaign campaign_name"
            r'của\s+([a-zA-Z0-9_\-]+)',         # "của campaign_name"
            r'roi\s+([a-zA-Z0-9_\-]+)',         # "roi campaign_name"
        ]
        
        for pattern in campaign_patterns:
            match = re.search(pattern, query_lower)
            if match:
                campaign_id = match.group(1)
                print(f"🎯 Extracted campaign ID: {campaign_id}")
                return campaign_id
        
        # Fallback: look for any identifier-like string
        words = query_lower.split()
        for i, word in enumerate(words):
            # Skip common words
            if word in ['chiến', 'dịch', 'campaign', 'roi', 'của', 'báo', 'cáo', 'năm', 'tháng', 'cho', 'tôi']:
                continue
            
            # Look for identifier patterns (contains underscores or mixed case)
            if '_' in word or any(c.isdigit() for c in word):
                print(f"🎯 Found potential campaign ID: {word}")
                return word
        
        print("⚠️ No campaign ID found, using 'unknown'")
        return "unknown"

# Định nghĩa bảng campaign mapping
CAMPAIGN_MAPPING = {
    # Marketing Campaigns
    "quang_cao_mua_le_hoi": {
        "id": "quang_cao_mua_le_hoi",
        "name": "Quảng cáo mùa lễ hội",
        "keywords": ["mùa lễ hội", "lễ hội", "holiday", "festival", "tết", "giáng sinh", "christmas"],
        "type": "seasonal"
    },
    "black_friday_2023": {
        "id": "black_friday_2023", 
        "name": "Black Friday 2023",
        "keywords": ["black friday", "thứ 6 đen", "giảm giá lớn", "sale lớn"],
        "type": "promotional"
    },
    "summer_sale": {
        "id": "summer_sale",
        "name": "Khuyến mãi mùa hè",
        "keywords": ["mùa hè", "summer", "hè", "khuyến mãi hè"],
        "type": "seasonal"
    },
    "new_customer_acquisition": {
        "id": "new_customer_acquisition",
        "name": "Thu hút khách hàng mới",
        "keywords": ["khách hàng mới", "new customer", "thu hút", "acquisition"],
        "type": "customer_acquisition"
    },
    "loyalty_program": {
        "id": "loyalty_program", 
        "name": "Chương trình khách hàng thân thiết",
        "keywords": ["thân thiết", "loyalty", "trung thành", "vip"],
        "type": "retention"
    },
    "social_media_ads": {
        "id": "social_media_ads",
        "name": "Quảng cáo mạng xã hội",
        "keywords": ["mạng xã hội", "social media", "facebook", "instagram", "tiktok"],
        "type": "digital"
    },
    "google_ads_q4": {
        "id": "google_ads_q4",
        "name": "Google Ads Q4",
        "keywords": ["google ads", "quý 4", "q4", "search ads"],
        "type": "digital"
    }
}

def get_campaign_from_query(query):
    """Detect campaign from query using the campaign mapping table"""
    query_lower = query.lower()
    
    # Score each campaign based on keyword matches
    campaign_scores = {}
    
    for campaign_id, campaign_info in CAMPAIGN_MAPPING.items():
        score = 0
        keywords = campaign_info["keywords"]
        
        for keyword in keywords:
            if keyword in query_lower:
                # Longer keywords get higher scores
                score += len(keyword.split()) * 2
                # Exact match gets bonus
                if keyword == query_lower.strip():
                    score += 5
        
        if score > 0:
            campaign_scores[campaign_id] = score
    
    # Return the campaign with highest score
    if campaign_scores:
        best_campaign = max(campaign_scores, key=campaign_scores.get)
        print(f"🎯 Detected campaign: {best_campaign} (score: {campaign_scores[best_campaign]})")
        print(f"📋 Campaign name: {CAMPAIGN_MAPPING[best_campaign]['name']}")
        return best_campaign
    
    print("🔍 No specific campaign detected")
    return None

def main():
    """Main chatbot conversation loop"""
    print(f"🤖 Business Analytics Chatbot ({SCHEMA_COUNT} Predefined Schemas)")
    print("=" * 60)
    print("Tôi có thể giúp bạn phân tích dữ liệu kinh doanh.")
    print("Hãy đặt câu hỏi về doanh thu, đơn hàng, khách hàng, v.v.")
    print(f"Chỉ hỗ trợ {SCHEMA_COUNT} function schema được định nghĩa trước.")
    print("Gõ 'quit' hoặc 'exit' để thoát.")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = BusinessAnalyticsChatbot()
    
    while True:
        try:
            # Get user input
            question = input("\n🙋 Bạn: ").strip()
            
            # Check for exit commands
            if question.lower() in ['quit', 'exit', 'thoát', 'bye', 'goodbye']:
                print("👋 Tạm biệt! Cảm ơn bạn đã sử dụng chatbot.")
                break
            
            if not question:
                print("⚠️ Vui lòng nhập câu hỏi.")
                continue
            
            # Process the question
            result = chatbot.process_query(question)
            
            if result and "error" not in result:
                print(f"\n🎯 Function Call Result:")
                print(f"   Schema ID: {result.get('schema_id')}")
                print(f"   Function: {result.get('function')}")
                print(f"   Description: {result.get('description')}")
                print(f"   Parameters: {json.dumps(result.get('parameters', {}), indent=4, ensure_ascii=False)}")
                print(f"   Status: {result.get('status', 'unknown')}")
                print(f"   Method: {result.get('method', 'unknown')}")
            else:
                error_msg = result.get("error", "Unknown error") if result else "Could not process query"
                print(f"❌ {error_msg}")
                print(f"💡 Hỗ trợ {SCHEMA_COUNT} loại câu hỏi: doanh thu, đơn hàng, khách hàng, ROI, traffic, v.v.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Tạm biệt! Cảm ơn bạn đã sử dụng chatbot.")
            break
        except Exception as e:
            print(f"❌ Lỗi không mong muốn: {e}")
            print("💡 Vui lòng thử lại.")

if __name__ == "__main__":
    main()