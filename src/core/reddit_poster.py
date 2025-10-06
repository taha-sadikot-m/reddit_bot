"""
Reddit Poster - Automated posting system for Reddit comments
Handles authentication, posting, rate limiting, and safety features
"""

import praw
import asyncio
import time
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re
import random

class RedditPoster:
    def __init__(self, client_id: str, client_secret: str, username: str, password: str, user_agent: str = "RedditMarketingBot/1.0"):
        """Initialize Reddit poster with authentication"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.user_agent = user_agent
        
        # Initialize Reddit instance for posting
        self.reddit = None
        self.authenticated = False
        self.last_post_time = None
        
        # Safety settings
        self.min_post_delay = 600  # 10 minutes between posts (Reddit rate limit)
        self.max_daily_posts = 10  # Maximum posts per day
        self.require_approval = True  # Require manual approval before posting
        
        # Tracking
        self.daily_post_count = 0
        self.posted_today = []
        self.last_reset_date = datetime.now().date()
        
        # Posted content tracking (to avoid duplicates)
        self.posted_questions = set()
        self.posting_history = []
        
    async def initialize(self) -> bool:
        """Initialize and authenticate with Reddit"""
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                username=self.username,
                password=self.password,
                user_agent=self.user_agent,
                check_for_async=False
            )
            
            # Test authentication
            user = self.reddit.user.me()
            if user:
                self.authenticated = True
                print(f"✅ Reddit authenticated as u/{user.name}")
                print(f"   Karma: {user.comment_karma} comment, {user.link_karma} link")
                return True
            else:
                print("❌ Reddit authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ Reddit posting initialization failed: {str(e)}")
            self.authenticated = False
            return False
    
    def _reset_daily_counters(self):
        """Reset daily counters if it's a new day"""
        current_date = datetime.now().date()
        if current_date > self.last_reset_date:
            self.daily_post_count = 0
            self.posted_today = []
            self.last_reset_date = current_date
            print(f"🔄 Daily counters reset for {current_date}")
    
    def _can_post(self) -> Tuple[bool, str]:
        """Check if we can post based on rate limits and safety settings"""
        if not self.authenticated:
            return False, "Not authenticated with Reddit"
        
        # Reset daily counters if needed
        self._reset_daily_counters()
        
        # Check daily limit
        if self.daily_post_count >= self.max_daily_posts:
            return False, f"Daily posting limit reached ({self.max_daily_posts} posts)"
        
        # Check time since last post
        if self.last_post_time:
            time_since_last = datetime.now() - self.last_post_time
            if time_since_last.total_seconds() < self.min_post_delay:
                remaining = self.min_post_delay - time_since_last.total_seconds()
                return False, f"Rate limit: {remaining:.0f} seconds until next post allowed"
        
        return True, "Ready to post"
    
    def _is_duplicate_content(self, question_id: str, response: str) -> bool:
        """Check if we've already posted to this question or similar content"""
        # Check if we've posted to this exact question
        if question_id in self.posted_questions:
            return True
        
        # Check for similar response content (basic duplicate detection)
        response_words = set(response.lower().split())
        for history in self.posting_history[-20:]:  # Check last 20 posts
            history_words = set(history.get('response', '').lower().split())
            if len(response_words.intersection(history_words)) > len(response_words) * 0.7:
                return True  # 70% similarity threshold
        
        return False
    
    def _assess_content_quality(self, response: str, question: Dict[str, Any]) -> Tuple[bool, str, float]:
        """Assess if the response is high quality and suitable for posting"""
        score = 0.0
        issues = []
        
        # Length check (not too short, not too long)
        if len(response) < 20:
            issues.append("Response too short")
            score -= 0.3
        elif len(response) > 500:
            issues.append("Response too long")
            score -= 0.1
        else:
            score += 0.2
        
        # Check for helpful content indicators
        helpful_patterns = [
            r'\b(try|use|check out|consider|recommend)\b',
            r'\b(helps?|works?|useful|effective)\b',
            r'\b(experience|found|worked for me)\b'
        ]
        for pattern in helpful_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                score += 0.2
        
        # Check for promotional red flags
        promotional_patterns = [
            r'\b(buy|purchase|sale|discount|affiliate)\b',
            r'\b(click here|visit|sign up|register)\b',
            r'\b(guaranteed|amazing|incredible|revolutionary)\b'
        ]
        for pattern in promotional_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append("Contains promotional language")
                score -= 0.4
        
        # Check for natural language
        if "'" in response or response.count('!') <= 2:
            score += 0.1
        
        # Question relevance (basic check)
        question_words = set(question.get('title', '').lower().split())
        response_words = set(response.lower().split())
        overlap = len(question_words.intersection(response_words))
        if overlap >= 2:
            score += 0.2
        
        # Overall assessment
        is_suitable = score >= 0.3 and len(issues) == 0
        quality_msg = f"Quality score: {score:.2f}. Issues: {', '.join(issues) if issues else 'None'}"
        
        return is_suitable, quality_msg, score
    
    async def post_comment(self, question: Dict[str, Any], response: str, dry_run: bool = True) -> Dict[str, Any]:
        """Post a comment to a Reddit question"""
        result = {
            'success': False,
            'message': '',
            'question_id': question.get('id'),
            'question_title': question.get('title', '')[:50] + '...',
            'subreddit': question.get('subreddit'),
            'posted_at': None,
            'comment_url': None,
            'dry_run': dry_run
        }
        
        try:
            # Check if we can post
            can_post, reason = self._can_post()
            if not can_post:
                result['message'] = f"Cannot post: {reason}"
                return result
            
            # Check for duplicates
            if self._is_duplicate_content(question['id'], response):
                result['message'] = "Duplicate content detected, skipping"
                return result
            
            # Assess content quality
            is_suitable, quality_msg, quality_score = self._assess_content_quality(response, question)
            if not is_suitable:
                result['message'] = f"Content not suitable: {quality_msg}"
                return result
            
            # If this is a dry run, just simulate
            if dry_run:
                result['success'] = True
                result['message'] = f"✅ DRY RUN: Would post comment. {quality_msg}"
                result['posted_at'] = datetime.now().isoformat()
                return result
            
            # Get the Reddit submission
            if question.get('search_method') == 'mock':
                result['message'] = "Cannot post to mock questions (not real Reddit posts)"
                return result
            
            submission = self.reddit.submission(id=question['id'])
            
            # Add random delay to appear more human
            await asyncio.sleep(random.uniform(2, 8))
            
            # Post the comment
            comment = submission.reply(response)
            
            # Update tracking
            self.last_post_time = datetime.now()
            self.daily_post_count += 1
            self.posted_questions.add(question['id'])
            
            # Save to history
            post_record = {
                'timestamp': datetime.now().isoformat(),
                'question_id': question['id'],
                'question_title': question.get('title'),
                'subreddit': question.get('subreddit'),
                'response': response,
                'comment_id': comment.id,
                'comment_url': f"https://reddit.com{comment.permalink}",
                'quality_score': quality_score
            }
            self.posting_history.append(post_record)
            
            result['success'] = True
            result['message'] = "✅ Comment posted successfully"
            result['posted_at'] = datetime.now().isoformat()
            result['comment_url'] = f"https://reddit.com{comment.permalink}"
            
            print(f"✅ Posted comment to r/{question.get('subreddit')} - {comment.permalink}")
            
        except Exception as e:
            result['message'] = f"❌ Failed to post: {str(e)}"
            print(f"❌ Error posting comment: {str(e)}")
        
        return result
    
    async def post_multiple_comments(self, questions_with_responses: List[Dict[str, Any]], dry_run: bool = True) -> Dict[str, Any]:
        """Post comments to multiple questions with safety checks"""
        results = {
            'total_questions': len(questions_with_responses),
            'posted': 0,
            'skipped': 0,
            'failed': 0,
            'details': []
        }
        
        print(f"🚀 Starting to post {len(questions_with_responses)} comments (dry_run={dry_run})")
        
        for i, qa_pair in enumerate(questions_with_responses, 1):
            question = {
                'id': qa_pair.get('id'),
                'title': qa_pair.get('title'),
                'selftext': qa_pair.get('selftext'),
                'subreddit': qa_pair.get('subreddit'),
                'search_method': qa_pair.get('search_method')
            }
            response = qa_pair.get('ai_response', '')
            
            print(f"\n🔄 Processing {i}/{len(questions_with_responses)}: r/{question.get('subreddit')} - {question.get('title', '')[:50]}...")
            
            # Post the comment
            result = await self.post_comment(question, response, dry_run=dry_run)
            results['details'].append(result)
            
            if result['success']:
                results['posted'] += 1
                if not dry_run:
                    # Add delay between actual posts
                    delay = random.uniform(self.min_post_delay, self.min_post_delay + 300)  # 10-15 minutes
                    print(f"⏳ Waiting {delay/60:.1f} minutes before next post...")
                    await asyncio.sleep(delay)
            else:
                if 'duplicate' in result['message'].lower() or 'not suitable' in result['message'].lower():
                    results['skipped'] += 1
                else:
                    results['failed'] += 1
            
            print(f"   {result['message']}")
        
        return results
    
    def get_posting_stats(self) -> Dict[str, Any]:
        """Get current posting statistics"""
        self._reset_daily_counters()
        
        return {
            'authenticated': self.authenticated,
            'username': self.username if self.authenticated else None,
            'daily_posts': self.daily_post_count,
            'daily_limit': self.max_daily_posts,
            'total_posted': len(self.posting_history),
            'last_post': self.last_post_time.isoformat() if self.last_post_time else None,
            'can_post_now': self._can_post()[0],
            'next_post_available': (self.last_post_time + timedelta(seconds=self.min_post_delay)).isoformat() if self.last_post_time else 'Now'
        }
    
    def save_posting_history(self, filepath: str = "posting_history.json"):
        """Save posting history to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.posting_history, f, indent=2, default=str)
            print(f"✅ Posting history saved to {filepath}")
        except Exception as e:
            print(f"❌ Error saving posting history: {str(e)}")
    
    def load_posting_history(self, filepath: str = "posting_history.json"):
        """Load posting history from file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    self.posting_history = json.load(f)
                # Rebuild posted_questions set
                self.posted_questions = {post['question_id'] for post in self.posting_history}
                print(f"✅ Loaded {len(self.posting_history)} posts from history")
            else:
                print("ℹ️  No posting history file found, starting fresh")
        except Exception as e:
            print(f"❌ Error loading posting history: {str(e)}")