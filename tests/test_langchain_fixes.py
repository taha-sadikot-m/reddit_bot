"""
Quick test to verify LangChain fixes work
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_business_analyzer():
    """Test the fixed business analyzer"""
    try:
        from business_analyzer import BusinessAnalyzer
        
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        # Initialize analyzer
        analyzer = BusinessAnalyzer(api_key)
        print("✅ BusinessAnalyzer initialized successfully")
        
        # Test with a simple business description
        test_description = "A simple task management app for small teams to organize their work and deadlines"
        
        print("🧪 Testing business analysis...")
        result = await analyzer.analyze_business(test_description)
        
        if result and isinstance(result, dict):
            print("✅ Business analysis completed successfully")
            print(f"   Product Summary: {result.get('product_summary', 'N/A')[:50]}...")
            print(f"   Keywords: {len(result.get('keywords', []))} found")
            print(f"   Subreddits: {len(result.get('recommended_subreddits', []))} recommended")
            return True
        else:
            print("❌ Business analysis failed - no valid result")
            return False
            
    except Exception as e:
        print(f"❌ Error in business analyzer test: {str(e)}")
        return False

async def test_ai_response_generator():
    """Test the fixed AI response generator"""
    try:
        from ai_response_generator import AIResponseGenerator
        
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
        
        # Initialize generator
        generator = AIResponseGenerator(api_key)
        print("✅ AIResponseGenerator initialized successfully")
        
        # Test with sample data
        sample_question = {
            "title": "Looking for a good project management tool",
            "selftext": "Need something simple for my small team",
            "subreddit": "entrepreneur"
        }
        
        sample_business = {
            "product_summary": "TaskFlow - simple project management for small teams",
            "key_benefits": ["easy to use", "affordable", "team collaboration"]
        }
        
        print("🧪 Testing response generation...")
        response = await generator.generate_response(
            sample_question, 
            sample_business, 
            response_style="Casual"
        )
        
        if response and len(response) > 10:
            print("✅ Response generation completed successfully")
            print(f"   Generated response: {response[:100]}...")
            return True
        else:
            print("❌ Response generation failed - no valid response")
            return False
            
    except Exception as e:
        print(f"❌ Error in AI response generator test: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing LangChain Fixes")
    print("=" * 50)
    
    # Test business analyzer
    print("\n📊 Testing Business Analyzer...")
    business_test = await test_business_analyzer()
    
    print("\n🤖 Testing AI Response Generator...")
    response_test = await test_ai_response_generator()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   Business Analyzer: {'✅ PASS' if business_test else '❌ FAIL'}")
    print(f"   Response Generator: {'✅ PASS' if response_test else '❌ FAIL'}")
    
    if business_test and response_test:
        print("\n🎉 All tests passed! LangChain fixes are working.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())