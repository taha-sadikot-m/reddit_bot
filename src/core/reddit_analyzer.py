"""
Reddit Analyzer - Advanced Reddit search and question discovery
Uses Reddit API to find relevant questions based on business context
"""

import praw
import asyncio
from typing import List, Dict, Any, Optional
import time
from datetime import datetime, timedelta
import re
import random

class RedditAnalyzer:
    def __init__(self, client_id: str, client_secret: str, user_agent: str = "RedditMarketingBot/1.0"):
        """Initialize Reddit API client"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        
        # Try to initialize PRAW, fall back to mock mode if credentials are invalid
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
                check_for_async=False  # Suppress async warnings
            )
            # Test the connection
            self.reddit.auth.limits
            self.use_mock_data = False
            print("✅ Reddit API connected successfully")
        except Exception as e:
            print(f"⚠️  Reddit API connection failed: {str(e)}")
            print("🔄 Using mock data for demonstration...")
            self.reddit = None
            self.use_mock_data = True
        
        # Mock data for when Reddit API is not available
        self.mock_questions = [
            {
                'id': 'mock1',
                'title': 'Looking for a good project management tool for small team',
                'selftext': 'Hey everyone! I run a small startup with 5 people and we\'re struggling to keep track of tasks and deadlines. We\'ve tried spreadsheets but it gets messy. Looking for something simple and affordable. Any recommendations?',
                'subreddit': 'entrepreneur',
                'score': 25,
                'num_comments': 12,
                'created_utc': 1640995200,
                'url': 'https://reddit.com/r/entrepreneur/mock1',
                'author': 'startup_founder',
                'relevance_score': 0.85,
                'search_method': 'mock',
                'flair': 'Question'
            },
            {
                'id': 'mock2', 
                'title': 'Best tools for automating repetitive business tasks?',
                'selftext': 'I spend way too much time on data entry, scheduling, and follow-ups. It\'s killing my productivity. Does anyone know of good automation tools? I\'m not super technical but willing to learn.',
                'subreddit': 'smallbusiness',
                'score': 45,
                'num_comments': 23,
                'created_utc': 1640995200,
                'url': 'https://reddit.com/r/smallbusiness/mock2',
                'author': 'busy_entrepreneur',
                'relevance_score': 0.92,
                'search_method': 'mock',
                'flair': 'Advice'
            },
            {
                'id': 'mock3',
                'title': 'Struggling with team communication and task tracking',
                'selftext': 'Our team is growing and we\'re having trouble staying organized. People miss deadlines, forget tasks, and communication is scattered across email, Slack, and texts. Need a better system.',
                'subreddit': 'productivity',
                'score': 18,
                'num_comments': 8,
                'created_utc': 1640995200,
                'url': 'https://reddit.com/r/productivity/mock3',
                'author': 'team_leader',
                'relevance_score': 0.78,
                'search_method': 'mock',
                'flair': None
            }
        ]
        
        # Default subreddits for various business categories
        self.default_subreddits = {
            'business': ['entrepreneur', 'smallbusiness', 'business', 'startups', 'marketing'],
            'technology': ['technology', 'software', 'programming', 'webdev', 'saas'],
            'productivity': ['productivity', 'getmotivated', 'lifehacks', 'organization'],
            'finance': ['personalfinance', 'investing', 'financialplanning', 'money'],
            'ecommerce': ['ecommerce', 'shopify', 'amazon', 'dropshipping', 'onlinebusiness'],
            'health': ['health', 'fitness', 'nutrition', 'wellness', 'mentalhealth'],
            'education': ['education', 'learnprogramming', 'studytips', 'university'],
            'general': ['askreddit', 'nostupidquestions', 'advice', 'lifeprotips']
        }

    async def find_relevant_questions(
        self, 
        business_info: Dict[str, Any], 
        max_questions: int = 20,
        subreddit_limit: int = 8,
        min_upvotes: int = 5,
        days_back: int = 7,
        include_nsfw: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find relevant questions across multiple subreddits
        
        Args:
            business_info: Business analysis results
            max_questions: Maximum number of questions to return
            subreddit_limit: Maximum number of subreddits to search
            min_upvotes: Minimum upvotes for questions
            days_back: How many days back to search
            include_nsfw: Whether to include NSFW subreddits
            
        Returns:
            List of relevant questions with metadata
        """
        try:
            # If using mock data (Reddit API not available), return mock questions
            if self.use_mock_data:
                print("📋 Using mock data for demonstration (Reddit API not connected)")
                # Filter and score mock questions based on business info
                scored_questions = []
                for question in self.mock_questions:
                    # Calculate relevance score for mock questions
                    search_terms = self._generate_search_terms(business_info)
                    relevance_score = self._calculate_mock_relevance_score(question, search_terms, business_info)
                    question['relevance_score'] = relevance_score
                    scored_questions.append(question)
                
                # Sort by relevance and return top questions
                sorted_questions = sorted(scored_questions, key=lambda x: x.get('relevance_score', 0), reverse=True)
                return sorted_questions[:max_questions]
            
            # Get search parameters for real Reddit API
            subreddits = self._get_target_subreddits(business_info, subreddit_limit)
            search_terms = self._generate_search_terms(business_info)
            
            all_questions = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            print(f"Searching {len(subreddits)} subreddits for relevant questions...")
            
            for subreddit_name in subreddits:
                try:
                    print(f"Searching r/{subreddit_name}...")
                    questions = await self._search_subreddit(
                        subreddit_name=subreddit_name,
                        search_terms=search_terms,
                        business_info=business_info,
                        min_upvotes=min_upvotes,
                        cutoff_date=cutoff_date,
                        include_nsfw=include_nsfw
                    )
                    all_questions.extend(questions)
                    
                    # Add delay to respect rate limits
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"Error searching r/{subreddit_name}: {str(e)}")
                    continue
            
            # Sort by relevance score and return top questions
            sorted_questions = sorted(all_questions, key=lambda x: x.get('relevance_score', 0), reverse=True)
            return sorted_questions[:max_questions]
            
        except Exception as e:
            print(f"Error in find_relevant_questions: {str(e)}")
            return []

    def _get_target_subreddits(self, business_info: Dict[str, Any], limit: int) -> List[str]:
        """Get target subreddits for searching"""
        # Start with recommended subreddits from business analysis
        target_subreddits = business_info.get('recommended_subreddits', [])
        
        print(f"🔍 Debug: Initial subreddits from business analysis: {target_subreddits}")
        
        # Add category-specific subreddits based on industry
        industry = business_info.get('industry_category', '').lower()
        keywords = [kw.lower() for kw in business_info.get('keywords', [])]
        
        print(f"🔍 Debug: Industry: {industry}")
        print(f"🔍 Debug: Keywords: {keywords}")
        
        # Map industry and keywords to subreddit categories
        for category, subreddits in self.default_subreddits.items():
            should_add = False
            
            if category in industry:
                should_add = True
            elif category == 'technology' and any(keyword in industry for keyword in ['tech', 'software', 'saas', 'platform', 'app']):
                should_add = True
            elif category == 'business' and any(keyword in industry for keyword in ['business', 'startup', 'company', 'service']):
                should_add = True
            elif category == 'productivity' and any(keyword in industry for keyword in ['productivity', 'efficiency', 'management', 'organization']):
                should_add = True
            elif category == 'ecommerce' and any(keyword in industry for keyword in ['retail', 'inventory', 'sales', 'commerce']):
                should_add = True
            
            if should_add:
                target_subreddits.extend(subreddits)
                print(f"🔍 Debug: Added {category} subreddits: {subreddits}")
        
        # If still no subreddits, add default business subreddits
        if not target_subreddits:
            print("⚠️  No subreddits found, adding default business subreddits")
            target_subreddits = self.default_subreddits['business'] + self.default_subreddits['general']
        
        # Remove duplicates and limit
        unique_subreddits = list(dict.fromkeys(target_subreddits))  # Preserves order
        final_subreddits = unique_subreddits[:limit]
        
        print(f"🎯 Final target subreddits ({len(final_subreddits)}): {final_subreddits}")
        
        return final_subreddits

    def _search_subreddit_sync(
        self,
        subreddit_name: str,
        search_terms: List[str],
        business_info: Dict[str, Any],
        min_upvotes: int,
        cutoff_date: datetime,
        include_nsfw: bool
    ) -> List[Dict[str, Any]]:
        """Synchronous helper to search a specific subreddit for relevant questions"""
        questions = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Skip NSFW subreddits if not included
            if not include_nsfw and subreddit.over18:
                return questions
            
            # Search recent posts
            search_methods = [
                ('new', subreddit.new(limit=100)),
                ('hot', subreddit.hot(limit=50)),
                ('rising', subreddit.rising(limit=25))
            ]
            
            for method_name, posts in search_methods:
                try:
                    for post in posts:
                        # Check if post is recent enough
                        post_date = datetime.fromtimestamp(post.created_utc)
                        if post_date < cutoff_date:
                            continue
                        
                        # Enhanced filtering for quality posts
                        if not self._is_quality_post(post, min_upvotes):
                            continue
                        
                        # Calculate relevance score
                        relevance_score = self._calculate_relevance_score(post, search_terms, business_info)
                        
                        if relevance_score > 0.5:  # Higher threshold for better quality
                            question_data = {
                                'id': post.id,
                                'title': post.title,
                                'selftext': post.selftext,
                                'subreddit': subreddit_name,
                                'score': post.score,
                                'num_comments': post.num_comments,
                                'created_utc': post.created_utc,
                                'url': f"https://reddit.com{post.permalink}",
                                'author': str(post.author) if post.author else '[deleted]',
                                'relevance_score': relevance_score,
                                'search_method': method_name,
                                'flair': post.link_flair_text if post.link_flair_text else None
                            }
                            questions.append(question_data)
                        
                        # Respect rate limits
                        time.sleep(0.1)
                        
                except Exception as e:
                    print(f"Error in search method {method_name}: {str(e)}")
                    continue
            
            # Also search with specific search terms
            for term in search_terms[:3]:  # Limit to top 3 search terms
                try:
                    search_results = subreddit.search(term, sort='relevance', time_filter='month', limit=20)
                    
                    for post in search_results:
                        post_date = datetime.fromtimestamp(post.created_utc)
                        if (post_date >= cutoff_date and 
                            self._is_quality_post(post, min_upvotes)):
                            
                            # Check if we already have this post
                            if not any(q['id'] == post.id for q in questions):
                                relevance_score = self._calculate_relevance_score(post, search_terms, business_info)
                                
                                if relevance_score > 0.5:
                                    question_data = {
                                        'id': post.id,
                                        'title': post.title,
                                        'selftext': post.selftext,
                                        'subreddit': subreddit_name,
                                        'score': post.score,
                                        'num_comments': post.num_comments,
                                        'created_utc': post.created_utc,
                                        'url': f"https://reddit.com{post.permalink}",
                                        'author': str(post.author) if post.author else '[deleted]',
                                        'relevance_score': relevance_score,
                                        'search_method': f'search_{term}',
                                        'flair': post.link_flair_text if post.link_flair_text else None
                                    }
                                    questions.append(question_data)
                    
                    time.sleep(1)  # Rate limiting for search
                    
                except Exception as e:
                    print(f"Error searching for term '{term}': {str(e)}")
                    continue
            
        except Exception as e:
            print(f"Error accessing subreddit r/{subreddit_name}: {str(e)}")
        
        return questions

    async def _search_subreddit(
        self,
        subreddit_name: str,
        search_terms: List[str],
        business_info: Dict[str, Any],
        min_upvotes: int,
        cutoff_date: datetime,
        include_nsfw: bool
    ) -> List[Dict[str, Any]]:
        """Async wrapper for searching a specific subreddit"""
        # Use asyncio.to_thread to run the synchronous PRAW code in a thread pool
        return await asyncio.to_thread(
            self._search_subreddit_sync,
            subreddit_name,
            search_terms,
            business_info,
            min_upvotes,
            cutoff_date,
            include_nsfw
        )

    def _generate_search_terms(self, business_info: Dict[str, Any]) -> List[str]:
        """Generate marketing-focused search terms based on business information"""
        search_terms = []
        
        # Priority 1: High-intent purchase/recommendation terms
        high_intent_terms = [
            'best tool for', 'recommend tool', 'looking for software', 'need solution',
            'what tool should', 'any good tools', 'help me find', 'suggestions for tools'
        ]
        search_terms.extend(high_intent_terms)
        
        # Priority 2: Problem-seeking terms combined with keywords
        keywords = business_info.get('keywords', [])
        problem_prefixes = ['struggling with', 'having trouble with', 'need help with', 'looking for help with']
        for keyword in keywords[:5]:  # Top 5 keywords only
            search_terms.append(keyword)
            for prefix in problem_prefixes[:2]:  # Limit combinations
                search_terms.append(f"{prefix} {keyword}")
        
        # Priority 3: Pain points as direct search terms
        pain_points = business_info.get('pain_points_solved', [])
        for pain_point in pain_points[:3]:  # Top 3 pain points
            # Use the pain point directly if it's concise
            if len(pain_point.split()) <= 4:
                search_terms.append(pain_point.lower())
            else:
                # Extract key phrases
                words = re.findall(r'\b\w{4,}\b', pain_point.lower())  # 4+ letter words
                search_terms.extend(words[:3])
        
        # Priority 4: Solution-seeking terms
        solution_terms = [
            'alternative to', 'better than', 'replacement for', 'similar to',
            'free alternative', 'open source', 'budget friendly'
        ]
        search_terms.extend(solution_terms)
        
        # Priority 5: Question indicators for natural opportunities
        question_terms = [
            'how do i', 'what is the best', 'can anyone recommend', 
            'does anyone know', 'has anyone tried', 'what do you use'
        ]
        search_terms.extend(question_terms)
        
        # Clean, deduplicate, and prioritize
        cleaned_terms = []
        for term in search_terms:
            term = re.sub(r'[^a-zA-Z0-9\s]', '', str(term).lower()).strip()
            if len(term) > 2 and term not in cleaned_terms:
                cleaned_terms.append(term)
        
        return cleaned_terms[:25]  # Increased limit for better coverage

    def _calculate_relevance_score(self, post, search_terms: List[str], business_info: Dict[str, Any]) -> float:
        """Calculate relevance score for a Reddit post with focus on marketing opportunities"""
        score = 0.0
        
        # Combine title and text for analysis
        full_text = f"{post.title} {post.selftext}".lower()
        title_text = post.title.lower()
        
        # HIGH VALUE: Direct problem/solution seeking (best marketing opportunities)
        high_value_patterns = [
            'looking for', 'need help with', 'best tool for', 'recommend', 'suggestions for',
            'what should i use', 'any good', 'help me find', 'trying to find',
            'does anyone know', 'what do you use for', 'best way to'
        ]
        for pattern in high_value_patterns:
            if pattern in full_text:
                score += 0.8
                if pattern in title_text:  # Even higher if in title
                    score += 0.4
        
        # MEDIUM VALUE: Problem descriptions (good opportunities)
        problem_patterns = [
            'struggling with', 'having trouble', 'can\'t figure out', 'frustrated with',
            'stuck on', 'difficult to', 'challenge with', 'issue with', 'problem with'
        ]
        for pattern in problem_patterns:
            if pattern in full_text:
                score += 0.6
        
        # Pain point matching (very high weight for exact matches)
        pain_points = business_info.get('pain_points_solved', [])
        for pain_point in pain_points:
            pain_words = re.findall(r'\b\w+\b', pain_point.lower())
            for word in pain_words:
                if len(word) > 3 and word in full_text:
                    score += 0.5
                    if word in title_text:
                        score += 0.3  # Bonus for title matches
        
        # Keyword matching with context awareness
        keywords = [kw.lower() for kw in business_info.get('keywords', [])]
        for keyword in keywords:
            if keyword in full_text:
                score += 0.4
                # Check if keyword appears in problem-seeking context
                context_indicators = ['for ' + keyword, keyword + ' tool', keyword + ' solution', 
                                    'good ' + keyword, 'best ' + keyword]
                for context in context_indicators:
                    if context in full_text:
                        score += 0.3
        
        # Post engagement quality (higher engagement = better opportunity)
        engagement_score = (post.score * 0.01) + (post.num_comments * 0.02)
        score += min(engagement_score, 0.5)  # Cap engagement bonus
        
        # Post length quality (substantial posts are better)
        if 50 <= len(post.selftext) <= 500:  # Sweet spot for detailed but not overwhelming
            score += 0.2
        elif len(post.selftext) > 500:
            score += 0.1  # Good but might be too long
        
        # Time sensitivity bonus (recent posts are better)
        post_age_hours = (datetime.now().timestamp() - post.created_utc) / 3600
        if post_age_hours < 24:
            score += 0.3
        elif post_age_hours < 72:
            score += 0.1
        
        # NEGATIVE indicators (reduce score significantly)
        negative_terms = [
            'joke', 'meme', 'funny', 'lol', 'troll', 'shitpost', 'circlejerk',
            'rant', 'venting', 'unpopular opinion', 'change my mind', 'roast me'
        ]
        for term in negative_terms:
            if term in full_text:
                score -= 0.5
        
        # Avoid highly promotional posts (already solved)
        promo_indicators = ['my product', 'our solution', 'check out', 'affiliate', 'discount code']
        for indicator in promo_indicators:
            if indicator in full_text:
                score -= 0.8
        
        # Bonus for specific, actionable questions
        if '?' in post.title:  # Direct questions are great
            score += 0.2
        
        # Normalize and return score
        return max(0.0, min(score, 3.0))
    
    def _calculate_mock_relevance_score(self, question: Dict[str, Any], search_terms: List[str], business_info: Dict[str, Any]) -> float:
        """Calculate relevance score for mock questions"""
        score = 0.0
        
        # Combine title and text for analysis
        full_text = f"{question['title']} {question['selftext']}".lower()
        title_text = question['title'].lower()
        
        # Check for high-value patterns
        high_value_patterns = [
            'looking for', 'need help with', 'best tool for', 'recommend', 'suggestions for',
            'what should i use', 'any good', 'help me find', 'trying to find'
        ]
        for pattern in high_value_patterns:
            if pattern in full_text:
                score += 0.8
                if pattern in title_text:
                    score += 0.4
        
        # Pain point matching
        pain_points = business_info.get('pain_points_solved', [])
        for pain_point in pain_points:
            pain_words = re.findall(r'\b\w+\b', pain_point.lower())
            for word in pain_words:
                if len(word) > 3 and word in full_text:
                    score += 0.5
                    if word in title_text:
                        score += 0.3
        
        # Keyword matching
        keywords = [kw.lower() for kw in business_info.get('keywords', [])]
        for keyword in keywords:
            if keyword in full_text:
                score += 0.4
        
        # Base score for mock questions (they're pre-selected to be relevant)
        score += 0.6
        
        return max(0.0, min(score, 3.0))

    def get_subreddit_info(self, subreddit_name: str) -> Dict[str, Any]:
        """Get information about a specific subreddit"""
        if self.use_mock_data:
            # Return mock subreddit info
            return {
                'name': subreddit_name,
                'title': f"r/{subreddit_name}",
                'description': f"Mock description for r/{subreddit_name}",
                'subscribers': 100000,
                'over18': False,
                'created_utc': 1640995200,
                'public_description': f"A community for {subreddit_name} discussions"
            }
        
        try:
            if not self.reddit:
                return {}
            subreddit = self.reddit.subreddit(subreddit_name)
            return {
                'name': subreddit.display_name,
                'title': subreddit.title,
                'description': subreddit.description,
                'subscribers': subreddit.subscribers,
                'over18': subreddit.over18,
                'created_utc': subreddit.created_utc,
                'public_description': subreddit.public_description
            }
        except Exception as e:
            print(f"Error getting subreddit info for r/{subreddit_name}: {str(e)}")
            return {}

    def validate_subreddits(self, subreddit_names: List[str]) -> List[str]:
        """Validate that subreddits exist and are accessible"""
        valid_subreddits = []
        
        for name in subreddit_names:
            try:
                subreddit = self.reddit.subreddit(name)
                # Try to access a property to validate
                _ = subreddit.subscribers
                valid_subreddits.append(name)
            except Exception as e:
                print(f"Subreddit r/{name} is not accessible: {str(e)}")
                continue
        
        return valid_subreddits

    async def get_trending_topics(self, subreddit_names: List[str]) -> Dict[str, List[str]]:
        """Get trending topics from specified subreddits"""
        trending_topics = {}
        
        for subreddit_name in subreddit_names:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                hot_posts = list(subreddit.hot(limit=25))
                
                # Extract common words from titles
                titles = [post.title.lower() for post in hot_posts]
                all_words = []
                for title in titles:
                    words = re.findall(r'\b\w+\b', title)
                    all_words.extend([w for w in words if len(w) > 3])
                
                # Count word frequency
                word_count = {}
                for word in all_words:
                    word_count[word] = word_count.get(word, 0) + 1
                
                # Get top trending words
                trending_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
                trending_topics[subreddit_name] = [word for word, count in trending_words[:10]]
                
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error getting trending topics for r/{subreddit_name}: {str(e)}")
                trending_topics[subreddit_name] = []
        
        return trending_topics
    
    def _is_quality_post(self, post, min_upvotes: int) -> bool:
        """Check if post meets quality criteria for marketing opportunities"""
        # Basic requirements
        if (post.score < min_upvotes or 
            not post.is_self or  # Only self posts (text posts)
            len(post.selftext) < 20):  # Must have substantial text
            return False
        
        # Check for spam indicators
        full_text = f"{post.title} {post.selftext}".lower()
        spam_indicators = [
            'buy now', 'click here', 'limited time', 'act fast', 'guaranteed',
            'make money fast', 'work from home', 'get rich', 'free money'
        ]
        for spam in spam_indicators:
            if spam in full_text:
                return False
        
        # Avoid deleted/removed content
        if post.selftext in ['[deleted]', '[removed]', '']:
            return False
        
        # Avoid posts that are too short or too long
        if len(post.selftext) > 2000:  # Probably too long for good engagement
            return False
        
        # Must be seeking help/advice/recommendations
        help_seeking_patterns = [
            '?', 'help', 'advice', 'recommend', 'suggest', 'looking for',
            'need', 'how to', 'best way', 'what should', 'any ideas'
        ]
        if not any(pattern in full_text for pattern in help_seeking_patterns):
            return False
        
        return True
