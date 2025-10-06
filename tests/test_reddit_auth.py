"""
Simple Reddit Authentication Test
Quick test to verify your Reddit API credentials are working
"""

import praw
import sys
import os

# Add the current directory to Python path  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import REDDIT_CONFIG

def test_reddit_authentication():
    """Test Reddit authentication with current credentials"""
    print("🔧 Testing Reddit Authentication...")
    print("=" * 40)
    
    # Check if credentials are configured
    required_fields = ['client_id', 'client_secret', 'username', 'password']
    missing_fields = []
    
    for field in required_fields:
        value = REDDIT_CONFIG.get(field, '')
        if not value or value.startswith('YOUR_'):
            missing_fields.append(field)
    
    if missing_fields:
        print("❌ Missing or unconfigured fields:")
        for field in missing_fields:
            print(f"   - {field}")
        print("\n📝 Please update config.py with your actual Reddit credentials")
        print("📚 See REDDIT_SETUP_GUIDE.md for detailed instructions")
        return False
    
    try:
        print("🔐 Attempting authentication...")
        
        # Create Reddit instance
        reddit = praw.Reddit(
            client_id=REDDIT_CONFIG['client_id'],
            client_secret=REDDIT_CONFIG['client_secret'],
            username=REDDIT_CONFIG['username'],
            password=REDDIT_CONFIG['password'],
            user_agent=REDDIT_CONFIG['user_agent']
        )
        
        # Test authentication by getting user info
        user = reddit.user.me()
        
        if user:
            print("✅ Authentication successful!")
            print(f"   👤 Username: {user.name}")
            print(f"   💬 Comment Karma: {user.comment_karma}")
            print(f"   🔗 Link Karma: {user.link_karma}")
            print(f"   📅 Account Age: {user.created_utc}")
            
            # Check if account is suitable for posting
            print("\n📊 Account Suitability Check:")
            
            # Age check (rough)
            if user.comment_karma >= 5:
                print("   ✅ Sufficient comment karma for posting")
            else:
                print("   ⚠️  Low comment karma - consider posting manually first")
            
            if user.link_karma >= 1:
                print("   ✅ Has some link karma")
            else:
                print("   ℹ️  No link karma (not required)")
            
            print("\n🎉 Your Reddit credentials are working correctly!")
            print("🚀 You can now use the automated posting features.")
            
            return True
        else:
            print("❌ Authentication failed - no user returned")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Authentication failed: {error_msg}")
        
        # Provide specific guidance based on error type
        if "unauthorized_client" in error_msg:
            print("\n🔧 Solution: Your Reddit app must be configured as 'script' type")
            print("   1. Go to https://www.reddit.com/prefs/apps")
            print("   2. Delete your current app")
            print("   3. Create a new app with type 'script' (not 'web app')")
            print("   4. Update your config.py with the new credentials")
            
        elif "invalid_grant" in error_msg:
            print("\n🔧 Solution: Check your username and password")
            print("   1. Verify your Reddit username (without u/ prefix)")
            print("   2. Verify your Reddit password")
            print("   3. If you have 2FA enabled, create an app-specific password")
            
        elif "rate" in error_msg.lower():
            print("\n🔧 Solution: Rate limited - wait a few minutes and try again")
            
        else:
            print("\n📚 Check REDDIT_SETUP_GUIDE.md for detailed troubleshooting")
        
        return False

def main():
    """Main function"""
    print("🧪 Reddit Authentication Test")
    print("=" * 50)
    
    success = test_reddit_authentication()
    
    if success:
        print("\n✅ Ready to proceed with automated posting!")
        print("🚀 Next steps:")
        print("   1. Run: python test_posting_system.py")
        print("   2. Or run: streamlit run enhanced_posting_app.py")
    else:
        print("\n❌ Please fix authentication issues before proceeding")
        print("📚 See REDDIT_SETUP_GUIDE.md for help")
    
    return success

if __name__ == "__main__":
    main()