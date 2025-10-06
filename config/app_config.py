# Application Configuration
# General application settings and defaults

APP_CONFIG = {
    # Default workflow settings
    "default_max_questions": 20,
    "default_subreddit_limit": 8,
    "default_response_style": "Casual",
    "default_min_upvotes": 5,
    "default_days_back": 7,
    "default_include_nsfw": False,
    
    # Posting settings
    "posting": {
        "dry_run_default": True,
        "auto_post_default": False,
        "min_post_delay": 600,  # 10 minutes in seconds
        "max_daily_posts": 10,
        "quality_threshold": 0.3,
        "require_approval": True
    },
    
    # Data storage settings
    "data": {
        "posting_history_file": "data/posting_history.json",
        "output_directory": "data/outputs",
        "backup_directory": "data/backups",
        "log_directory": "data/logs"
    },
    
    # Streamlit app settings
    "streamlit": {
        "page_title": "Reddit Marketing Bot Pro",
        "page_icon": "🤖",
        "layout": "wide",
        "sidebar_state": "expanded"
    },
    
    # Logging settings
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_enabled": True,
        "console_enabled": True
    },
    
    # Performance settings
    "performance": {
        "request_timeout": 30,
        "max_concurrent_requests": 3,
        "retry_attempts": 3,
        "backoff_factor": 2.0
    },
    
    # Safety settings
    "safety": {
        "enable_content_filtering": True,
        "enable_duplicate_detection": True,
        "enable_rate_limiting": True,
        "enable_quality_checks": True,
        "max_response_length": 500,
        "min_response_length": 20
    }
}

# Environment-specific overrides
DEVELOPMENT_CONFIG = {
    **APP_CONFIG,
    "posting": {
        **APP_CONFIG["posting"],
        "dry_run_default": True,
        "max_daily_posts": 5
    },
    "logging": {
        **APP_CONFIG["logging"],
        "level": "DEBUG"
    }
}

PRODUCTION_CONFIG = {
    **APP_CONFIG,
    "posting": {
        **APP_CONFIG["posting"],
        "dry_run_default": False,
        "require_approval": True
    },
    "logging": {
        **APP_CONFIG["logging"],
        "level": "INFO"
    }
}

# Export the appropriate config based on environment
import os
ENV = os.getenv("ENVIRONMENT", "development").lower()

if ENV == "production":
    APP_CONFIG = PRODUCTION_CONFIG
elif ENV == "development":
    APP_CONFIG = DEVELOPMENT_CONFIG

__all__ = ['APP_CONFIG', 'DEVELOPMENT_CONFIG', 'PRODUCTION_CONFIG']