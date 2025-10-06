# Reddit API Configuration
# Replace these with your actual Reddit app credentials

REDDIT_CONFIG = {
    "client_id": "Y96LEdMaSo3y8utdwBJKjg",  # Replace with your actual client ID
    "client_secret": "PlaqeNkvwRvG_Fxu3LxZ7wbmydLhnQ",  # Replace with your actual client secret
    "user_agent": "RedditBot/1.0 by RedditUser",  # Generic user agent that should work
    "username": "TaxProfessional9743",  # Required for posting: your Reddit username
    "password": "Sadikot@123"   # Required for posting: your Reddit password
}

# Instructions for Reddit API Setup:
# 1. Go to https://www.reddit.com/prefs/apps
# 2. Click "Create App" or "Create Another App"
# 3. Choose "script" for personal use
# 4. Fill in the form:
#    - Name: Your app name
#    - App type: Script
#    - Description: Brief description of your bot
#    - About URL: Leave blank or add a URL
#    - Redirect URI: http://localhost:8080 (required but not used for scripts)
# 5. After creating, you'll see:
#    - Client ID: The string under your app name (about 14 characters)
#    - Client Secret: The "secret" field (about 27 characters)
# 6. Replace the values above with your actual credentials
# 
# For Posting Features:
# - You MUST provide your actual Reddit username and password
# - The bot needs these credentials to post comments automatically
# - Make sure your account has sufficient karma to post in target subreddits
# - Some subreddits have minimum account age requirements