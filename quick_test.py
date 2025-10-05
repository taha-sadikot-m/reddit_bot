"""
Quick Reddit App Type Test
=========================
This will help diagnose if your Reddit app is configured correctly.
"""

import praw

# Your current credentials
CLIENT_ID = "JzMoXfHl2-vkeePH0w0qPA"
CLIENT_SECRET = "ZUA5-WYZftqZMiNcQ0wbalCb8tzP8w"
USER_AGENT = "RedditBot/1.0 by RedditUser"

def test_app_type():
    print("Testing Reddit app configuration...")
    print("=" * 50)
    
    try:
        # Test read-only access (should work for both web app and script)
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT
        )
        
        # Try to access a simple public subreddit
        subreddit = reddit.subreddit('python')
        print(f"✅ Basic connection successful!")
        print(f"Subreddit: {subreddit.display_name}")
        print(f"Subscribers: {subreddit.subscribers:,}")
        
        # Get a few posts to confirm API is working
        posts = list(subreddit.hot(limit=3))
        print(f"✅ Retrieved {len(posts)} posts successfully!")
        
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post.title[:60]}...")
        
        print("\n🎉 SUCCESS: Your Reddit API credentials are working!")
        print("Your bot should now work for read-only operations.")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ ERROR: {error_msg}")
        
        if "401" in error_msg:
            print("\n🔍 DIAGNOSIS: Invalid credentials")
            print("SOLUTIONS:")
            print("1. Double-check your client_id and client_secret")
            print("2. Make sure you copied them correctly from https://www.reddit.com/prefs/apps")
            
        elif "403" in error_msg:
            print("\n🔍 DIAGNOSIS: Access forbidden")
            print("SOLUTIONS:")
            print("1. Your app might need to be approved")
            print("2. Try creating a new Reddit app")
            
        elif "script apps" in error_msg.lower():
            print("\n🔍 DIAGNOSIS: Wrong app type")
            print("SOLUTIONS:")
            print("1. Go to https://www.reddit.com/prefs/apps")
            print("2. Delete your current app")
            print("3. Create a new one and select 'script' (not 'web app')")
            
        else:
            print(f"\n🔍 DIAGNOSIS: Unknown error")
            print("SOLUTIONS:")
            print("1. Check your internet connection")
            print("2. Verify Reddit is accessible")
            print("3. Try creating new credentials")
        
        return False

if __name__ == "__main__":
    test_app_type()
