"""
Reddit Marketing Bot - Core Package
Professional Reddit marketing automation with AI-powered response generation
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Core imports for easy access
from .business_analyzer import BusinessAnalyzer
from .reddit_analyzer import RedditAnalyzer
from .ai_response_generator import AIResponseGenerator
from .reddit_poster import RedditPoster
from .workflow_manager import WorkflowManager

__all__ = [
    'BusinessAnalyzer',
    'RedditAnalyzer', 
    'AIResponseGenerator',
    'RedditPoster',
    'WorkflowManager'
]