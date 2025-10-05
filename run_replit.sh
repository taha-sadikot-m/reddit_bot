#!/bin/bash

# Reddit Marketing Bot - Replit Setup Script
# This script sets up the environment and runs the application on Replit

echo "🚀 Setting up Reddit Marketing Bot on Replit..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env file exists, if not create from template
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.template .env
    echo "✅ Please edit .env file with your actual API keys"
fi

# Set Streamlit configuration for Replit
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOL
[server]
port = 8501
address = "0.0.0.0"
headless = true
fileWatcherType = "none"

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"
serverPort = 8501

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
EOL

echo "🎨 Streamlit configuration created"

# Run the enhanced Streamlit app
echo "🌟 Starting Reddit Marketing Bot..."
echo "📱 Your app will be available at: https://${REPL_SLUG}.${REPL_OWNER}.repl.co"
echo ""
echo "⚠️  Important: Remember to add your API keys in the sidebar!"
echo "   - Gemini API Key: Get from https://makersuite.google.com/app/apikey"
echo "   - Reddit API: Get from https://www.reddit.com/prefs/apps"
echo ""

# Start the application
streamlit run enhanced_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true --server.fileWatcherType none --browser.gatherUsageStats false
