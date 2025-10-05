"""
Test script to validate the improvements to human-like responses and better question finding
"""

import asyncio
import json
from typing import Dict, Any

# Import our improved components
from ai_response_generator import AIResponseGenerator
from reddit_analyzer import RedditAnalyzer

# Mock test data
SAMPLE_QUESTIONS = [
    {
        "title": "Need help finding a good project management tool for small team",
        "selftext": "Hey everyone! I'm running a small startup with 5 people and we're struggling to keep track of all our tasks and deadlines. We've tried using spreadsheets but it's getting messy. Looking for recommendations for a simple project management tool that won't break the bank. Any suggestions?",
        "subreddit": "entrepreneur",
        "score": 25,
        "num_comments": 12,
        "created_utc": 1640995200
    },
    {
        "title": "How to automate repetitive tasks in my business?",
        "selftext": "I spend way too much time on repetitive admin tasks like data entry, scheduling, and follow-ups. It's killing my productivity. Does anyone know of tools or methods to automate this stuff? I'm not super technical but willing to learn.",
        "subreddit": "smallbusiness",
        "score": 45,
        "num_comments": 23,
        "created_utc": 1640995200
    }
]

SAMPLE_BUSINESS_INFO = {
    "product_summary": "TaskFlow - a simple project management and automation tool for small businesses",
    "key_benefits": ["saves time on admin tasks", "keeps teams organized", "affordable pricing"],
    "use_cases": ["project tracking", "task automation", "team collaboration"],
    "pain_points_solved": ["disorganized task management", "repetitive manual work", "poor team communication"],
    "keywords": ["project management", "task automation", "productivity", "small business tools"],
    "marketing_angles": ["Position as affordable alternative", "Highlight ease of use", "Focus on time-saving benefits"]
}

async def test_response_generation():
    """Test the improved response generation"""
    print("🧪 Testing Response Generation Improvements...")
    print("=" * 60)
    
    # Initialize with mock API key (won't actually call API in this test)
    generator = AIResponseGenerator("mock_api_key")
    
    # Test different styles
    styles = ["Casual", "Professional", "Friendly"]
    
    for i, question in enumerate(SAMPLE_QUESTIONS, 1):
        print(f"\n📝 Test Question {i}:")
        print(f"Title: {question['title']}")
        print(f"Subreddit: r/{question['subreddit']}")
        print("-" * 40)
        
        for style in styles:
            print(f"\n🎭 {style} Style Response:")
            try:
                # Test the prompt generation components
                style_guide = generator._get_style_guide(style)
                casual_patterns = generator._get_casual_patterns()
                business_context = generator._format_business_context(SAMPLE_BUSINESS_INFO)
                
                print(f"Style Guide: {style_guide}")
                print(f"Casual Patterns: {casual_patterns}")
                print(f"Business Context: {business_context[:100]}...")
                
                # Test post-processing with a sample response
                sample_response = "I understand that you are looking for a solution to your problem. I would recommend that you consider trying TaskFlow. It is important to note that this tool can help you. Additionally, you should not worry about the cost."
                
                processed = generator._post_process_response(sample_response, question, SAMPLE_BUSINESS_INFO)
                print(f"Processed Response: {processed}")
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            print("-" * 20)
    
    print("\n✅ Response generation test completed!")

def test_question_scoring():
    """Test the improved question relevance scoring"""
    print("\n🧪 Testing Question Scoring Improvements...")
    print("=" * 60)
    
    # Initialize with mock credentials
    analyzer = RedditAnalyzer("mock_client_id", "mock_client_secret")
    
    # Mock post objects for testing
    class MockPost:
        def __init__(self, title, selftext, score, num_comments, created_utc):
            self.title = title
            self.selftext = selftext
            self.score = score
            self.num_comments = num_comments
            self.created_utc = created_utc
            self.is_self = True
    
    # Test posts with different characteristics
    test_posts = [
        MockPost(
            "Looking for project management software recommendations",
            "Need something simple and affordable for my small team",
            15, 8, 1640995200
        ),
        MockPost(
            "Just a random meme lol",
            "This is just a joke post with no real content",
            5, 2, 1640995200
        ),
        MockPost(
            "Struggling with task automation - any tools to help?",
            "I spend hours on repetitive work and need to automate it somehow",
            35, 18, 1640995200
        )
    ]
    
    search_terms = analyzer._generate_search_terms(SAMPLE_BUSINESS_INFO)
    print(f"Generated Search Terms: {search_terms[:10]}...")  # Show first 10
    
    print(f"\n📊 Relevance Scores:")
    for i, post in enumerate(test_posts, 1):
        score = analyzer._calculate_relevance_score(post, search_terms, SAMPLE_BUSINESS_INFO)
        quality_check = analyzer._is_quality_post(post, 5)
        
        print(f"\nPost {i}: '{post.title[:50]}...'")
        print(f"  Relevance Score: {score:.2f}")
        print(f"  Quality Check: {'✅ Pass' if quality_check else '❌ Fail'}")
        print(f"  Marketing Opportunity: {'🎯 High' if score > 1.0 else '📈 Medium' if score > 0.5 else '📉 Low'}")
    
    print("\n✅ Question scoring test completed!")

def test_casual_patterns():
    """Test the casual language patterns"""
    print("\n🧪 Testing Casual Language Patterns...")
    print("=" * 60)
    
    generator = AIResponseGenerator("mock_api_key")
    
    # Test multiple pattern generations
    print("Sample Casual Patterns:")
    for i in range(5):
        patterns = generator._get_casual_patterns()
        print(f"{i+1}. {patterns}")
    
    # Test post-processing improvements
    test_responses = [
        "I understand that you are looking for a solution. I would recommend that you try this tool.",
        "It is important to note that you should not worry about this issue.",
        "Additionally, you will find that this approach works well for your situation."
    ]
    
    print("\n📝 Post-Processing Examples:")
    for i, response in enumerate(test_responses, 1):
        processed = generator._post_process_response(response, SAMPLE_QUESTIONS[0], SAMPLE_BUSINESS_INFO)
        print(f"\nOriginal {i}: {response}")
        print(f"Processed {i}: {processed}")
    
    print("\n✅ Casual patterns test completed!")

async def main():
    """Run all tests"""
    print("🚀 Testing Reddit Bot Improvements")
    print("=" * 80)
    
    # Run tests
    await test_response_generation()
    test_question_scoring()
    test_casual_patterns()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary of Improvements:")
    print("✅ Human-like response generation with casual language")
    print("✅ Concise responses (1-3 sentences)")
    print("✅ Better question relevance scoring")
    print("✅ Enhanced quality filtering")
    print("✅ Marketing opportunity detection")
    print("✅ Casual language patterns and contractions")

if __name__ == "__main__":
    asyncio.run(main())