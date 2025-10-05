"""
Replit-Optimized Version of the Reddit Marketing Bot
Configured specifically for Replit deployment with enhanced error handling
"""

import streamlit as st
import os
import sys
import asyncio
import pandas as pd
from datetime import datetime
import json
import io
import time
from typing import List, Dict, Any, Optional

# Configure for Replit environment
if 'REPL_SLUG' in os.environ:
    st.set_page_config(
        page_title="Reddit Marketing AI Bot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/yourusername/reddit-marketing-bot',
            'Report a bug': "https://github.com/yourusername/reddit-marketing-bot/issues",
            'About': "# Reddit Marketing AI Bot\nPowered by AI to find and respond to Reddit questions!"
        }
    )
else:
    st.set_page_config(
        page_title="Reddit Marketing AI Bot", 
        page_icon="🤖", 
        layout="wide"
    )

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import with error handling for Replit
def safe_import():
    """Safely import modules with helpful error messages"""
    global PyPDF2, RedditAnalyzer, AIResponseGenerator, BusinessAnalyzer, WorkflowManager
    missing_modules = []
    
    try:
        import PyPDF2
    except ImportError:
        missing_modules.append("PyPDF2")
        PyPDF2 = None
    
    try:
        from reddit_analyzer import RedditAnalyzer
        from ai_response_generator import AIResponseGenerator  
        from business_analyzer import BusinessAnalyzer
        from workflow_manager import WorkflowManager
    except ImportError as e:
        st.error(f"""
        🚨 **Module Import Error**
        
        Could not import required modules: {str(e)}
        
        **For Replit users:**
        1. Make sure all Python files are uploaded
        2. Check that requirements.txt is properly configured
        3. Try refreshing the Replit environment
        
        **Files needed:**
        - business_analyzer.py
        - reddit_analyzer.py  
        - ai_response_generator.py
        - workflow_manager.py
        """)
        st.stop()
    
    if missing_modules:
        st.warning(f"""
        ⚠️ **Optional modules missing:** {', '.join(missing_modules)}
        
        Some features may be limited. To install:
        ```bash
        pip install {' '.join(missing_modules)}
        ```
        """)

# Safe import
safe_import()

# Enhanced CSS optimized for Replit
st.markdown("""
<style>
    /* Replit-optimized styling */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF4B4B, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .replit-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.5rem;
    }
    
    .setup-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .api-config-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #2d3748;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #38a169;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .info-card {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        color: #2d3748;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #FF4B4B, #FF6B6B);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(255, 75, 75, 0.3);
    }
    
    /* Mobile optimization for Replit */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .setup-card, .api-config-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    # Header with Replit badge
    st.markdown('<h1 class="main-header">🤖 Reddit Marketing AI Bot</h1>', unsafe_allow_html=True)
    
    # Replit environment indicator
    if 'REPL_SLUG' in os.environ:
        st.markdown(f'''
        <div style="text-align: center;">
            <span class="replit-badge">🚀 Running on Replit</span>
            <span class="replit-badge">📱 Repl: {os.environ.get("REPL_SLUG", "Unknown")}</span>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 1.3rem; margin-bottom: 2rem;">'
        'Find perfect Reddit questions and generate human-like marketing responses with AI'
        '</p>', 
        unsafe_allow_html=True
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Check if this is first run
    if not st.session_state.get('setup_complete', False):
        show_initial_setup()
    else:
        # Main application interface
        configure_sidebar()
        
        if not st.session_state.get('api_configured', False):
            show_api_configuration()
        else:
            show_main_interface()

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'workflow_results': None,
        'business_info': None,
        'processing': False,
        'api_configured': False,
        'setup_complete': False,
        'favorites': [],
        'analysis_history': [],
        'gemini_api_key': '',
        'reddit_client_id': '',
        'reddit_client_secret': '',
        'max_questions': 15,
        'subreddit_limit': 8,
        'response_style': 'Professional',
        'include_nsfw': False,
        'min_upvotes': 5,
        'days_back': 7
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_initial_setup():
    """Show initial setup screen for first-time users"""
    st.markdown("""
    <div class="setup-card">
        <h2>🎉 Welcome to Reddit Marketing AI Bot!</h2>
        <p>This powerful tool helps you find relevant Reddit questions and generate human-like responses that naturally promote your business.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 What this bot does:
        
        1. **🧠 AI Business Analysis** - Understands your product and audience
        2. **🔍 Smart Reddit Search** - Finds relevant questions across subreddits  
        3. **🤖 Response Generation** - Creates helpful, human-like answers
        4. **📊 Quality Scoring** - Evaluates response effectiveness
        5. **⭐ Management Tools** - Save favorites, track analytics
        """)
    
    with col2:
        st.markdown("""
        ### 🔑 What you'll need:
        
        1. **Google Gemini API Key** (Free tier available)
           - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
           
        2. **Reddit API Credentials** (Free)
           - Get from [Reddit Apps](https://www.reddit.com/prefs/apps)
           
        3. **Your Business Description**
           - Product details, target audience, benefits
        """)
    
    st.markdown("""
    <div class="info-card">
        <h4>💡 Pro Tips for Best Results:</h4>
        <ul>
            <li><strong>Be Specific:</strong> Detailed business descriptions yield better questions</li>
            <li><strong>Start Small:</strong> Test with 10-15 questions first</li>
            <li><strong>Review Responses:</strong> Always review AI responses before using</li>
            <li><strong>Follow Rules:</strong> Each subreddit has specific guidelines</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 Let's Get Started!", type="primary", use_container_width=True):
        st.session_state.setup_complete = True
        st.rerun()

def show_api_configuration():
    """Show API configuration screen"""
    st.markdown("""
    <div class="api-config-card">
        <h2>🔑 API Configuration</h2>
        <p>Configure your API keys to unlock the full power of the Reddit Marketing Bot.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Google Gemini API")
        gemini_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.get('gemini_api_key', ''),
            help="Get your free API key from Google AI Studio",
            placeholder="Enter your Gemini API key here..."
        )
        
        if st.button("🔗 Get Gemini API Key", use_container_width=True):
            st.markdown("[Click here to get your Gemini API key](https://makersuite.google.com/app/apikey)")
    
    with col2:
        st.markdown("### 📱 Reddit API")
        reddit_client_id = st.text_input(
            "Reddit Client ID",
            value=st.session_state.get('reddit_client_id', ''),
            help="Get from Reddit Apps page",
            placeholder="Enter your Reddit Client ID..."
        )
        
        reddit_client_secret = st.text_input(
            "Reddit Client Secret",
            type="password", 
            value=st.session_state.get('reddit_client_secret', ''),
            help="Get from Reddit Apps page",
            placeholder="Enter your Reddit Client Secret..."
        )
        
        if st.button("🔗 Get Reddit API Keys", use_container_width=True):
            st.markdown("[Click here to create a Reddit app](https://www.reddit.com/prefs/apps)")
    
    # Save configuration
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("💾 Save API Configuration", type="primary", use_container_width=True):
            if gemini_key and reddit_client_id and reddit_client_secret:
                st.session_state.gemini_api_key = gemini_key
                st.session_state.reddit_client_id = reddit_client_id
                st.session_state.reddit_client_secret = reddit_client_secret
                st.session_state.api_configured = True
                
                st.success("✅ API configuration saved successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Please fill in all API credentials")
    
    # Help section
    with st.expander("🆘 Need Help Getting API Keys?"):
        st.markdown("""
        ### 🤖 Google Gemini API Key:
        1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API Key"
        4. Copy the generated key and paste above
        
        ### 📱 Reddit API Credentials:
        1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
        2. Click "Create App" or "Create Another App"
        3. Choose "script" for personal use
        4. Fill in the form:
           - **Name:** Your app name (e.g., "My Marketing Bot")
           - **App type:** Script
           - **Description:** Brief description
           - **Redirect URI:** `http://localhost:8080`
        5. After creating, copy:
           - **Client ID:** The string under your app name
           - **Client Secret:** The "secret" field
        
        ### 🔒 Security Notes:
        - API keys are stored only in your browser session
        - Never share your API keys publicly
        - You can revoke keys anytime from the respective platforms
        """)

def configure_sidebar():
    """Configure sidebar with settings"""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # Quick status
        if st.session_state.get('api_configured'):
            st.success("✅ APIs Configured")
        else:
            st.error("❌ APIs Not Configured")
        
        # Search parameters
        with st.expander("🎯 Search Parameters", expanded=True):
            st.session_state.max_questions = st.slider(
                "Max Questions", 5, 50, st.session_state.get('max_questions', 15)
            )
            st.session_state.subreddit_limit = st.slider(
                "Subreddit Limit", 3, 20, st.session_state.get('subreddit_limit', 8)
            )
            st.session_state.response_style = st.selectbox(
                "Response Style",
                ["Professional", "Casual", "Expert", "Friendly", "Technical"],
                index=["Professional", "Casual", "Expert", "Friendly", "Technical"].index(
                    st.session_state.get('response_style', 'Professional')
                )
            )
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            st.session_state.include_nsfw = st.checkbox(
                "Include NSFW subreddits", 
                value=st.session_state.get('include_nsfw', False)
            )
            st.session_state.min_upvotes = st.number_input(
                "Minimum upvotes", 
                min_value=0, 
                value=st.session_state.get('min_upvotes', 5)
            )
            st.session_state.days_back = st.slider(
                "Days back to search", 
                1, 30, 
                st.session_state.get('days_back', 7)
            )
        
        # Reset configuration
        st.markdown("---")
        if st.button("🔄 Reset API Config"):
            for key in ['gemini_api_key', 'reddit_client_id', 'reddit_client_secret', 'api_configured']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

def show_main_interface():
    """Show main application interface"""
    tab1, tab2, tab3 = st.tabs(["📝 Analysis", "📊 Results", "⭐ Favorites"])
    
    with tab1:
        show_analysis_tab()
    
    with tab2:
        show_results_tab()
    
    with tab3:
        show_favorites_tab()

def show_analysis_tab():
    """Show analysis input tab"""
    st.markdown("## 📝 Business Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input method
        input_method = st.radio(
            "Choose input method:",
            ["✍️ Text Description", "📄 PDF Upload"],
            horizontal=True
        )
        
        business_description = ""
        
        if input_method == "✍️ Text Description":
            business_description = st.text_area(
                "Describe your business:",
                height=300,
                placeholder=get_example_description(),
                help="Be specific about your product, target audience, and key benefits"
            )
        
        elif PyPDF2 and input_method == "📄 PDF Upload":
            uploaded_file = st.file_uploader("Upload PDF", type="pdf")
            if uploaded_file:
                business_description = extract_pdf_text(uploaded_file)
        
        elif not PyPDF2:
            st.warning("PDF upload not available. Please use text description.")
        
        # Analysis button
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            if business_description:
                run_analysis(business_description)
            else:
                st.error("Please provide business information")
    
    with col2:
        show_workflow_info()

def get_example_description():
    """Get example business description"""
    return """Example: CloudStock Pro is a SaaS inventory management platform for small retail businesses.

Key Features:
• Real-time inventory tracking across multiple locations
• Automated reorder notifications based on sales patterns
• Analytics dashboard with customizable reports  
• Integration with popular POS systems (Square, Shopify)
• Mobile app for on-the-go management

Target Audience: Small retail businesses (5-50 employees) struggling with manual inventory processes, stockouts, or overstock situations.

Perfect for: Boutiques, electronics stores, sporting goods retailers, bookstores.

Benefits: 40% reduction in stockouts, 25% decrease in excess inventory, 3-5 hours saved weekly."""

def extract_pdf_text(uploaded_file):
    """Extract text from PDF file"""
    if not PyPDF2:
        st.error("PDF processing not available")
        return ""
    
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        if text:
            st.success(f"✅ PDF processed! Extracted {len(text)} characters.")
            with st.expander("📄 View extracted text"):
                st.text_area("Content:", value=text[:1000] + "..." if len(text) > 1000 else text, height=200, disabled=True)
        return text
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        return ""

def show_workflow_info():
    """Show workflow information panel"""
    st.markdown("""
    <div class="info-card">
        <h4>🔄 AI Workflow</h4>
        
        <p><strong>1. 🧠 Business Analysis</strong><br>
        AI analyzes your description to understand products, audience, and value proposition.</p>
        
        <p><strong>2. 🎯 Reddit Discovery</strong><br>
        Searches relevant subreddits for questions matching your business context.</p>
        
        <p><strong>3. 🤖 Response Generation</strong><br>
        Creates human-like responses that naturally introduce your solution.</p>
        
        <p><strong>4. 📊 Quality Assessment</strong><br>
        Evaluates response quality with helpfulness and naturalness metrics.</p>
    </div>
    """, unsafe_allow_html=True)

def run_analysis(business_description):
    """Run the complete workflow analysis"""
    if not st.session_state.get('api_configured'):
        st.error("Please configure API keys first")
        return
    
    st.session_state.processing = True
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🔄 Initializing workflow...")
        progress_bar.progress(0.1)
        
        # Initialize workflow manager
        workflow_manager = WorkflowManager(
            gemini_api_key=st.session_state.gemini_api_key,
            reddit_client_id=st.session_state.reddit_client_id,
            reddit_client_secret=st.session_state.reddit_client_secret
        )
        
        progress_bar.progress(0.2)
        status_text.text("🧠 Analyzing business...")
        
        # Run complete workflow
        results = asyncio.run(workflow_manager.run_complete_workflow(
            business_description=business_description,
            max_questions=st.session_state.max_questions,
            subreddit_limit=st.session_state.subreddit_limit,
            response_style=st.session_state.response_style,
            include_nsfw=st.session_state.include_nsfw,
            min_upvotes=st.session_state.min_upvotes,
            days_back=st.session_state.days_back
        ))
        
        progress_bar.progress(1.0)
        status_text.text("✅ Analysis complete!")
        
        # Store results
        st.session_state.workflow_results = results
        st.session_state.business_info = results.get('business_analysis', {})
        
        # Add to history
        st.session_state.analysis_history.append({
            'timestamp': datetime.now(),
            'business_description': business_description[:100] + "...",
            'questions_found': len(results.get('question_answer_pairs', [])),
            'style': st.session_state.response_style
        })
        
        st.success("🎉 Analysis completed! Check the Results tab.")
        time.sleep(2)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        if "API" in str(e):
            st.error("Please check your API keys are correct")
    finally:
        st.session_state.processing = False

def show_results_tab():
    """Show results tab"""
    if not st.session_state.workflow_results:
        st.info("Complete an analysis to see results here.")
        return
    
    results = st.session_state.workflow_results
    qa_pairs = results.get('question_answer_pairs', [])
    
    # Results summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Questions Found", len(qa_pairs))
    with col2:
        avg_score = sum(q.get('score', 0) for q in qa_pairs) / len(qa_pairs) if qa_pairs else 0
        st.metric("Avg Score", f"{avg_score:.1f}")
    with col3:
        total_comments = sum(q.get('num_comments', 0) for q in qa_pairs)
        st.metric("Total Comments", total_comments)
    with col4:
        unique_subreddits = len(set(q.get('subreddit', '') for q in qa_pairs))
        st.metric("Subreddits", unique_subreddits)
    
    if not qa_pairs:
        st.warning("No questions found. Try adjusting search parameters.")
        return
    
    # Display questions
    st.markdown("## 💬 Questions & AI Responses")
    
    for i, qa in enumerate(qa_pairs[:10], 1):  # Limit to first 10 for performance
        with st.expander(f"❓ {qa.get('title', 'No title')[:80]}...", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Subreddit:** r/{qa.get('subreddit', 'unknown')}")
                st.markdown(f"**Score:** {qa.get('score', 0)} upvotes • **Comments:** {qa.get('num_comments', 0)}")
                st.markdown(f"**Relevance:** {qa.get('relevance_score', 0):.2f}")
                
                # Question text
                question_text = qa.get('selftext', 'No question text')
                if len(question_text) > 300:
                    question_text = question_text[:300] + "..."
                st.markdown(f"**Question:** {question_text}")
                
                # AI Response
                st.markdown("**🤖 AI Response:**")
                st.markdown(qa.get('ai_response', 'No response generated'))
            
            with col2:
                if st.button(f"⭐ Save", key=f"save_{i}"):
                    add_to_favorites(qa, i)
                
                if st.button(f"📋 Copy", key=f"copy_{i}"):
                    st.code(qa.get('ai_response', ''), language=None)
                
                if st.button(f"🔗 View", key=f"view_{i}"):
                    st.markdown(f"[Open Reddit Post]({qa.get('url', '#')})")

def show_favorites_tab():
    """Show favorites tab"""
    if not st.session_state.get('favorites'):
        st.info("Save responses from the Results tab to see them here.")
        return
    
    st.markdown("## ⭐ Saved Responses")
    
    for i, fav in enumerate(st.session_state.favorites):
        with st.expander(f"⭐ {fav['title'][:60]}...", expanded=False):
            st.markdown(f"**Subreddit:** r/{fav['subreddit']}")
            st.markdown(f"**Score:** {fav['score']} upvotes")
            st.markdown(f"**Saved:** {fav['saved_at'][:16]}")
            st.markdown("**Response:**")
            st.markdown(fav['response'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📋 Copy", key=f"fav_copy_{i}"):
                    st.code(fav['response'])
            with col2:
                if st.button(f"🗑️ Remove", key=f"fav_remove_{i}"):
                    st.session_state.favorites.pop(i)
                    st.rerun()

def add_to_favorites(qa_pair, index):
    """Add response to favorites"""
    favorite = {
        'title': qa_pair.get('title', ''),
        'subreddit': qa_pair.get('subreddit', ''),
        'response': qa_pair.get('ai_response', ''),
        'score': qa_pair.get('score', 0),
        'saved_at': datetime.now().isoformat()
    }
    
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    
    # Check if already exists
    if not any(fav['title'] == favorite['title'] for fav in st.session_state.favorites):
        st.session_state.favorites.append(favorite)
        st.success("✅ Added to favorites!")
    else:
        st.warning("Already in favorites!")

if __name__ == "__main__":
    main()
