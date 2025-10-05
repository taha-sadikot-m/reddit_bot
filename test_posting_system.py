"""
Test the Reddit Posting System
Comprehensive testing of the automated posting functionality
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow_manager import WorkflowManager
from reddit_poster import RedditPoster
from config import REDDIT_CONFIG

async def test_reddit_posting_system():
    """Test the complete Reddit posting system"""
    print("🚀 Testing Reddit Posting System")
    print("=" * 50)
    
    # Test configuration
    test_business = """
    We offer a SaaS platform that helps small businesses manage their inventory efficiently. Our tool provides real-time tracking, automated reordering, and detailed analytics. Target customers are small to medium retail businesses looking to optimize their stock management.
    """
    
    try:
        # Initialize workflow manager with posting capabilities
        print("\n1️⃣ Initializing Workflow Manager...")
        
        # Check if we have Reddit credentials for posting
        has_posting_creds = (
            REDDIT_CONFIG.get('username') and 
            REDDIT_CONFIG.get('password') and 
            not REDDIT_CONFIG['username'].startswith('YOUR_') and
            not REDDIT_CONFIG['password'].startswith('YOUR_')
        )
        
        workflow_manager = WorkflowManager(
            gemini_api_key=os.getenv('GEMINI_API_KEY', 'your-gemini-api-key-here'),
            reddit_client_id=REDDIT_CONFIG['client_id'],
            reddit_client_secret=REDDIT_CONFIG['client_secret'],
            reddit_username=REDDIT_CONFIG['username'] if has_posting_creds else None,
            reddit_password=REDDIT_CONFIG['password'] if has_posting_creds else None
        )
        
        print(f"✅ Workflow Manager initialized")
        print(f"   Posting enabled: {'Yes' if has_posting_creds else 'No'}")
        
        # Test the complete workflow with posting
        print("\n2️⃣ Running Complete Workflow with Posting...")
        
        results = await workflow_manager.run_complete_workflow(
            business_description=test_business,
            max_questions=5,  # Small number for testing
            subreddit_limit=3,
            response_style="Casual",
            min_upvotes=1,
            days_back=7,
            auto_post=has_posting_creds,  # Only enable if we have credentials
            dry_run=False  # Always dry run for testing
        )
        
        print("\n✅ Workflow completed!")
        
        # Display results
        print("\n3️⃣ Workflow Results:")
        print("-" * 30)
        
        summary = results.get('workflow_summary', {})
        print(f"📊 Questions found: {summary.get('total_questions_found', 0)}")
        print(f"📝 Responses generated: {summary.get('responses_generated', 0)}")
        print(f"✅ Success: {summary.get('success', False)}")
        
        # Posting results
        posting_results = results.get('posting_results', {})
        if posting_results:
            print(f"\n📤 Posting Results:")
            print(f"   Posted: {posting_results.get('posted', 0)}")
            print(f"   Skipped: {posting_results.get('skipped', 0)}")
            print(f"   Failed: {posting_results.get('failed', 0)}")
            
            # Show details
            details = posting_results.get('details', [])
            if details:
                print(f"\n📋 Posting Details:")
                for i, detail in enumerate(details[:3], 1):  # Show first 3
                    status = "✅" if detail['success'] else "❌"
                    print(f"   {i}. {status} {detail['question_title'][:50]}...")
                    print(f"      r/{detail['subreddit']} - {detail['message']}")
        
        # Test individual Reddit poster functionality
        if has_posting_creds:
            print("\n4️⃣ Testing Reddit Poster Directly...")
            await test_reddit_poster_direct()
        else:
            print("\n4️⃣ Skipping direct poster test (no credentials)")
        
        # Display sample Q&A pairs
        qa_pairs = results.get('question_answer_pairs', [])
        if qa_pairs:
            print(f"\n5️⃣ Sample Question & Response:")
            print("-" * 40)
            
            sample = qa_pairs[0]
            print(f"🔍 Subreddit: r/{sample.get('subreddit', 'unknown')}")
            print(f"📝 Question: {sample.get('title', 'N/A')[:80]}...")
            print(f"🤖 Response: {sample.get('ai_response', 'N/A')[:100]}...")
            print(f"⭐ Score: {sample.get('score', 0)} upvotes")
            print(f"💬 Comments: {sample.get('num_comments', 0)}")
            
            if sample.get('url'):
                print(f"🔗 URL: {sample.get('url')}")
        
        print("\n✅ All tests completed successfully!")
        
        # Provide user guidance
        print("\n" + "=" * 50)
        print("🎯 Next Steps:")
        print("1. Update your Reddit credentials in config.py for live posting")
        print("2. Set dry_run=False when ready for live posting")
        print("3. Start with a small number of questions for safety")
        print("4. Monitor your Reddit account for any issues")
        print("5. Use the enhanced_posting_app.py for the full interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_reddit_poster_direct():
    """Test the Reddit poster directly"""
    try:
        print("   Initializing Reddit Poster...")
        
        poster = RedditPoster(
            client_id=REDDIT_CONFIG['client_id'],
            client_secret=REDDIT_CONFIG['client_secret'],
            username=REDDIT_CONFIG['username'],
            password=REDDIT_CONFIG['password']
        )
        
        # Test authentication
        success = await poster.initialize()
        if success:
            print("   ✅ Reddit authentication successful")
            
            # Get posting stats
            stats = poster.get_posting_stats()
            print(f"   📊 Username: {stats['username']}")
            print(f"   📊 Daily posts: {stats['daily_posts']}/{stats['daily_limit']}")
            print(f"   📊 Total posted: {stats['total_posted']}")
            print(f"   📊 Can post now: {stats['can_post_now']}")
            
            # Test content quality assessment
            test_response = "Hey! I've been using TaskFlow for a few months now and it's really helped me stay organized. The AI prioritization is surprisingly good at figuring out what I should work on first. You might want to check it out if you're struggling with task management like I was."
            
            test_question = {
                'id': 'test123',
                'title': 'Looking for a good productivity app for remote work',
                'selftext': 'I work from home and struggle to stay organized',
                'subreddit': 'productivity'
            }
            
            is_suitable, quality_msg, score = poster._assess_content_quality(test_response, test_question)
            print(f"   🧪 Content quality test: {'✅ Suitable' if is_suitable else '❌ Not suitable'}")
            print(f"   📊 Quality score: {score:.2f}")
            print(f"   💬 Message: {quality_msg}")
            
        else:
            print("   ❌ Reddit authentication failed")
            
    except Exception as e:
        print(f"   ❌ Direct poster test failed: {str(e)}")

def test_configuration():
    """Test configuration setup"""
    print("🔧 Testing Configuration...")
    
    # Check Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key and not gemini_key.startswith('your-'):
        print("   ✅ Gemini API key found in environment")
    else:
        print("   ⚠️  Gemini API key not found - using placeholder")
    
    # Check Reddit config
    required_fields = ['client_id', 'client_secret', 'username', 'password']
    config_status = {}
    
    for field in required_fields:
        value = REDDIT_CONFIG.get(field, '')
        if value and not value.startswith('YOUR_'):
            config_status[field] = "✅ Configured"
        else:
            config_status[field] = "❌ Needs configuration"
    
    print("   Reddit Configuration Status:")
    for field, status in config_status.items():
        print(f"     {field}: {status}")
    
    return all("✅" in status for status in config_status.values())

async def main():
    """Main test function"""
    print("🧪 Reddit Marketing Bot - Posting System Test")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_configuration()
    
    if not config_ok:
        print("\n⚠️  Some configuration missing, but continuing with available features...")
    
    # Run posting system test
    success = await test_reddit_posting_system()
    
    if success:
        print("\n🎉 All tests passed! The posting system is ready.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    print("\n📚 Documentation:")
    print("- Use enhanced_posting_app.py for the full Streamlit interface")
    print("- Configure your Reddit credentials in config.py")
    print("- Always test with dry_run=True first")
    print("- Monitor your Reddit account for any automation flags")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())