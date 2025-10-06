"""
Reddit Marketing Bot - Main Package
Professional Reddit marketing automation suite
"""

__version__ = "1.0.0"

# Import main components
from .core import (
    BusinessAnalyzer,
    RedditAnalyzer,
    AIResponseGenerator,
    RedditPoster,
    WorkflowManager
)

__all__ = [
    'BusinessAnalyzer',
    'RedditAnalyzer',
    'AIResponseGenerator', 
    'RedditPoster',
    'WorkflowManager'
]