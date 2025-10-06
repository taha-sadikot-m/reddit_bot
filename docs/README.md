# Reddit Marketing Bot

A comprehensive AI-powered tool that finds relevant Reddit questions and generates human-like marketing responses for your business.

## 🚀 Features

- **AI Business Analysis**: Uses Google Gemini to analyze your business and understand your target audience
- **Smart Reddit Discovery**: Finds relevant questions across multiple subreddits using advanced search algorithms
- **Human-like Response Generation**: Creates contextual, helpful responses that naturally introduce your product
- **Quality Assessment**: Evaluates response quality with metrics for helpfulness, naturalness, and marketing subtlety
- **Beautiful UI**: Modern Streamlit interface with advanced features like favorites, analytics, and export options
- **Multiple Input Methods**: Text description or PDF document upload
- **Comprehensive Analytics**: Charts and insights about question performance and subreddit effectiveness

## 🛠️ Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get API Keys

#### Google Gemini API Key:
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

#### Reddit API Credentials:
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" for personal use
4. Fill in the form:
   - Name: Your app name
   - App type: Script
   - Description: Brief description
   - About URL: Leave blank
   - Redirect URI: `http://localhost:8080`
5. Copy the Client ID (under your app name) and Client Secret

### 3. Configure Environment

Copy `.env.template` to `.env` and fill in your API keys:

```bash
cp .env.template .env
```

Edit `.env` with your actual API keys:
```
GEMINI_API_KEY=your_actual_gemini_api_key
REDDIT_CLIENT_ID=your_actual_client_id
REDDIT_CLIENT_SECRET=your_actual_client_secret
```

### 4. Run the Application

#### Option 1: Enhanced Streamlit App (Recommended)
```bash
streamlit run enhanced_app.py
```

#### Option 2: Basic Streamlit App
```bash
streamlit run app.py
```

#### Option 3: Test Individual Components
```bash
python quick_test.py
```

## 📖 How to Use

### 1. **Configure APIs**
- Enter your Gemini API key and Reddit credentials in the sidebar
- Save the configuration

### 2. **Provide Business Information**
- Choose between text description or PDF upload
- Describe your product, target audience, and key benefits
- Be specific about what problems your product solves

### 3. **Customize Search Settings**
- Adjust number of questions to find (5-50)
- Select number of subreddits to search (3-20)
- Choose response style (Professional, Casual, Expert, Friendly, Technical)
- Set minimum upvotes and search timeframe

### 4. **Run Analysis**
- Click "Start AI Analysis"
- The AI will:
  - Analyze your business
  - Find relevant Reddit questions
  - Generate human-like responses
  - Provide quality metrics

### 5. **Review Results**
- Browse questions and AI-generated responses
- Filter and sort by relevance, upvotes, or date
- Add best responses to favorites
- Edit responses if needed
- Copy responses for use

### 6. **Use Analytics**
- View question score distributions
- Analyze subreddit performance
- Export data and reports
- Track analysis history

## 🎯 Best Practices

### Writing Effective Business Descriptions:

```
Example: We offer CloudStock Pro, a SaaS inventory management platform for small retail businesses. Our software provides:

• Real-time inventory tracking across multiple locations
• Automated reorder notifications based on sales patterns  
• Detailed analytics and reporting dashboards
• Integration with popular POS systems
• Mobile app for inventory checks

Target customers: Small retail businesses (5-50 employees) struggling with manual inventory, overstocking, or stockouts. Perfect for boutiques, electronics stores, sporting goods retailers looking to optimize inventory management and reduce costs.
```

### Response Guidelines:
- Responses are designed to be helpful first, promotional second
- Natural mentions of your product as one of several solutions
- Contextual advice that genuinely addresses the question
- Professional tone that matches Reddit community standards

## 📁 Project Structure

```
redditbot/
├── app.py                     # Basic Streamlit app
├── enhanced_app.py           # Advanced Streamlit app with full features
├── business_analyzer.py      # AI business analysis using LangChain + Gemini
├── reddit_analyzer.py        # Reddit API integration and question discovery
├── ai_response_generator.py  # AI response generation with quality metrics
├── workflow_manager.py       # LangGraph workflow orchestration
├── main.py                   # Original Reddit API client
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env.template            # Environment variables template
├── quick_test.py            # Component testing
└── README.md               # This file
```

## 🔧 Architecture

### Workflow Steps:
1. **Business Analysis** (LangChain + Gemini)
   - Analyzes business description
   - Identifies target audience and pain points
   - Suggests relevant subreddits and keywords

2. **Reddit Discovery** (PRAW + Custom Algorithms)
   - Searches multiple subreddits
   - Filters by relevance, score, and recency
   - Calculates relevance scores based on business context

3. **Response Generation** (LangChain + Gemini)
   - Creates contextual, helpful responses
   - Multiple response styles available
   - Natural product mentions without being salesy

4. **Quality Assessment**
   - Readability scoring
   - Helpfulness evaluation
   - Marketing subtlety analysis
   - Overall quality metrics

### Technologies Used:
- **AI/ML**: Google Gemini Pro, LangChain, LangGraph
- **Reddit API**: PRAW (Python Reddit API Wrapper)
- **UI**: Streamlit with custom CSS
- **Data**: Pandas, Plotly for analytics
- **Async**: AsyncIO for concurrent processing

## 🚨 Important Notes

### Rate Limits:
- Reddit API: ~60 requests per minute
- Gemini API: Varies by plan
- Built-in delays to respect limits

### Quality Control:
- All responses are AI-generated suggestions
- Review before posting to Reddit
- Ensure compliance with subreddit rules
- Use responses as starting points, not final posts

### Privacy:
- No data is stored externally
- All processing happens locally
- API keys stored only in your environment

## 🛡️ Legal & Ethical Guidelines

1. **Reddit Terms of Service**: Ensure all activities comply with Reddit's ToS
2. **Subreddit Rules**: Each subreddit has specific rules - always read and follow them
3. **Authentic Engagement**: Use responses as genuine help, not just promotion
4. **Disclosure**: Consider disclosing affiliation when appropriate
5. **Value First**: Always provide real value before any promotional content

## 🐛 Troubleshooting

### Common Issues:

**Import Errors:**
```bash
pip install --upgrade -r requirements.txt
```

**API Connection Issues:**
- Verify API keys are correct
- Check internet connection
- Ensure Reddit app is configured as "script" type

**No Questions Found:**
- Try broader business description
- Increase search parameters
- Check if subreddits exist and are accessible

**Poor Response Quality:**
- Provide more specific business description
- Try different response styles
- Include more context about target audience

## 📊 Performance Tips

1. **Optimize Search Parameters:**
   - Start with 10-15 questions to test
   - Gradually increase if results are good
   - Focus on 5-8 most relevant subreddits

2. **Improve Business Description:**
   - Include specific use cases
   - Mention target audience demographics
   - Describe key differentiators

3. **Response Customization:**
   - Experiment with different styles
   - Edit AI responses to match your voice
   - A/B test different approaches

## 🤝 Contributing

This is a complete, production-ready system. To extend functionality:

1. Add new response styles in `ai_response_generator.py`
2. Implement additional analytics in `enhanced_app.py`
3. Add new data sources beyond Reddit
4. Integrate with other AI models

## 📄 License

This project is for educational and business use. Ensure compliance with all API terms of service and platform guidelines.

---

**Happy Marketing! 🚀**
