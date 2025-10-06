"""
Reddit Marketing Bot - Replit UI
A comprehensive web application for finding relevant Reddit questions and generating human-like responses
"""

import streamlit as st
import os
import asyncio
import pandas as pd
from datetime import datetime
import json
import io
import PyPDF2
from typing import List, Dict, Any, Optional
import time

# Import our custom modules
from reddit_analyzer import RedditAnalyzer
from ai_response_generator import AIResponseGenerator
from business_analyzer import BusinessAnalyzer
from workflow_manager import WorkflowManager

# Page configuration
st.set_page_config(
    page_title="Reddit Marketing Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #FF6B6B;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
    .question-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF4B4B;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .answer-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🤖 Reddit Marketing Bot</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.2rem;">Find relevant Reddit questions and generate human-like marketing responses</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = None
    if 'business_info' not in st.session_state:
        st.session_state.business_info = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False

    # Sidebar for configuration
    with st.sidebar:
        st.markdown('<h2 class="sub-header">⚙️ Configuration</h2>', unsafe_allow_html=True)
        
        # API Keys section
        st.markdown("### 🔑 API Configuration")
        gemini_api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key")
        reddit_client_id = st.text_input("Reddit Client ID", help="Your Reddit app client ID")
        reddit_client_secret = st.text_input("Reddit Client Secret", type="password", help="Your Reddit app client secret")
        
        # Search parameters
        st.markdown("### 🎯 Search Parameters")
        max_questions = st.slider("Max Questions to Find", min_value=5, max_value=50, value=20)
        subreddit_limit = st.slider("Subreddits to Search", min_value=3, max_value=15, value=8)
        response_style = st.selectbox(
            "Response Style",
            ["Professional", "Casual", "Expert", "Friendly", "Technical"]
        )
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            include_nsfw = st.checkbox("Include NSFW subreddits", value=False)
            min_upvotes = st.number_input("Minimum upvotes for questions", min_value=0, value=5)
            days_back = st.slider("Search posts from last N days", min_value=1, max_value=30, value=7)

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📝 Business Information</h2>', unsafe_allow_html=True)
        
        # Input method selection
        input_method = st.radio(
            "How would you like to provide your business information?",
            ["Text Description", "Upload PDF Document"],
            horizontal=True
        )
        
        business_description = ""
        
        if input_method == "Text Description":
            business_description = st.text_area(
                "Describe your business, product, or service:",
                placeholder="Example: We offer a SaaS platform that helps small businesses manage their inventory efficiently. Our tool provides real-time tracking, automated reordering, and detailed analytics. Target customers are small to medium retail businesses looking to optimize their stock management.",
                height=200
            )
            
        else:  # PDF Upload
            uploaded_file = st.file_uploader("Upload PDF document", type="pdf")
            if uploaded_file is not None:
                try:
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    pdf_text = ""
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text()
                    
                    business_description = pdf_text
                    st.success(f"PDF uploaded successfully! Extracted {len(pdf_text)} characters.")
                    
                    with st.expander("📄 View extracted text"):
                        st.text_area("Extracted content:", value=pdf_text[:2000] + "..." if len(pdf_text) > 2000 else pdf_text, height=200, disabled=True)
                        
                except Exception as e:
                    st.error(f"Error reading PDF: {str(e)}")
        
        # Process button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn2:
            process_button = st.button(
                "🚀 Start Analysis",
                type="primary",
                use_container_width=True,
                disabled=not business_description or not gemini_api_key or not reddit_client_id or not reddit_client_secret
            )
    
    with col2:
        st.markdown('<h2 class="sub-header">ℹ️ How it works</h2>', unsafe_allow_html=True)
        
        with st.container():
            st.markdown("""
            <div class="info-box">
            <h4>🔍 Step 1: Business Analysis</h4>
            Our AI analyzes your business description to understand your product, target audience, and value proposition.
            </div>
            
            <div class="info-box">
            <h4>🎯 Step 2: Reddit Search</h4>
            We search relevant subreddits for questions that match your business context and target audience.
            </div>
            
            <div class="info-box">
            <h4>🤖 Step 3: Response Generation</h4>
            AI generates human-like, helpful responses that naturally introduce your product as a solution.
            </div>
            
            <div class="info-box">
            <h4>📊 Step 4: Results Review</h4>
            Review and customize the generated responses before using them for marketing.
            </div>
            """, unsafe_allow_html=True)

    # Process the workflow
    if process_button and not st.session_state.processing:
        st.session_state.processing = True
        
        with st.spinner("🔄 Processing your request..."):
            try:
                # Initialize workflow manager
                workflow_manager = WorkflowManager(
                    gemini_api_key=gemini_api_key,
                    reddit_client_id=reddit_client_id,
                    reddit_client_secret=reddit_client_secret
                )
                
                # Run the complete workflow
                results = asyncio.run(workflow_manager.run_complete_workflow(
                    business_description=business_description,
                    max_questions=max_questions,
                    subreddit_limit=subreddit_limit,
                    response_style=response_style,
                    include_nsfw=include_nsfw,
                    min_upvotes=min_upvotes,
                    days_back=days_back
                ))
                
                st.session_state.workflow_results = results
                st.session_state.business_info = results.get('business_analysis', {})
                
            except Exception as e:
                st.error(f"Error during processing: {str(e)}")
            finally:
                st.session_state.processing = False

    # Display results
    if st.session_state.workflow_results:
        display_results(st.session_state.workflow_results)

def display_results(results: Dict[str, Any]):
    """Display the workflow results in an organized manner"""
    
    st.markdown("---")
    st.markdown('<h2 class="sub-header">📊 Analysis Results</h2>', unsafe_allow_html=True)
    
    # Business Analysis Summary
    if 'business_analysis' in results:
        with st.expander("🏢 Business Analysis Summary", expanded=True):
            business_info = results['business_analysis']
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Product/Service:**")
                st.write(business_info.get('product_summary', 'N/A'))
                
                st.markdown("**Target Audience:**")
                st.write(business_info.get('target_audience', 'N/A'))
                
            with col2:
                st.markdown("**Key Benefits:**")
                benefits = business_info.get('key_benefits', [])
                for benefit in benefits:
                    st.write(f"• {benefit}")
                
                st.markdown("**Relevant Subreddits:**")
                subreddits = business_info.get('recommended_subreddits', [])
                for subreddit in subreddits:
                    st.write(f"• r/{subreddit}")

    # Questions and Answers
    if 'question_answer_pairs' in results:
        st.markdown('<h2 class="sub-header">💬 Questions & AI-Generated Responses</h2>', unsafe_allow_html=True)
        
        qa_pairs = results['question_answer_pairs']
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Questions Found", len(qa_pairs))
        with col2:
            avg_score = sum(q.get('score', 0) for q in qa_pairs) / len(qa_pairs) if qa_pairs else 0
            st.metric("Avg Question Score", f"{avg_score:.1f}")
        with col3:
            total_comments = sum(q.get('num_comments', 0) for q in qa_pairs)
            st.metric("Total Comments", total_comments)
        with col4:
            unique_subreddits = len(set(q.get('subreddit', '') for q in qa_pairs))
            st.metric("Subreddits Covered", unique_subreddits)
        
        # Display each question-answer pair
        for i, qa_pair in enumerate(qa_pairs, 1):
            with st.container():
                st.markdown(f"### 📋 Question {i}")
                
                # Question details
                st.markdown(f"""
                <div class="question-card">
                    <h4>❓ {qa_pair.get('title', 'No title')}</h4>
                    <p><strong>Subreddit:</strong> r/{qa_pair.get('subreddit', 'unknown')}</p>
                    <p><strong>Score:</strong> {qa_pair.get('score', 0)} upvotes | <strong>Comments:</strong> {qa_pair.get('num_comments', 0)}</p>
                    <p><strong>Created:</strong> {datetime.fromtimestamp(qa_pair.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M')}</p>
                    <p><strong>Question:</strong> {qa_pair.get('selftext', 'No question text')[:500]}{'...' if len(qa_pair.get('selftext', '')) > 500 else ''}</p>
                    <p><strong>URL:</strong> <a href="{qa_pair.get('url', '#')}" target="_blank">View on Reddit</a></p>
                </div>
                """, unsafe_allow_html=True)
                
                # AI-generated answer
                st.markdown(f"""
                <div class="answer-card">
                    <h4>🤖 AI-Generated Response</h4>
                    <p>{qa_pair.get('ai_response', 'No response generated')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons for each response
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"📋 Copy Response {i}", key=f"copy_{i}"):
                        st.code(qa_pair.get('ai_response', ''), language=None)
                        
                with col2:
                    if st.button(f"✏️ Edit Response {i}", key=f"edit_{i}"):
                        edited_response = st.text_area(
                            f"Edit response for question {i}:",
                            value=qa_pair.get('ai_response', ''),
                            key=f"edit_area_{i}",
                            height=150
                        )
                        qa_pair['ai_response'] = edited_response
                        
                with col3:
                    if st.button(f"⭐ Save Favorite {i}", key=f"save_{i}"):
                        save_favorite_response(qa_pair, i)
                
                st.markdown("---")

    # Export options
    if st.session_state.workflow_results:
        st.markdown('<h2 class="sub-header">📤 Export Results</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export to CSV", use_container_width=True):
                csv_data = create_csv_export(st.session_state.workflow_results)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"reddit_marketing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
        with col2:
            if st.button("📝 Export to JSON", use_container_width=True):
                json_data = json.dumps(st.session_state.workflow_results, indent=2, default=str)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"reddit_marketing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
        with col3:
            if st.button("📄 Generate Report", use_container_width=True):
                report = generate_summary_report(st.session_state.workflow_results)
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"reddit_marketing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )

def save_favorite_response(qa_pair: Dict, index: int):
    """Save a favorite response to session state"""
    if 'favorites' not in st.session_state:
        st.session_state.favorites = []
    
    favorite = {
        'index': index,
        'title': qa_pair.get('title', ''),
        'subreddit': qa_pair.get('subreddit', ''),
        'response': qa_pair.get('ai_response', ''),
        'saved_at': datetime.now().isoformat()
    }
    
    st.session_state.favorites.append(favorite)
    st.success(f"Response {index} saved to favorites!")

def create_csv_export(results: Dict[str, Any]) -> str:
    """Create CSV export of the results"""
    qa_pairs = results.get('question_answer_pairs', [])
    
    data = []
    for qa in qa_pairs:
        data.append({
            'title': qa.get('title', ''),
            'subreddit': qa.get('subreddit', ''),
            'score': qa.get('score', 0),
            'num_comments': qa.get('num_comments', 0),
            'created_date': datetime.fromtimestamp(qa.get('created_utc', 0)).strftime('%Y-%m-%d'),
            'question_text': qa.get('selftext', ''),
            'ai_response': qa.get('ai_response', ''),
            'url': qa.get('url', '')
        })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

def generate_summary_report(results: Dict[str, Any]) -> str:
    """Generate a summary report of the results"""
    report = f"""
REDDIT MARKETING BOT - ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

========================================
BUSINESS ANALYSIS SUMMARY
========================================
"""
    
    if 'business_analysis' in results:
        business = results['business_analysis']
        report += f"""
Product/Service: {business.get('product_summary', 'N/A')}
Target Audience: {business.get('target_audience', 'N/A')}

Key Benefits:
"""
        for benefit in business.get('key_benefits', []):
            report += f"• {benefit}\n"
        
        report += f"""
Recommended Subreddits:
"""
        for subreddit in business.get('recommended_subreddits', []):
            report += f"• r/{subreddit}\n"
    
    if 'question_answer_pairs' in results:
        qa_pairs = results['question_answer_pairs']
        report += f"""

========================================
QUESTIONS & RESPONSES SUMMARY
========================================
Total Questions Found: {len(qa_pairs)}
Average Question Score: {sum(q.get('score', 0) for q in qa_pairs) / len(qa_pairs) if qa_pairs else 0:.1f}
Total Comments: {sum(q.get('num_comments', 0) for q in qa_pairs)}
Unique Subreddits: {len(set(q.get('subreddit', '') for q in qa_pairs))}

========================================
DETAILED QUESTIONS & RESPONSES
========================================
"""
        
        for i, qa in enumerate(qa_pairs, 1):
            report += f"""
Question {i}:
Title: {qa.get('title', 'No title')}
Subreddit: r/{qa.get('subreddit', 'unknown')}
Score: {qa.get('score', 0)} upvotes
Comments: {qa.get('num_comments', 0)}
Date: {datetime.fromtimestamp(qa.get('created_utc', 0)).strftime('%Y-%m-%d %H:%M')}

Question Text:
{qa.get('selftext', 'No question text')}

AI-Generated Response:
{qa.get('ai_response', 'No response generated')}

URL: {qa.get('url', '#')}

---
"""
    
    return report

if __name__ == "__main__":
    main()
