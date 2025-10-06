"""
Configuration Management - Main Configuration File
Centralized configuration for Reddit Marketing Bot
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configurations
from .reddit_config import REDDIT_CONFIG
from .ai_config import AI_CONFIG
from .app_config import APP_CONFIG

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.reddit = REDDIT_CONFIG
        self.ai = AI_CONFIG
        self.app = APP_CONFIG
    
    def get_reddit_config(self) -> Dict[str, Any]:
        """Get Reddit API configuration"""
        return {
            "client_id": os.getenv("REDDIT_CLIENT_ID", self.reddit["client_id"]),
            "client_secret": os.getenv("REDDIT_CLIENT_SECRET", self.reddit["client_secret"]),
            "username": os.getenv("REDDIT_USERNAME", self.reddit["username"]),
            "password": os.getenv("REDDIT_PASSWORD", self.reddit["password"]),
            "user_agent": self.reddit["user_agent"]
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI API configuration"""
        return {
            "gemini_api_key": os.getenv("GEMINI_API_KEY", self.ai["gemini_api_key"]),
            "model_name": self.ai["model_name"],
            "temperature": self.ai["temperature"],
            "max_tokens": self.ai["max_tokens"]
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return self.app
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate all configurations"""
        validation = {}
        
        # Validate Reddit config
        reddit_config = self.get_reddit_config()
        validation["reddit"] = all([
            reddit_config["client_id"] and not reddit_config["client_id"].startswith("YOUR_"),
            reddit_config["client_secret"] and not reddit_config["client_secret"].startswith("YOUR_")
        ])
        
        # Validate AI config
        ai_config = self.get_ai_config()
        validation["ai"] = bool(
            ai_config["gemini_api_key"] and 
            not ai_config["gemini_api_key"].startswith("your-")
        )
        
        validation["overall"] = all(validation.values())
        
        return validation

# Create global config instance
config = Config()

# For backward compatibility
REDDIT_CONFIG = config.get_reddit_config()
AI_CONFIG = config.get_ai_config()
APP_CONFIG = config.get_app_config()

__all__ = ['config', 'REDDIT_CONFIG', 'AI_CONFIG', 'APP_CONFIG']