"""
Critical fix test for Reddit analyzer - handles invalid credentials gracefully
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_reddit_analyzer_with_invalid_creds():
    """Test Reddit analyzer with potentially invalid credentials"""
    try:
        from reddit_analyzer import RedditAnalyzer
        
        # Get Reddit credentials from environment (may be invalid)
        client_id = os.getenv('REDDIT_CLIENT_ID', 'invalid_id')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET', 'invalid_secret')
        
        print(f"🔧 Testing with credentials: {client_id[:10]}... / {client_secret[:10]}...")
        
        # Initialize analyzer (should handle invalid credentials gracefully)
        analyzer = RedditAnalyzer(client_id, client_secret)
        print("✅ RedditAnalyzer initialized")
        
        # Test with sample business info
        sample_business_info = {
            "product_summary": "TaskFlow - simple project management for small teams",
            "keywords": ["project management", "productivity", "task tracking"],
            "pain_points_solved": ["disorganized tasks", "missed deadlines", "poor communication"],
            "recommended_subreddits": ["entrepreneur", "smallbusiness", "productivity"]
        }
        
        print("🧪 Testing question search...")
        questions = await analyzer.find_relevant_questions(
            business_info=sample_business_info,
            max_questions=5,  # Small number for testing
            subreddit_limit=3,
            min_upvotes=5,
            days_back=7
        )
        
        if questions and len(questions) > 0:
            print(f"✅ Found {len(questions)} questions successfully!")
            print("\n📋 Sample questions found:")
            for i, q in enumerate(questions[:3], 1):
                print(f"   {i}. r/{q.get('subreddit', 'unknown')}: {q.get('title', 'No title')[:60]}...")
                print(f"      Score: {q.get('relevance_score', 0):.2f} | Method: {q.get('search_method', 'unknown')}")
            
            return True
        else:
            print("❌ No questions found")
            return False
            
    except Exception as e:
        print(f"❌ Error in Reddit analyzer test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the critical fix test"""
    print("🚨 CRITICAL FIX TEST: Reddit Analyzer with Invalid Credentials")
    print("=" * 70)
    print("This test verifies the bot works even with invalid Reddit credentials")
    print("by falling back to mock data for demonstration purposes.")
    print()
    
    success = await test_reddit_analyzer_with_invalid_creds()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 CRITICAL FIX SUCCESSFUL!")
        print("✅ Reddit analyzer now handles invalid credentials gracefully")
        print("✅ Falls back to mock data when Reddit API is unavailable")
        print("✅ Bot will continue to work for demonstration purposes")
        print("\n💡 To use real Reddit data, get valid credentials from:")
        print("   https://www.reddit.com/prefs/apps")
    else:
        print("❌ CRITICAL FIX FAILED!")
        print("The Reddit analyzer still has issues. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())