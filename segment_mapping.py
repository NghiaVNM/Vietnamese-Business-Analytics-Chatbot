import re

class SegmentMapper:
    """Class to handle customer segment mapping and detection"""
    
    def __init__(self):
        """Initialize segment mapping with predefined patterns"""
        self.segment_patterns = {
            'premium': [
                'cao cấp', 'premium', 'vip', 'thượng hạng', 'luxury',
                'high-end', 'đặc biệt', 'ưu tiên', 'platinum', 'gold'
            ],
            'middle': [
                'trung bình', 'middle', 'standard', 'bình thường',
                'thường', 'regular', 'silver', 'cơ bản', 'basic'
            ],
            'economy': [
                'tiết kiệm', 'economy', 'budget', 'giá rẻ', 'phổ thông',
                'bronze', 'entry', 'starter', 'cấp thấp'
            ],
            'new_customer': [
                'khách hàng mới', 'new customer', 'khách mới',
                'customer mới', 'mới gia nhập', 'first time',
                'lần đầu', 'new users', 'người dùng mới'
            ],
            'returning_customer': [
                'khách hàng cũ', 'returning customer', 'khách cũ',
                'quay lại', 'returning', 'repeat customer',
                'loyal customer', 'thân thiết', 'trung thành'
            ],
            'enterprise': [
                'doanh nghiệp', 'enterprise', 'công ty', 'tổ chức',
                'corporate', 'business', 'b2b', 'thương mại'
            ],
            'individual': [
                'cá nhân', 'individual', 'personal', 'retail',
                'b2c', 'người tiêu dùng', 'consumer'
            ],
            'casual': [
                'vãng lai', 'occasional', 'thỉnh thoảng', 'không thường xuyên',
                'casual', 'sporadic', 'infrequent', 'one-time', 'ngẫu nhiên'
            ]
        }
        
        self.new_customer_keywords = [
            'khách hàng mới', 'new customer', 'khách mới',
            'customer mới', 'mới gia nhập', 'first time',
            'lần đầu', 'new users', 'người dùng mới',
            'khách hàng mới tham gia', 'newly registered',
            'đăng ký mới', 'sign up', 'acquisition'
        ]
        
        print("✅ SegmentMapper initialized")
    
    def get_segment(self, query):
        """Extract customer segment from query text"""
        query_lower = query.lower()
        
        # Score each segment based on keyword matches
        segment_scores = {}
        
        for segment_name, keywords in self.segment_patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    # Longer keywords get higher scores
                    score += len(keyword.split())
            
            if score > 0:
                segment_scores[segment_name] = score
        
        # Return the segment with highest score
        if segment_scores:
            best_segment = max(segment_scores, key=segment_scores.get)
            print(f"🎯 Detected segment: {best_segment} (score: {segment_scores[best_segment]})")
            return best_segment
        
        # Default fallback
        print("🎯 No specific segment detected, using 'all'")
        return 'all'
    
    def detect_new_customer_intent(self, query):
        """Detect if query is asking about new customers specifically"""
        query_lower = query.lower()
        
        # Check for new customer keywords
        for keyword in self.new_customer_keywords:
            if keyword in query_lower:
                print(f"🆕 New customer intent detected: '{keyword}'")
                return True
        
        # Check for pattern combinations that indicate new customer queries
        new_customer_patterns = [
            r'khách.*mới',
            r'new.*customer',
            r'customer.*mới',
            r'mới.*gia nhập',
            r'lần đầu.*mua',
            r'đăng ký.*mới',
            r'acquisition.*customer'
        ]
        
        for pattern in new_customer_patterns:
            if re.search(pattern, query_lower):
                print(f"🆕 New customer pattern detected: '{pattern}'")
                return True
        
        return False
    
    def get_segment_keywords(self, segment):
        """Get keywords for a specific segment"""
        return self.segment_patterns.get(segment, [])
    
    def is_valid_segment(self, segment):
        """Check if segment is valid"""
        valid_segments = list(self.segment_patterns.keys()) + ['all']
        return segment in valid_segments
    
    def map_vietnamese_to_english_segment(self, vietnamese_segment):
        """Map Vietnamese segment names to English equivalents"""
        mapping = {
            'cao cấp': 'premium',
            'trung bình': 'middle',
            'tiết kiệm': 'economy',
            'doanh nghiệp': 'enterprise',
            'cá nhân': 'individual',
            'khách hàng mới': 'new_customer',
            'khách hàng cũ': 'returning_customer',
            'thân thiết': 'returning_customer',
            'vip': 'premium'
        }
        
        return mapping.get(vietnamese_segment.lower(), vietnamese_segment)
    
    def get_all_segments(self):
        """Get list of all available segments"""
        return list(self.segment_patterns.keys()) + ['all']
    
    def analyze_segment_complexity(self, query):
        """Analyze how complex the segment detection is for this query"""
        query_lower = query.lower()
        detected_segments = []
        
        for segment_name, keywords in self.segment_patterns.items():
            for keyword in keywords:
                if keyword in query_lower:
                    detected_segments.append(segment_name)
                    break
        
        complexity_info = {
            'detected_segments': detected_segments,
            'segment_count': len(detected_segments),
            'complexity': 'simple' if len(detected_segments) <= 1 else 'complex',
            'confidence': 'high' if len(detected_segments) == 1 else 'medium' if len(detected_segments) > 1 else 'low'
        }
        
        return complexity_info
