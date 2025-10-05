"""
Reddit Bot Setup Guide
======================

You're getting a 401 error because your Reddit API credentials are invalid.
Follow these steps EXACTLY to fix it:

STEP 1: Create a Reddit App
---------------------------
1. Go to: https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App" 
3. Fill out the form:
   - Name: MyRedditBot (or any name you like)
   - App type: Select "script" 
   - Description: Personal Reddit bot
   - About URL: (leave blank)
   - Redirect URI: http://localhost:8080

STEP 2: Get Your Credentials  
----------------------------
After creating the app, you'll see something like this:

MyRedditBot
personal use script by YourUsername
[some_long_string_here]  <-- This is your CLIENT_ID

secret: [another_long_string] <-- This is your CLIENT_SECRET

STEP 3: Update config.py
------------------------
Replace the values in config.py with your actual credentials:

REDDIT_CONFIG = {
    "client_id": "your_client_id_from_step_2",
    "client_secret": "your_client_secret_from_step_2", 
    "user_agent": "MyRedditBot/1.0 by YourActualRedditUsername",
    "username": "",  # Leave empty for now
    "password": ""   # Leave empty for now
}

STEP 4: Test Your Setup
-----------------------
Run: python test_credentials.py

This will test if your credentials work before running the main bot.

IMPORTANT NOTES:
- The client_id is usually about 14 characters long
- The client_secret is usually about 27 characters long  
- Replace "YourActualRedditUsername" with your actual Reddit username
- Don't share these credentials with anyone!

COMMON MISTAKES:
- Using fake/example credentials (like "TaxProfessional9743")
- Not replacing "YourUsername" in the user_agent
- Mixing up client_id and client_secret
- Not selecting "script" as the app type
"""

if __name__ == "__main__":
    print(__doc__)
