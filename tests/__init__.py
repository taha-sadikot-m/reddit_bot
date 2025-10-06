"""
Tests Package - Reddit Marketing Bot
Comprehensive test suite for all components
"""

# Test configuration
TEST_CONFIG = {
    "test_business_description": """
    We offer a SaaS platform that helps small businesses manage their inventory efficiently. 
    Our tool provides real-time tracking, automated reordering, and detailed analytics. 
    Target customers are small to medium retail businesses looking to optimize their stock management.
    """,
    "mock_mode": True,  # Use mock data by default in tests
    "dry_run": True,   # Always dry run in tests
    "max_test_questions": 5,  # Limit questions in tests
    "test_timeout": 30  # Test timeout in seconds
}

__all__ = ['TEST_CONFIG']