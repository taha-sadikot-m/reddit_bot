# AI API Configuration
# Configuration for AI services (Gemini, etc.)

AI_CONFIG = {
    "gemini_api_key": "your-gemini-api-key-here",  # Replace with your Gemini API key
    "model_name": "gemini-2.5-flash",  # Gemini model to use
    "temperature": 0.3,  # Creativity level (0.0 - 1.0)
    "max_tokens": 2048,  # Maximum response length
    "timeout": 30,  # Request timeout in seconds
    "retry_attempts": 3,  # Number of retry attempts on failure
    "rate_limit_delay": 1.0  # Delay between requests in seconds
}

# Instructions for AI API Setup:
# 1. Go to https://aistudio.google.com/app/apikey
# 2. Create a new API key
# 3. Copy the API key and replace the placeholder above
# 4. Set the GEMINI_API_KEY environment variable (recommended)
# 
# Environment Variable Setup:
# - Create a .env file in the project root
# - Add: GEMINI_API_KEY=your-actual-api-key-here
# - The bot will automatically use the environment variable