"""
Reddit Credentials Tester
=========================
Use this script to test if your Reddit API credentials are working
before running the main bot.
"""

import praw
from config import REDDIT_CONFIG

def test_credentials():
    """Test Reddit API credentials"""
    
    print("Testing Reddit API credentials...")
    print("=" * 50)
    
    # Check if config has been updated
    if REDDIT_CONFIG['client_id'] == "YOUR_CLIENT_ID_HERE":
        print("❌ ERROR: You haven't updated config.py yet!")
        print("Please follow the instructions in setup_guide.py")
        return False
    
    # Display current config (hide sensitive info)
    print(f"Client ID: {REDDIT_CONFIG['client_id'][:6]}...")
    print(f"Client Secret: {REDDIT_CONFIG['client_secret'][:6]}...")
    print(f"User Agent: {REDDIT_CONFIG['user_agent']}")
    print()
    
    try:
        # Test basic connection
        reddit = praw.Reddit(
            client_id=REDDIT_CONFIG['client_id'],
            client_secret=REDDIT_CONFIG['client_secret'],
            user_agent=REDDIT_CONFIG['user_agent']
        )
        
        # Try to access a simple endpoint
        print("Testing connection...")
        subreddit = reddit.subreddit('test')
        
        # This will trigger authentication
        print(f"Subreddit name: {subreddit.display_name}")
        print(f"Subscribers: {subreddit.subscribers}")
        
        print("✅ SUCCESS: Your credentials are working!")
        print("You can now run main.py")
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        print(f"❌ ERROR: {e}")
        print()
        
        if "401" in error_msg or "unauthorized" in error_msg:
            print("DIAGNOSIS: Invalid credentials")
            print("SOLUTION:")
            print("1. Double-check your client_id and client_secret")
            print("2. Make sure you created a 'script' type app, not 'web app'")
            print("3. Verify you copied the credentials correctly")
            
        elif "403" in error_msg or "forbidden" in error_msg:
            print("DIAGNOSIS: Access forbidden")
            print("SOLUTION:")
            print("1. Your credentials might be valid but restricted")
            print("2. Try creating a new Reddit app")
            
        elif "user_agent" in error_msg or "429" in error_msg:
            print("DIAGNOSIS: User agent issue or rate limiting")
            print("SOLUTION:")
            print("1. Make sure your user_agent follows format: 'AppName/Version by Username'")
            print("2. Replace 'YourUsername' with your actual Reddit username")
            print("3. Wait a few minutes if rate limited")
            
        else:
            print("DIAGNOSIS: Unknown error")
            print("SOLUTION:")
            print("1. Check your internet connection")
            print("2. Verify Reddit is not down")
            print("3. Try creating new credentials")
        
        return False

if __name__ == "__main__":
    success = test_credentials()
    
    if not success:
        print("\n" + "=" * 50)
        print("Need help? Run: python setup_guide.py")
        print("Or visit: https://www.reddit.com/prefs/apps")
