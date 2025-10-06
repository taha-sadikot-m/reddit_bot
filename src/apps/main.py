"""
Reddit API Client - Comprehensive Python wrapper for Reddit API endpoints
Requires: pip install praw
"""

import praw
from typing import List, Dict, Any, Optional
import time

class RedditAPIClient:
    def __init__(self, client_id: str, client_secret: str, user_agent: str, 
                 username: str = None, password: str = None):
        """
        Initialize Reddit API client
        
        Args:
            client_id: Reddit app client ID
            client_secret: Reddit app client secret
            user_agent: User agent string (e.g., "MyApp/1.0 by YourUsername")
            username: Reddit username (optional, for authenticated requests)
            password: Reddit password (optional, for authenticated requests)
        """
        if username and password:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                username=username,
                password=password,
                user_agent=user_agent
            )
        else:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )

    # SUBREDDIT ENDPOINTS
    
    def get_subreddit_info(self, subreddit_name: str) -> Dict[str, Any]:
        """Get subreddit information"""
        subreddit = self.reddit.subreddit(subreddit_name)
        return {
            'display_name': subreddit.display_name,
            'title': subreddit.title,
            'description': subreddit.description,
            'subscribers': subreddit.subscribers,
            'created_utc': subreddit.created_utc,
            'over18': subreddit.over18,
            'public_description': subreddit.public_description
        }
    
    def get_subreddit_hot_posts(self, subreddit_name: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get hot posts from subreddit"""
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.hot(limit=limit):
            posts.append(self._format_post(post))
        return posts
    
    def get_subreddit_new_posts(self, subreddit_name: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get new posts from subreddit"""
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.new(limit=limit):
            posts.append(self._format_post(post))
        return posts
    
    def get_subreddit_top_posts(self, subreddit_name: str, time_filter: str = 'day', 
                               limit: int = 25) -> List[Dict[str, Any]]:
        """Get top posts from subreddit"""
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.top(time_filter=time_filter, limit=limit):
            posts.append(self._format_post(post))
        return posts
    
    def get_subreddit_rising_posts(self, subreddit_name: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get rising posts from subreddit"""
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.rising(limit=limit):
            posts.append(self._format_post(post))
        return posts
    
    def search_subreddit(self, subreddit_name: str, query: str, sort: str = 'relevance', 
                        time_filter: str = 'all', limit: int = 25) -> List[Dict[str, Any]]:
        """Search within a subreddit"""
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.search(query, sort=sort, time_filter=time_filter, limit=limit):
            posts.append(self._format_post(post))
        return posts

    # POST ENDPOINTS
    
    def get_post_by_id(self, post_id: str) -> Dict[str, Any]:
        """Get post by ID"""
        post = self.reddit.submission(id=post_id)
        return self._format_post(post)
    
    def get_post_comments(self, post_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get comments for a post"""
        post = self.reddit.submission(id=post_id)
        post.comments.replace_more(limit=0)  # Remove "more comments" objects
        comments = []
        for comment in post.comments.list():
            comments.append(self._format_comment(comment))
        if limit:
            comments = comments[:limit]
        return comments
    
    def submit_post(self, subreddit_name: str, title: str, selftext: str = None, 
                   url: str = None, flair_id: str = None) -> str:
        """Submit a new post (requires authentication)"""
        subreddit = self.reddit.subreddit(subreddit_name)
        if selftext:
            post = subreddit.submit(title=title, selftext=selftext, flair_id=flair_id)
        elif url:
            post = subreddit.submit(title=title, url=url, flair_id=flair_id)
        else:
            raise ValueError("Either selftext or url must be provided")
        return post.id
    
    def upvote_post(self, post_id: str):
        """Upvote a post (requires authentication)"""
        post = self.reddit.submission(id=post_id)
        post.upvote()
    
    def downvote_post(self, post_id: str):
        """Downvote a post (requires authentication)"""
        post = self.reddit.submission(id=post_id)
        post.downvote()
    
    def save_post(self, post_id: str):
        """Save a post (requires authentication)"""
        post = self.reddit.submission(id=post_id)
        post.save()
    
    def unsave_post(self, post_id: str):
        """Unsave a post (requires authentication)"""
        post = self.reddit.submission(id=post_id)
        post.unsave()

    # COMMENT ENDPOINTS
    
    def get_comment_by_id(self, comment_id: str) -> Dict[str, Any]:
        """Get comment by ID"""
        comment = self.reddit.comment(id=comment_id)
        return self._format_comment(comment)
    
    def reply_to_post(self, post_id: str, text: str) -> str:
        """Reply to a post (requires authentication)"""
        post = self.reddit.submission(id=post_id)
        reply = post.reply(text)
        return reply.id
    
    def reply_to_comment(self, comment_id: str, text: str) -> str:
        """Reply to a comment (requires authentication)"""
        comment = self.reddit.comment(id=comment_id)
        reply = comment.reply(text)
        return reply.id
    
    def upvote_comment(self, comment_id: str):
        """Upvote a comment (requires authentication)"""
        comment = self.reddit.comment(id=comment_id)
        comment.upvote()
    
    def downvote_comment(self, comment_id: str):
        """Downvote a comment (requires authentication)"""
        comment = self.reddit.comment(id=comment_id)
        comment.downvote()
    
    def edit_comment(self, comment_id: str, new_text: str):
        """Edit a comment (requires authentication and ownership)"""
        comment = self.reddit.comment(id=comment_id)
        comment.edit(new_text)
    
    def delete_comment(self, comment_id: str):
        """Delete a comment (requires authentication and ownership)"""
        comment = self.reddit.comment(id=comment_id)
        comment.delete()

    # USER ENDPOINTS
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user information"""
        user = self.reddit.redditor(username)
        return {
            'name': user.name,
            'created_utc': user.created_utc,
            'comment_karma': user.comment_karma,
            'link_karma': user.link_karma,
            'is_gold': user.is_gold,
            'is_mod': user.is_mod,
            'verified': user.verified,
            'has_verified_email': user.has_verified_email
        }
    
    def get_user_posts(self, username: str, sort: str = 'new', limit: int = 25) -> List[Dict[str, Any]]:
        """Get user's posts"""
        user = self.reddit.redditor(username)
        posts = []
        if sort == 'new':
            submissions = user.submissions.new(limit=limit)
        elif sort == 'hot':
            submissions = user.submissions.hot(limit=limit)
        elif sort == 'top':
            submissions = user.submissions.top(limit=limit)
        else:
            submissions = user.submissions.new(limit=limit)
        
        for post in submissions:
            posts.append(self._format_post(post))
        return posts
    
    def get_user_comments(self, username: str, sort: str = 'new', limit: int = 25) -> List[Dict[str, Any]]:
        """Get user's comments"""
        user = self.reddit.redditor(username)
        comments = []
        if sort == 'new':
            user_comments = user.comments.new(limit=limit)
        elif sort == 'hot':
            user_comments = user.comments.hot(limit=limit)
        elif sort == 'top':
            user_comments = user.comments.top(limit=limit)
        else:
            user_comments = user.comments.new(limit=limit)
            
        for comment in user_comments:
            comments.append(self._format_comment(comment))
        return comments
    
    def follow_user(self, username: str):
        """Follow a user (requires authentication)"""
        user = self.reddit.redditor(username)
        user.friend()
    
    def unfollow_user(self, username: str):
        """Unfollow a user (requires authentication)"""
        user = self.reddit.redditor(username)
        user.unfriend()

    # SEARCH ENDPOINTS
    
    def search_reddit(self, query: str, sort: str = 'relevance', time_filter: str = 'all', 
                     limit: int = 25) -> List[Dict[str, Any]]:
        """Search all of Reddit"""
        posts = []
        for post in self.reddit.subreddit('all').search(query, sort=sort, 
                                                        time_filter=time_filter, limit=limit):
            posts.append(self._format_post(post))
        return posts
    
    def search_subreddits(self, query: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Search for subreddits"""
        subreddits = []
        for subreddit in self.reddit.subreddits.search(query, limit=limit):
            subreddits.append({
                'display_name': subreddit.display_name,
                'title': subreddit.title,
                'subscribers': subreddit.subscribers,
                'over18': subreddit.over18,
                'public_description': subreddit.public_description
            })
        return subreddits

    # MESSAGE ENDPOINTS
    
    def send_private_message(self, username: str, subject: str, message: str):
        """Send a private message (requires authentication)"""
        self.reddit.redditor(username).message(subject, message)
    
    def get_inbox(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Get inbox messages (requires authentication)"""
        messages = []
        for message in self.reddit.inbox.all(limit=limit):
            messages.append({
                'id': message.id,
                'subject': message.subject,
                'body': message.body,
                'author': str(message.author) if message.author else '[deleted]',
                'created_utc': message.created_utc,
                'was_comment': message.was_comment
            })
        return messages
    
    def get_unread_messages(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Get unread messages (requires authentication)"""
        messages = []
        for message in self.reddit.inbox.unread(limit=limit):
            messages.append({
                'id': message.id,
                'subject': message.subject,
                'body': message.body,
                'author': str(message.author) if message.author else '[deleted]',
                'created_utc': message.created_utc,
                'was_comment': message.was_comment
            })
        return messages
    
    def mark_as_read(self, message_id: str):
        """Mark a message as read (requires authentication)"""
        message = self.reddit.inbox.message(message_id)
        message.mark_read()

    # MULTIREDDIT ENDPOINTS
    
    def get_multireddit(self, username: str, multireddit_name: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get posts from a multireddit"""
        multireddit = self.reddit.multireddit(username, multireddit_name)
        posts = []
        for post in multireddit.hot(limit=limit):
            posts.append(self._format_post(post))
        return posts
    
    def create_multireddit(self, name: str, subreddits: List[str], 
                          description: str = '', visibility: str = 'private') -> str:
        """Create a multireddit (requires authentication)"""
        multireddit = self.reddit.multireddit.create(
            display_name=name,
            subreddits=subreddits,
            description_md=description,
            visibility=visibility
        )
        return multireddit.name

    # MODERATION ENDPOINTS (require mod permissions)
    
    def get_modqueue(self, subreddit_name: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get moderation queue (requires mod permissions)"""
        subreddit = self.reddit.subreddit(subreddit_name)
        items = []
        for item in subreddit.mod.queue(limit=limit):
            if hasattr(item, 'title'):  # Post
                items.append(self._format_post(item))
            else:  # Comment
                items.append(self._format_comment(item))
        return items
    
    def remove_post(self, post_id: str, spam: bool = False):
        """Remove a post (requires mod permissions)"""
        post = self.reddit.submission(id=post_id)
        post.mod.remove(spam=spam)
    
    def approve_post(self, post_id: str):
        """Approve a post (requires mod permissions)"""
        post = self.reddit.submission(id=post_id)
        post.mod.approve()
    
    def ban_user(self, subreddit_name: str, username: str, ban_reason: str = '', 
                duration: int = None, ban_message: str = ''):
        """Ban a user from subreddit (requires mod permissions)"""
        subreddit = self.reddit.subreddit(subreddit_name)
        subreddit.banned.add(username, ban_reason=ban_reason, 
                           duration=duration, ban_message=ban_message)

    # HELPER METHODS
    
    def _format_post(self, post) -> Dict[str, Any]:
        """Format a post object into a dictionary"""
        return {
            'id': post.id,
            'title': post.title,
            'author': str(post.author) if post.author else '[deleted]',
            'subreddit': str(post.subreddit),
            'score': post.score,
            'upvote_ratio': post.upvote_ratio,
            'num_comments': post.num_comments,
            'created_utc': post.created_utc,
            'selftext': post.selftext,
            'url': post.url,
            'is_self': post.is_self,
            'over_18': post.over_18,
            'spoiler': post.spoiler,
            'stickied': post.stickied,
            'permalink': f"https://reddit.com{post.permalink}"
        }
    
    def _format_comment(self, comment) -> Dict[str, Any]:
        """Format a comment object into a dictionary"""
        return {
            'id': comment.id,
            'author': str(comment.author) if comment.author else '[deleted]',
            'body': comment.body,
            'score': comment.score,
            'created_utc': comment.created_utc,
            'parent_id': comment.parent_id,
            'is_submitter': comment.is_submitter,
            'stickied': comment.stickied,
            'permalink': f"https://reddit.com{comment.permalink}"
        }

# Example usage
if __name__ == "__main__":
    try:
        # Import configuration
        from config import REDDIT_CONFIG
        
        # Validate configuration
        if REDDIT_CONFIG['client_id'] == "YOUR_CLIENT_ID_HERE":
            print("ERROR: Please update config.py with your actual Reddit API credentials!")
            print("Follow the instructions in config.py to set up your Reddit app.")
            exit(1)
        
        # Initialize client with your credentials (read-only mode, no username/password)
        client = RedditAPIClient(
            client_id=REDDIT_CONFIG['client_id'],
            client_secret=REDDIT_CONFIG['client_secret'],
            user_agent=REDDIT_CONFIG['user_agent']
            # Note: Not using username/password to avoid "script apps only" error
        )
        
        print("Testing Reddit API connection...")
        
        # Example: Get hot posts from a subreddit
        hot_posts = client.get_subreddit_hot_posts("python", limit=5)
        print(f"Successfully retrieved {len(hot_posts)} posts from r/python")
        print("\nHot posts from r/python:")
        for i, post in enumerate(hot_posts, 1):
            print(f"{i}. Title: {post['title'][:80]}...")
            print(f"   Score: {post['score']} | Comments: {post['num_comments']}")
            print("---")
            
    except ImportError:
        print("ERROR: config.py file not found or has import errors!")
        print("Please make sure config.py exists and has valid Python syntax.")
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "received 401 HTTP response" in error_msg:
            print("ERROR: 401 Unauthorized - Invalid Reddit API credentials!")
            print("This means your client_id, client_secret, or user_agent is incorrect.")
            print("Please check your config.py file and make sure you have:")
            print("1. Created a Reddit app at https://www.reddit.com/prefs/apps")
            print("2. Used the correct client_id and client_secret from your app")
            print("3. Set a proper user_agent string")
        elif "403" in error_msg:
            print("ERROR: 403 Forbidden - Access denied!")
            print("Your credentials are valid but you don't have permission for this action.")
        elif "429" in error_msg:
            print("ERROR: 429 Too Many Requests - Rate limited!")
            print("You're making too many requests. Please wait and try again.")
        else:
            print(f"ERROR: {error_msg}")
            print("Please check your internet connection and Reddit API credentials.")