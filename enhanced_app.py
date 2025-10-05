"""
Enhanced Streamlit App with Better UI and Additional Features
"""

import streamlit as st
import os
import sys
import asyncio
import pandas as pd
from datetime import datetime
import json
import io
import PyPDF2
from typing import List, Dict, Any, Optional
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import our custom modules
try:
    from reddit_analyzer import RedditAnalyzer
    from ai_response_generator import AIResponseGenerator
    from business_analyzer import BusinessAnalyzer
    from workflow_manager import WorkflowManager
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required modules are in the same directory.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Reddit Marketing AI Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FF4B4B, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #FF6B6B;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #FF6B6B;
        padding-bottom: 0.5rem;
    }
    .info-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #FF4B4B;
    }
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .warning-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .question-card {
        background: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #FF4B4B;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .question-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.15);
    }
    .answer-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #28a745;
        margin: 1.5rem 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .progress-container {
        background: #f1f3f4;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stButton > button {
        background: linear-gradient(90deg, #FF4B4B, #FF6B6B);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(255, 75, 75, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 Reddit Marketing AI Bot</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 1.3rem; margin-bottom: 2rem;">'
        'Find perfect Reddit questions and generate human-like marketing responses with AI'
        '</p>', 
        unsafe_allow_html=True
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar configuration
    configure_sidebar()
    
    # Main content area
    if not st.session_state.get('api_configured', False):
        show_api_configuration()
    else:
        show_main_interface()

def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        'workflow_results': None,
        'business_info': None,
        'processing': False,
        'api_configured': False,
        'favorites': [],
        'analysis_history': [],
        'current_tab': 'input'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def configure_sidebar():
    """Configure the sidebar with settings and information"""
    with st.sidebar:
        st.markdown('<h2 class="sub-header">⚙️ Configuration</h2>', unsafe_allow_html=True)
        
        # API Configuration
        with st.expander("🔑 API Settings", expanded=not st.session_state.get('api_configured', False)):
            gemini_api_key = st.text_input("Gemini API Key", type="password", help="Get your API key from Google AI Studio")
            reddit_client_id = st.text_input("Reddit Client ID", help="From your Reddit app")
            reddit_client_secret = st.text_input("Reddit Client Secret", type="password", help="From your Reddit app")
            
            if st.button("✅ Save API Configuration"):
                if gemini_api_key and reddit_client_id and reddit_client_secret:
                    st.session_state.gemini_api_key = gemini_api_key
                    st.session_state.reddit_client_id = reddit_client_id
                    st.session_state.reddit_client_secret = reddit_client_secret
                    st.session_state.api_configured = True
                    st.success("API configuration saved!")
                    st.rerun()
                else:
                    st.error("Please fill in all API credentials")
        
        # Search Parameters
        with st.expander("🎯 Search Settings", expanded=True):
            st.session_state.max_questions = st.slider("Max Questions", 5, 50, 20)
            st.session_state.subreddit_limit = st.slider("Subreddits to Search", 3, 20, 10)
            st.session_state.response_style = st.selectbox(
                "Response Style",
                ["Professional", "Casual", "Expert", "Friendly", "Technical"],
                index=0
            )
        
        # Advanced Settings
        with st.expander("🔧 Advanced Options"):
            st.session_state.include_nsfw = st.checkbox("Include NSFW subreddits", value=False)
            st.session_state.min_upvotes = st.number_input("Min upvotes", min_value=0, value=5)
            st.session_state.days_back = st.slider("Days back to search", 1, 30, 7)
            st.session_state.enable_caching = st.checkbox("Enable caching", value=True)
        
        # Help and Information
        with st.expander("ℹ️ How to Get API Keys"):
            st.markdown("""
            **Gemini API Key:**
            1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
            2. Sign in with your Google account
            3. Click "Create API Key"
            4. Copy the generated key
            
            **Reddit API:**
            1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
            2. Click "Create App"
            3. Choose "script" type
            4. Use `http://localhost:8080` as redirect URI
            5. Copy Client ID and Secret
            """)

def show_api_configuration():
    """Show API configuration interface when not configured"""
    st.markdown('<div class="warning-card">', unsafe_allow_html=True)
    st.markdown("### 🔧 API Configuration Required")
    st.markdown("Please configure your API keys in the sidebar to get started.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🤖 What this bot does:
        - Analyzes your business/product description
        - Finds relevant questions on Reddit
        - Generates human-like responses with subtle marketing
        - Provides quality metrics and recommendations
        """)
    
    with col2:
        st.markdown("""
        #### 🚀 Key Features:
        - AI-powered business analysis
        - Multi-subreddit question discovery
        - Context-aware response generation
        - Quality scoring and optimization
        """)

def show_main_interface():
    """Show the main application interface"""
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Input & Analysis", "📊 Results", "⭐ Favorites", "📈 Analytics"])
    
    with tab1:
        show_input_interface()
    
    with tab2:
        show_results_interface()
    
    with tab3:
        show_favorites_interface()
    
    with tab4:
        show_analytics_interface()

def show_input_interface():
    """Show the business input and analysis interface"""
    st.markdown('<h2 class="sub-header">📝 Business Information</h2>', unsafe_allow_html=True)
    
    # Business input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input method selection
        input_method = st.radio(
            "How would you like to provide your business information?",
            ["✍️ Text Description", "📄 Upload PDF Document"],
            horizontal=True
        )
        
        business_description = ""
        
        if input_method == "✍️ Text Description":
            business_description = st.text_area(
                "Describe your business, product, or service:",
                placeholder=get_example_description(),
                height=250,
                help="Be specific about your product features, target audience, and key benefits"
            )
            
        else:  # PDF Upload
            uploaded_file = st.file_uploader(
                "Upload PDF document", 
                type="pdf",
                help="Upload a business plan, product description, or marketing document"
            )
            if uploaded_file is not None:
                business_description = extract_pdf_text(uploaded_file)
        
        # Analysis button
        if st.button("🚀 Start AI Analysis", type="primary", use_container_width=True):
            if business_description:
                run_workflow_analysis(business_description)
            else:
                st.error("Please provide business information first")
    
    with col2:
        show_workflow_steps()

def get_example_description():
    """Get example business description"""
    return """Example: We offer CloudStock Pro, a SaaS inventory management platform designed for small to medium retail businesses. Our software provides:

• Real-time inventory tracking across multiple locations
• Automated reorder notifications based on sales patterns  
• Detailed analytics and reporting dashboards
• Integration with popular POS systems and e-commerce platforms
• Mobile app for on-the-go inventory checks

Target customers: Small retail businesses (5-50 employees) struggling with manual inventory processes, overstocking, or stockouts. Perfect for boutiques, electronics stores, sporting goods retailers, and similar businesses looking to optimize their inventory management and reduce costs."""

def extract_pdf_text(uploaded_file):
    """Extract text from uploaded PDF"""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text()
        
        if pdf_text:
            st.success(f"✅ PDF processed! Extracted {len(pdf_text)} characters.")
            with st.expander("📄 View extracted text"):
                st.text_area("Content:", value=pdf_text[:2000] + "..." if len(pdf_text) > 2000 else pdf_text, height=200, disabled=True)
            return pdf_text
        else:
            st.error("❌ Could not extract text from PDF")
            return ""
            
    except Exception as e:
        st.error(f"❌ Error reading PDF: {str(e)}")
        return ""

def show_workflow_steps():
    """Show workflow steps information"""
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("### 🔄 AI Workflow Steps")
    
    steps = [
        ("🔍", "Business Analysis", "AI analyzes your business to understand products, audience, and value proposition"),
        ("🎯", "Reddit Discovery", "Searches relevant subreddits for questions matching your business context"),
        ("🤖", "Response Generation", "Creates human-like responses that naturally introduce your solution"),
        ("📊", "Quality Assessment", "Evaluates response quality and provides optimization suggestions")
    ]
    
    for icon, title, description in steps:
        st.markdown(f"**{icon} {title}**")
        st.markdown(f"<small>{description}</small>", unsafe_allow_html=True)
        st.markdown("---")
    
    st.markdown('</div>', unsafe_allow_html=True)

def run_workflow_analysis(business_description):
    """Run the complete workflow analysis"""
    st.session_state.processing = True
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize workflow manager
        workflow_manager = WorkflowManager(
            gemini_api_key=st.session_state.gemini_api_key,
            reddit_client_id=st.session_state.reddit_client_id,
            reddit_client_secret=st.session_state.reddit_client_secret
        )
        
        # Update progress
        progress_bar.progress(0.1)
        status_text.text("🔄 Initializing AI workflow...")
        
        # Run workflow
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
        analysis_record = {
            'timestamp': datetime.now(),
            'business_description': business_description[:100] + "...",
            'questions_found': len(results.get('question_answer_pairs', [])),
            'style': st.session_state.response_style
        }
        st.session_state.analysis_history.append(analysis_record)
        
        st.success("🎉 Analysis completed successfully!")
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
    finally:
        st.session_state.processing = False

def show_results_interface():
    """Show the results interface"""
    if not st.session_state.workflow_results:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📊 No Results Yet")
        st.markdown("Complete the analysis in the 'Input & Analysis' tab to see results here.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    results = st.session_state.workflow_results
    
    # Results summary
    show_results_summary(results)
    
    # Business analysis
    show_business_analysis_summary(results)
    
    # Questions and answers
    show_questions_and_answers(results)

def show_results_summary(results):
    """Show results summary with metrics"""
    st.markdown('<h2 class="sub-header">📊 Analysis Summary</h2>', unsafe_allow_html=True)
    
    summary = results.get('workflow_summary', {})
    qa_pairs = results.get('question_answer_pairs', [])
    
    # Metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Questions Found", len(qa_pairs))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        avg_score = sum(q.get('score', 0) for q in qa_pairs) / len(qa_pairs) if qa_pairs else 0
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Avg Question Score", f"{avg_score:.1f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        total_comments = sum(q.get('num_comments', 0) for q in qa_pairs)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Comments", total_comments)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        unique_subreddits = len(set(q.get('subreddit', '') for q in qa_pairs))
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Subreddits", unique_subreddits)
        st.markdown('</div>', unsafe_allow_html=True)

def show_business_analysis_summary(results):
    """Show business analysis summary"""
    if 'business_analysis' not in results:
        return
    
    st.markdown('<h3 class="sub-header">🏢 Business Analysis</h3>', unsafe_allow_html=True)
    
    with st.expander("📋 View Business Analysis Details", expanded=False):
        business_info = results['business_analysis']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📦 Product Summary:**")
            st.write(business_info.get('product_summary', 'N/A'))
            
            st.markdown("**🎯 Target Audience:**")
            st.write(business_info.get('target_audience', 'N/A'))
            
            st.markdown("**🏭 Industry:**")
            st.write(business_info.get('industry_category', 'N/A'))
        
        with col2:
            st.markdown("**✨ Key Benefits:**")
            benefits = business_info.get('key_benefits', [])
            for benefit in benefits:
                st.write(f"• {benefit}")
            
            st.markdown("**🔧 Use Cases:**")
            use_cases = business_info.get('use_cases', [])
            for use_case in use_cases[:3]:
                st.write(f"• {use_case}")
            
            st.markdown("**📍 Recommended Subreddits:**")
            subreddits = business_info.get('recommended_subreddits', [])
            for subreddit in subreddits[:5]:
                st.write(f"• r/{subreddit}")

def show_questions_and_answers(results):
    """Show questions and AI-generated answers"""
    qa_pairs = results.get('question_answer_pairs', [])
    
    if not qa_pairs:
        st.warning("No questions found. Try adjusting your search parameters.")
        return
    
    st.markdown('<h3 class="sub-header">💬 Questions & AI Responses</h3>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        sort_by = st.selectbox("Sort by:", ["Relevance", "Upvotes", "Comments", "Date"])
    with col2:
        filter_subreddit = st.selectbox("Filter by subreddit:", ["All"] + list(set(q.get('subreddit', '') for q in qa_pairs)))
    with col3:
        min_score_filter = st.slider("Min score:", 0, max(q.get('score', 0) for q in qa_pairs), 0)
    
    # Apply filters and sorting
    filtered_qa = filter_and_sort_questions(qa_pairs, sort_by, filter_subreddit, min_score_filter)
    
    # Display questions and answers
    for i, qa_pair in enumerate(filtered_qa, 1):
        display_question_answer_pair(qa_pair, i)

def filter_and_sort_questions(qa_pairs, sort_by, filter_subreddit, min_score):
    """Filter and sort questions based on user selections"""
    # Filter
    filtered = qa_pairs
    
    if filter_subreddit != "All":
        filtered = [q for q in filtered if q.get('subreddit') == filter_subreddit]
    
    filtered = [q for q in filtered if q.get('score', 0) >= min_score]
    
    # Sort
    if sort_by == "Relevance":
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    elif sort_by == "Upvotes":
        filtered.sort(key=lambda x: x.get('score', 0), reverse=True)
    elif sort_by == "Comments":
        filtered.sort(key=lambda x: x.get('num_comments', 0), reverse=True)
    elif sort_by == "Date":
        filtered.sort(key=lambda x: x.get('created_utc', 0), reverse=True)
    
    return filtered

def display_question_answer_pair(qa_pair, index):
    """Display a single question-answer pair"""
    with st.container():
        # Question card
        st.markdown(f"""
        <div class="question-card">
            <h4>❓ Question {index}: {qa_pair.get('title', 'No title')}</h4>
            <p><strong>📍 Subreddit:</strong> r/{qa_pair.get('subreddit', 'unknown')}</p>
            <p><strong>📊 Metrics:</strong> {qa_pair.get('score', 0)} upvotes • {qa_pair.get('num_comments', 0)} comments • Relevance: {qa_pair.get('relevance_score', 0):.2f}</p>
            <p><strong>📅 Posted:</strong> {datetime.fromtimestamp(qa_pair.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong>❓ Question:</strong></p>
            <p>{qa_pair.get('selftext', 'No question text')[:500]}{'...' if len(qa_pair.get('selftext', '')) > 500 else ''}</p>
            <p><strong>🔗 URL:</strong> <a href="{qa_pair.get('url', '#')}" target="_blank">View on Reddit</a></p>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Response card
        st.markdown(f"""
        <div class="answer-card">
            <h4>🤖 AI-Generated Response</h4>
            <p>{qa_pair.get('ai_response', 'No response generated')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Quality metrics
        quality_metrics = qa_pair.get('quality_metrics', {})
        if quality_metrics:
            with st.expander(f"📈 Quality Metrics for Response {index}"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Overall Quality", f"{quality_metrics.get('overall_score', 0):.2f}")
                with col2:
                    st.metric("Helpfulness", f"{quality_metrics.get('helpfulness_score', 0):.2f}")
                with col3:
                    st.metric("Naturalness", f"{quality_metrics.get('naturalness_score', 0):.2f}")
                with col4:
                    st.metric("Marketing Subtlety", f"{quality_metrics.get('marketing_subtlety', 0):.2f}")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button(f"📋 Copy Response", key=f"copy_{index}"):
                st.code(qa_pair.get('ai_response', ''), language=None)
        
        with col2:
            if st.button(f"⭐ Add to Favorites", key=f"fav_{index}"):
                add_to_favorites(qa_pair, index)
        
        with col3:
            if st.button(f"✏️ Edit Response", key=f"edit_{index}"):
                st.session_state[f"editing_{index}"] = True
        
        with col4:
            if st.button(f"🔄 Regenerate", key=f"regen_{index}"):
                regenerate_response(qa_pair, index)
        
        # Edit interface
        if st.session_state.get(f"editing_{index}", False):
            with st.expander(f"✏️ Edit Response {index}", expanded=True):
                edited_response = st.text_area(
                    "Edit the response:",
                    value=qa_pair.get('ai_response', ''),
                    height=200,
                    key=f"edit_area_{index}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Changes", key=f"save_{index}"):
                        qa_pair['ai_response'] = edited_response
                        st.session_state[f"editing_{index}"] = False
                        st.success("Response updated!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_{index}"):
                        st.session_state[f"editing_{index}"] = False
                        st.rerun()
        
        st.markdown("---")

def add_to_favorites(qa_pair, index):
    """Add a question-answer pair to favorites"""
    favorite = {
        'index': index,
        'title': qa_pair.get('title', ''),
        'subreddit': qa_pair.get('subreddit', ''),
        'response': qa_pair.get('ai_response', ''),
        'url': qa_pair.get('url', ''),
        'saved_at': datetime.now().isoformat(),
        'score': qa_pair.get('score', 0),
        'relevance_score': qa_pair.get('relevance_score', 0)
    }
    
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    
    # Check if already in favorites
    if not any(fav['title'] == favorite['title'] for fav in st.session_state.favorites):
        st.session_state.favorites.append(favorite)
        st.success(f"✅ Added to favorites!")
    else:
        st.warning("Already in favorites!")

def regenerate_response(qa_pair, index):
    """Regenerate response for a specific question"""
    if not st.session_state.get('api_configured', False):
        st.error("API not configured!")
        return
    
    try:
        with st.spinner("🔄 Regenerating response..."):
            response_generator = AIResponseGenerator(st.session_state.gemini_api_key)
            new_response = asyncio.run(response_generator.generate_response(
                question_data=qa_pair,
                business_info=st.session_state.business_info,
                response_style=st.session_state.response_style
            ))
            qa_pair['ai_response'] = new_response
            st.success("✅ Response regenerated!")
            st.rerun()
    except Exception as e:
        st.error(f"❌ Failed to regenerate: {str(e)}")

def show_favorites_interface():
    """Show favorites interface"""
    st.markdown('<h2 class="sub-header">⭐ Favorite Responses</h2>', unsafe_allow_html=True)
    
    if not st.session_state.get('favorites'):
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("### 📝 No Favorites Yet")
        st.markdown("Add responses to favorites from the Results tab to see them here.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Display favorites
    for i, favorite in enumerate(st.session_state.favorites):
        with st.expander(f"⭐ {favorite['title'][:50]}..." if len(favorite['title']) > 50 else favorite['title'], expanded=False):
            st.markdown(f"**Subreddit:** r/{favorite['subreddit']}")
            st.markdown(f"**Score:** {favorite['score']} upvotes")
            st.markdown(f"**Relevance:** {favorite.get('relevance_score', 0):.2f}")
            st.markdown(f"**Saved:** {favorite['saved_at'][:16]}")
            st.markdown("**Response:**")
            st.markdown(favorite['response'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"📋 Copy", key=f"fav_copy_{i}"):
                    st.code(favorite['response'])
            with col2:
                if st.button(f"🔗 View Original", key=f"fav_view_{i}"):
                    st.markdown(f"[Open in Reddit]({favorite.get('url', '#')})")
            with col3:
                if st.button(f"🗑️ Remove", key=f"fav_remove_{i}"):
                    st.session_state.favorites.pop(i)
                    st.rerun()

def show_analytics_interface():
    """Show analytics and insights interface"""
    st.markdown('<h2 class="sub-header">📈 Analytics & Insights</h2>', unsafe_allow_html=True)
    
    if not st.session_state.workflow_results:
        st.info("Complete an analysis to see analytics here.")
        return
    
    results = st.session_state.workflow_results
    qa_pairs = results.get('question_answer_pairs', [])
    
    if not qa_pairs:
        st.warning("No data available for analytics.")
        return
    
    # Analytics tabs
    analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs(["📊 Question Analysis", "🎯 Subreddit Performance", "⏱️ Analysis History"])
    
    with analytics_tab1:
        show_question_analytics(qa_pairs)
    
    with analytics_tab2:
        show_subreddit_analytics(qa_pairs)
    
    with analytics_tab3:
        show_analysis_history()

def show_question_analytics(qa_pairs):
    """Show question analytics charts"""
    # Score distribution
    scores = [q.get('score', 0) for q in qa_pairs]
    relevance_scores = [q.get('relevance_score', 0) for q in qa_pairs]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_scores = px.histogram(
            x=scores,
            nbins=20,
            title="Question Score Distribution",
            labels={'x': 'Upvotes', 'y': 'Count'}
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    
    with col2:
        fig_relevance = px.histogram(
            x=relevance_scores,
            nbins=20,
            title="Relevance Score Distribution",
            labels={'x': 'Relevance Score', 'y': 'Count'}
        )
        st.plotly_chart(fig_relevance, use_container_width=True)
    
    # Scatter plot of score vs relevance
    fig_scatter = px.scatter(
        x=scores,
        y=relevance_scores,
        title="Question Score vs Relevance",
        labels={'x': 'Upvotes', 'y': 'Relevance Score'},
        hover_data=['x', 'y']
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

def show_subreddit_analytics(qa_pairs):
    """Show subreddit performance analytics"""
    # Subreddit distribution
    subreddit_counts = {}
    subreddit_avg_scores = {}
    
    for qa in qa_pairs:
        subreddit = qa.get('subreddit', 'unknown')
        score = qa.get('score', 0)
        
        if subreddit not in subreddit_counts:
            subreddit_counts[subreddit] = 0
            subreddit_avg_scores[subreddit] = []
        
        subreddit_counts[subreddit] += 1
        subreddit_avg_scores[subreddit].append(score)
    
    # Calculate averages
    for subreddit in subreddit_avg_scores:
        scores = subreddit_avg_scores[subreddit]
        subreddit_avg_scores[subreddit] = sum(scores) / len(scores) if scores else 0
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Questions per subreddit
        fig_counts = px.bar(
            x=list(subreddit_counts.keys()),
            y=list(subreddit_counts.values()),
            title="Questions Found per Subreddit",
            labels={'x': 'Subreddit', 'y': 'Number of Questions'}
        )
        fig_counts.update_xaxes(tickangle=45)
        st.plotly_chart(fig_counts, use_container_width=True)
    
    with col2:
        # Average scores per subreddit
        fig_avg_scores = px.bar(
            x=list(subreddit_avg_scores.keys()),
            y=list(subreddit_avg_scores.values()),
            title="Average Question Score per Subreddit",
            labels={'x': 'Subreddit', 'y': 'Average Score'}
        )
        fig_avg_scores.update_xaxes(tickangle=45)
        st.plotly_chart(fig_avg_scores, use_container_width=True)

def show_analysis_history():
    """Show analysis history"""
    if not st.session_state.get('analysis_history'):
        st.info("No analysis history yet. Complete some analyses to see history here.")
        return
    
    history_df = pd.DataFrame(st.session_state.analysis_history)
    
    # Display as table
    st.dataframe(
        history_df,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Date & Time"),
            "business_description": st.column_config.TextColumn("Business Description"),
            "questions_found": st.column_config.NumberColumn("Questions Found"),
            "style": st.column_config.TextColumn("Response Style")
        },
        use_container_width=True
    )
    
    # Export history
    if st.button("📤 Export History"):
        csv = history_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv,
            file_name=f"analysis_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
