# 🔧 Reddit API Setup Guide for Automated Posting

## 🚨 **Reddit Authentication Issue Resolved**

The error `unauthorized_client error processing request (Only script apps may use password auth)` indicates that your Reddit app needs to be configured as a "script" type application.

---

## 📝 **Step-by-Step Reddit API Configuration**

### **1. Create Reddit App (Correct Configuration)**

1. **Go to Reddit Apps**: https://www.reddit.com/prefs/apps
2. **Click "Create App" or "Create Another App"**
3. **IMPORTANT**: Select **"script"** as the app type (not "web app")
4. **Fill in the form:**
   ```
   Name: RedditMarketingBot (or any name you prefer)
   App type: script ⚠️ MUST be "script" for password auth
   Description: Automated Reddit marketing assistant
   About URL: (leave blank)
   Redirect URI: http://localhost:8080 (required but not used)
   ```
5. **Click "Create app"**

### **2. Get Your Credentials**

After creating the app, you'll see:
- **Client ID**: The string under your app name (14 characters, like `abc123def456gh`)
- **Client Secret**: The "secret" field (27 characters, like `ABC123def456GHI789jkl012MNO`)

### **3. Update config.py**

Replace the credentials in `config.py`:

```python
REDDIT_CONFIG = {
    "client_id": "your_actual_client_id_here",     # 14-character string from step 2
    "client_secret": "your_actual_client_secret_here", # 27-character string from step 2
    "user_agent": "RedditMarketingBot/1.0 by YourRedditUsername",
    "username": "your_actual_reddit_username",     # Your Reddit username (no u/ prefix)
    "password": "your_actual_reddit_password"      # Your Reddit account password
}
```

---

## 🛡️ **Security & Account Safety**

### **Recommended Account Setup:**

1. **Create a Dedicated Account**: 
   - Don't use your main personal Reddit account
   - Create a new account specifically for this bot
   - Build some karma manually before automating (post a few genuine comments)

2. **Account Requirements:**
   - Account should be at least 1-2 days old
   - Have some comment karma (5-10 points minimum)
   - Verify email address on the account

3. **App-Specific Password** (if using 2FA):
   - If your Reddit account has 2FA enabled, you may need an app-specific password
   - Go to Reddit preferences and generate one for this bot

---

## 🧪 **Test Your Setup**

### **1. Quick Authentication Test**

Create a simple test file:

```python
# test_reddit_auth.py
import praw
from config import REDDIT_CONFIG

try:
    reddit = praw.Reddit(
        client_id=REDDIT_CONFIG['client_id'],
        client_secret=REDDIT_CONFIG['client_secret'],
        username=REDDIT_CONFIG['username'],
        password=REDDIT_CONFIG['password'],
        user_agent=REDDIT_CONFIG['user_agent']
    )
    
    user = reddit.user.me()
    print(f"✅ Authentication successful! Logged in as: {user.name}")
    print(f"   Comment Karma: {user.comment_karma}")
    print(f"   Link Karma: {user.link_karma}")
    print(f"   Account Created: {user.created_utc}")
    
except Exception as e:
    print(f"❌ Authentication failed: {str(e)}")
```

### **2. Run the Test**

```bash
python test_reddit_auth.py
```

You should see:
```
✅ Authentication successful! Logged in as: your_username
   Comment Karma: 10
   Link Karma: 1
   Account Created: 1640995200.0
```

---

## 🔧 **Troubleshooting Common Issues**

### **Error: "unauthorized_client"**
- **Solution**: Ensure your Reddit app type is set to **"script"**, not "web app"
- **Check**: Your client_id and client_secret are correct

### **Error: "invalid_grant"**
- **Solution**: Check your username and password are correct
- **Check**: Account doesn't have 2FA enabled (or use app-specific password)

### **Error: "rate_limit"**
- **Solution**: You're making too many requests - add delays between calls
- **Check**: Wait a few minutes and try again

### **Error: "insufficient_scope"**
- **Solution**: This shouldn't happen with script apps, but verify your credentials

---

## 🚀 **After Successful Setup**

Once your Reddit authentication works:

1. **Run the full test**:
   ```bash
   python test_posting_system.py
   ```

2. **Launch the enhanced interface**:
   ```bash
   streamlit run enhanced_posting_app.py
   ```

3. **Start with dry run mode** to test without actually posting

---

## ⚠️ **Important Safety Notes**

### **Rate Limits:**
- Reddit allows 1 comment per 10 minutes for new accounts
- Established accounts can post more frequently
- Our bot automatically respects these limits

### **Account Protection:**
- Start with 2-3 posts per day maximum
- Monitor your account for any warnings
- Use high-quality, helpful responses only
- Don't spam the same subreddits repeatedly

### **Subreddit Rules:**
- Each subreddit has its own rules about self-promotion
- Read the rules before posting in new subreddits
- Some subreddits ban promotional content entirely
- Focus on subreddits where your product genuinely helps

---

## 📞 **Need Help?**

If you're still having issues after following this guide:

1. **Double-check** that your Reddit app type is "script"
2. **Verify** all credentials are copied correctly (no extra spaces)
3. **Test** with a simple PRAW script first
4. **Check** if your account has any restrictions

Once authentication works, the full posting system will be ready to use! 🎉