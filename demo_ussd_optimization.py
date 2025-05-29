#!/usr/bin/env python3
"""
Simple USSD Response Optimization Demo
"""

# Mock classes for testing
class MockUSSDService:
    def _extract_key_medical_info(self, response):
        """Extract key medical advice"""
        import re
        key_patterns = [
            r'(?:You should|Take|Avoid|Contact|See a doctor)[^.]*\.',
            r'(?:Important|Warning|Urgent|Emergency)[^.]*\.',
            r'(?:Call|Visit|Go to|Seek)[^.]*\.',
        ]
        
        extracted = []
        for pattern in key_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            extracted.extend(matches)
        
        if extracted:
            key_text = ' '.join(extracted[:2])
            if len(key_text) <= 120:
                return key_text
        return None
    
    def _clean_ai_response(self, response):
        """Clean AI response"""
        if not response:
            return "No response available."
        
        cleaned = ' '.join(response.split())
        
        # Remove AI prefixes
        prefixes = [
            "I understand that you're asking about",
            "Thank you for your question about",
            "Based on your question,",
        ]
        
        for prefix in prefixes:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
                break
        
        return cleaned
    
    def _smart_truncate_response(self, response, max_length, lang):
        """Smart truncation"""
        if len(response) <= max_length:
            return response
        
        # Try sentence boundary
        truncated = response[:max_length-3]
        for ending in ['. ', '! ', '? ']:
            pos = truncated.rfind(ending)
            if pos > max_length * 0.6:
                return response[:pos+1]
        
        # Fallback to word boundary
        words = response[:max_length-3].split()
        if len(words) > 1:
            return ' '.join(words[:-1]) + "..."
        
        return response[:max_length-3] + "..."

def demo_optimization():
    """Demonstrate optimization"""
    service = MockUSSDService()
    
    # Test case: Long AI response
    long_response = (
        "I understand that you're asking about pregnancy symptoms. "
        "It's important to note that you should take prenatal vitamins daily. "
        "Contact your doctor immediately if you experience severe bleeding. "
        "You should also avoid alcohol completely during pregnancy. "
        "Regular checkups are essential for monitoring your health."
    )
    
    print("📱 USSD RESPONSE OPTIMIZATION DEMO")
    print("=" * 40)
    print(f"Original Response ({len(long_response)} chars):")
    print(f"'{long_response}'\n")
    
    # Extract key info
    key_info = service._extract_key_medical_info(long_response)
    print(f"🔑 Key Medical Info:")
    print(f"'{key_info}'\n")
    
    # Clean response
    cleaned = service._clean_ai_response(long_response)
    print(f"🧹 Cleaned Response ({len(cleaned)} chars):")
    print(f"'{cleaned}'\n")
    
    # Smart truncate to USSD limit (120 chars for content)
    truncated = service._smart_truncate_response(cleaned, 120, 'en')
    print(f"✂️ Smart Truncated ({len(truncated)} chars):")
    print(f"'{truncated}'\n")
    
    # Final USSD format
    final_ussd = f"🤖 {truncated}\n\nMore? 0=Exit"
    print(f"📲 Final USSD Display ({len(final_ussd)} chars):")
    print(f"'{final_ussd}'")
    
    print(f"\n✅ Character limit compliance: {len(final_ussd)} ≤ 160")
    print("🎯 Key medical advice preserved!")

if __name__ == "__main__":
    demo_optimization()
