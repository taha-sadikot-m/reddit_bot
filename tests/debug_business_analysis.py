"""
Debug Business Analysis
Test to see what the business analyzer is actually returning
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from business_analyzer import BusinessAnalyzer
import json

async def debug_business_analysis():
    """Debug the business analysis to see what's happening with subreddit recommendations"""
    print("🔍 Debugging Business Analysis")
    print("=" * 50)
    
    # Test business description
    test_business = """
    We offer a SaaS platform that helps small businesses manage their inventory efficiently. Our tool provides real-time tracking, automated reordering, and detailed analytics. Target customers are small to medium retail businesses looking to optimize their stock management.
    """
    
    try:
        # Initialize business analyzer
        print("1️⃣ Initializing Business Analyzer...")
        analyzer = BusinessAnalyzer(os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here'))
        print("✅ Business Analyzer initialized")
        
        # Run business analysis
        print("\n2️⃣ Running Business Analysis...")
        business_info = await analyzer.analyze_business(test_business)
        
        # Print detailed results
        print("\n3️⃣ Business Analysis Results:")
        print("-" * 40)
        
        print(f"📊 Raw Result Type: {type(business_info)}")
        print(f"📊 Keys Available: {list(business_info.keys())}")
        
        # Check each important field
        important_fields = [
            'product_summary', 'target_audience', 'industry_category', 
            'recommended_subreddits', 'key_benefits', 'keywords'
        ]
        
        for field in important_fields:
            value = business_info.get(field, 'NOT FOUND')
            print(f"📝 {field}: {value}")
        
        # Focus on subreddits
        subreddits = business_info.get('recommended_subreddits', [])
        print(f"\n🎯 Subreddit Analysis:")
        print(f"   Subreddits found: {len(subreddits)}")
        print(f"   Subreddits list: {subreddits}")
        
        if not subreddits:
            print("❌ NO SUBREDDITS FOUND - This is the problem!")
            
            # Let's test the enhance subreddit method directly
            print("\n4️⃣ Testing Enhanced Subreddit Generation...")
            try:
                enhanced_subreddits = await analyzer._enhance_subreddit_recommendations(business_info)
                print(f"   Enhanced subreddits: {enhanced_subreddits}")
            except Exception as e:
                print(f"   ❌ Enhanced subreddit generation failed: {str(e)}")
        else:
            print("✅ Subreddits found successfully!")
        
        # Print full JSON for debugging
        print(f"\n📋 Full Business Analysis JSON:")
        print(json.dumps(business_info, indent=2, default=str))
        
        return business_info
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_direct_gemini():
    """Test Gemini API directly to see if it's working"""
    print("\n🧪 Testing Gemini API Directly...")
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        test_prompt = """
        Analyze this business: "We offer a SaaS platform that helps small businesses manage their inventory efficiently."
        
        Return JSON with this structure:
        {
            "product_summary": "brief summary",
            "recommended_subreddits": ["subreddit1", "subreddit2", "subreddit3"]
        }
        """
        
        response = model.generate_content(test_prompt)
        print(f"✅ Direct Gemini Response:")
        print(response.text)
        
    except Exception as e:
        print(f"❌ Direct Gemini test failed: {str(e)}")

async def main():
    """Main debug function"""
    print("🐛 Business Analysis Debug Session")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and not api_key.startswith('your-'):
        print("✅ Gemini API key found")
    else:
        print("❌ Gemini API key missing or placeholder")
        return
    
    # Run debug
    result = await debug_business_analysis()
    
    if result:
        print("\n✅ Debug completed successfully!")
    else:
        print("\n❌ Debug failed!")
    
    # Test direct Gemini API
    await test_direct_gemini()

if __name__ == "__main__":
    asyncio.run(main())