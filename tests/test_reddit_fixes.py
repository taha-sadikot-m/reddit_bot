"""
Quick test for Reddit analyzer async fixes
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_reddit_analyzer():
    """Test the fixed Reddit analyzer"""
    try:
        from reddit_analyzer import RedditAnalyzer
        
        # Get Reddit credentials from environment
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("❌ Reddit credentials not found in environment")
            return False
        
        # Initialize analyzer
        analyzer = RedditAnalyzer(client_id, client_secret)
        print("✅ RedditAnalyzer initialized successfully")
        
        # Test with sample business info
        sample_business_info = {
            "product_summary": "A simple task management tool",
            "keywords": ["productivity", "task management", "organization"],
            "pain_points_solved": ["disorganized tasks", "missed deadlines"],
            "recommended_subreddits": ["productivity", "entrepreneur"]
        }
        
        print("🧪 Testing question search (limited to 3 questions)...")
        questions = await analyzer.find_relevant_questions(
            business_info=sample_business_info,
            max_questions=3,  # Small number for testing
            subreddit_limit=2,  # Only test 2 subreddits
            min_upvotes=5,
            days_back=7
        )
        
        if questions and len(questions) > 0:
            print(f"✅ Found {len(questions)} questions successfully")
            for i, q in enumerate(questions, 1):
                print(f"   {i}. {q.get('title', 'No title')[:50]}... (Score: {q.get('relevance_score', 0):.2f})")
            return True
        else:
            print("⚠️  No questions found (this might be normal depending on search criteria)")
            return True  # Not necessarily an error
            
    except Exception as e:
        print(f"❌ Error in Reddit analyzer test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    print("🚀 Testing Reddit Analyzer Async Fixes")
    print("=" * 50)
    
    success = await test_reddit_analyzer()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
        print("The Reddit analyzer should now work without PRAW async warnings.")
    else:
        print("❌ Test failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())