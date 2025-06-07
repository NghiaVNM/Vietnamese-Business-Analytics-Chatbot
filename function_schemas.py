"""
Định nghĩa 21 schema function được phép sử dụng trong chatbot
"""

FUNCTION_SCHEMAS = {
    # Revenue-related functions (7 schemas)
    1: {
        "function": "get_total_revenue",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Lấy tổng doanh thu trong khoảng thời gian"
    },
    2: {
        "function": "get_new_customer_revenue", 
        "parameters": {
            "segment": "new_customer",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Doanh thu từ khách hàng mới"
    },
    3: {
        "function": "get_customer_segment_revenue",
        "parameters": {
            "segment": "premium|middle|economy|enterprise|individual|casual|returning_customer",
            "start_date": "YYYY-MM-DD", 
            "end_date": "YYYY-MM-DD"
        },
        "description": "Doanh thu theo phân khúc khách hàng"
    },
    4: {
        "function": "get_monthly_revenue",
        "parameters": {
            "year": "YYYY",
            "month": "MM"
        },
        "description": "Doanh thu theo tháng cụ thể"
    },
    5: {
        "function": "get_quarterly_revenue",
        "parameters": {
            "year": "YYYY",
            "quarter": "Q1|Q2|Q3|Q4"
        },
        "description": "Doanh thu theo quý"
    },
    6: {
        "function": "get_yearly_revenue",
        "parameters": {
            "year": "YYYY"
        },
        "description": "Doanh thu theo năm"
    },
    7: {
        "function": "get_revenue_by_product",
        "parameters": {
            "product_category": "string",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Doanh thu theo danh mục sản phẩm"
    },

    # Order-related functions (4 schemas)
    8: {
        "function": "get_total_orders",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Tổng số đơn hàng trong khoảng thời gian"
    },
    9: {
        "function": "get_orders_by_segment",
        "parameters": {
            "segment": "premium|middle|economy|enterprise|individual|casual|new_customer|returning_customer",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Số đơn hàng theo phân khúc"
    },
    10: {
        "function": "get_monthly_orders",
        "parameters": {
            "year": "YYYY",
            "month": "MM"
        },
        "description": "Số đơn hàng theo tháng"
    },
    11: {
        "function": "get_order_conversion_rate",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Tỷ lệ chuyển đổi đơn hàng"
    },

    # Customer-related functions (4 schemas)
    12: {
        "function": "get_customer_segment_report",
        "parameters": {
            "segment": "premium|middle|economy|enterprise|individual|casual|new_customer|returning_customer",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Báo cáo chi tiết theo phân khúc khách hàng"
    },
    13: {
        "function": "get_new_customer_count",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Số lượng khách hàng mới"
    },
    14: {
        "function": "get_customer_retention_rate",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Tỷ lệ giữ chân khách hàng"
    },
    15: {
        "function": "get_customer_lifetime_value",
        "parameters": {
            "segment": "premium|middle|economy|enterprise|individual|casual",
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Giá trị vòng đời khách hàng"
    },

    # Marketing & Analytics functions (4 schemas)
    16: {
        "function": "get_roi",
        "parameters": {
            "campaign_id": "string"
        },
        "description": "ROI của chiến dịch marketing"
    },
    17: {
        "function": "get_conversion_rate",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "segment": "premium|middle|economy|enterprise|individual|casual|new_customer|returning_customer|all"
        },
        "description": "Tỷ lệ chuyển đổi theo phân khúc"
    },
    18: {
        "function": "get_website_traffic",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Lượng truy cập website"
    },
    19: {
        "function": "get_user_engagement",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "metric": "pageviews|session_duration|bounce_rate"
        },
        "description": "Mức độ tương tác người dùng"
    },

    # General reports (2 schemas)
    20: {
        "function": "get_sales_report",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD"
        },
        "description": "Báo cáo bán hàng tổng quát"
    },
    21: {
        "function": "get_business_summary",
        "parameters": {
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "include_metrics": ["revenue", "orders", "customers", "conversion"]
        },
        "description": "Tóm tắt tình hình kinh doanh"
    }
}

# Validation functions
def validate_schema_id(schema_id):
    """Validate if schema ID is in allowed range"""
    return 1 <= schema_id <= 21

def get_schema_by_id(schema_id):
    """Get schema by ID"""
    if validate_schema_id(schema_id):
        return FUNCTION_SCHEMAS[schema_id]
    return None

def find_matching_schemas(function_name):
    """Find schemas that match a function name"""
    matching = []
    for schema_id, schema in FUNCTION_SCHEMAS.items():
        if schema["function"] == function_name:
            matching.append((schema_id, schema))
    return matching

def get_all_function_names():
    """Get list of all allowed function names"""
    return list(set(schema["function"] for schema in FUNCTION_SCHEMAS.values()))

def validate_function_call(function_name, parameters):
    """Validate if function call matches any allowed schema"""
    matching_schemas = find_matching_schemas(function_name)
    
    if not matching_schemas:
        return False, f"Function '{function_name}' not found in allowed schemas"
    
    # For now, just check if function exists
    # You can add more detailed parameter validation here
    return True, f"Function '{function_name}' is valid"
