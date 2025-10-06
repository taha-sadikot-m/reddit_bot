"""
Enhanced Reddit Marketing Bot with Automated Posting
Streamlit application with complete workflow including posting capabilities
"""

import streamlit as st
import asyncio
import os
from datetime import datetime
import json

# Set page config
st.set_page_config(
    page_title="Reddit Marketing Bot Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our components
from workflow_manager import WorkflowManager
from config import REDDIT_CONFIG
from reddit_poster import RedditPoster

# Initialize session state
if 'workflow_results' not in st.session_state:
    st.session_state.workflow_results = None
if 'posting_enabled' not in st.session_state:
    st.session_state.posting_enabled = False
if 'reddit_credentials_valid' not in st.session_state:
    st.session_state.reddit_credentials_valid = False

def check_reddit_credentials():
    """Check if Reddit credentials are properly configured"""
    config = st.session_state.get('reddit_config', REDDIT_CONFIG)
    
    required_fields = ['client_id', 'client_secret', 'username', 'password']
    for field in required_fields:
        if not config.get(field) or config[field].startswith('YOUR_'):
            return False
    return True

def main():
    st.title("🤖 Reddit Marketing Bot Pro")
    st.markdown("**Advanced Reddit marketing automation with intelligent posting**")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys Section
        st.subheader("🔑 API Keys")
        gemini_api_key = st.text_input(
            "Gemini API Key",
            type="password",
            help="Get your API key from Google AI Studio"
        )
        
        # Reddit Credentials Section
        st.subheader("🔐 Reddit Credentials")
        
        with st.expander("Reddit API Settings", expanded=True):
            reddit_client_id = st.text_input(
                "Client ID",
                value=REDDIT_CONFIG.get('client_id', ''),
                help="From your Reddit app settings"
            )
            reddit_client_secret = st.text_input(
                "Client Secret",
                type="password",
                value=REDDIT_CONFIG.get('client_secret', ''),
                help="From your Reddit app settings"
            )
            reddit_username = st.text_input(
                "Reddit Username",
                value=REDDIT_CONFIG.get('username', ''),
                help="Your Reddit username (required for posting)"
            )
            reddit_password = st.text_input(
                "Reddit Password",
                type="password",
                value=REDDIT_CONFIG.get('password', ''),
                help="Your Reddit password (required for posting)"
            )
        
        # Store credentials in session state
        st.session_state.reddit_config = {
            'client_id': reddit_client_id,
            'client_secret': reddit_client_secret,
            'username': reddit_username,
            'password': reddit_password,
            'user_agent': REDDIT_CONFIG.get('user_agent', 'RedditBot/1.0')
        }
        
        # Check credentials
        creds_valid = check_reddit_credentials()
        st.session_state.reddit_credentials_valid = creds_valid
        
        if creds_valid:
            st.success("✅ Reddit credentials configured")
            st.session_state.posting_enabled = True
        else:
            st.warning("⚠️ Reddit credentials needed for posting")
            st.session_state.posting_enabled = False
        
        # Workflow Configuration
        st.subheader("🎯 Workflow Settings")
        
        max_questions = st.slider(
            "Max Questions to Find",
            min_value=5,
            max_value=50,
            value=20,
            help="Maximum number of questions to analyze"
        )
        
        subreddit_limit = st.slider(
            "Subreddit Limit",
            min_value=3,
            max_value=15,
            value=8,
            help="Number of subreddits to search"
        )
        
        response_style = st.selectbox(
            "Response Style",
            ["Casual", "Professional", "Expert", "Friendly"],
            index=0,
            help="Tone of generated responses"
        )
        
        min_upvotes = st.slider(
            "Minimum Upvotes",
            min_value=1,
            max_value=50,
            value=5,
            help="Minimum upvotes for questions to consider"
        )
        
        days_back = st.slider(
            "Search Days Back",
            min_value=1,
            max_value=30,
            value=7,
            help="How many days back to search"
        )
        
        include_nsfw = st.checkbox(
            "Include NSFW Subreddits",
            value=False,
            help="Include NSFW content in search"
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Business Description")
        business_description = st.text_area(
            "Describe your business/product:",
            height=150,
            placeholder="Example: We are a SaaS company that helps small businesses manage their inventory more efficiently. Our product automates stock tracking, provides low-stock alerts, and generates purchase orders automatically...",
            help="Provide a detailed description of your business, product, or service"
        )
    
    with col2:
        st.header("🚀 Posting Options")
        
        if st.session_state.posting_enabled:
            auto_post = st.checkbox(
                "🔥 Enable Auto-Posting",
                value=False,
                help="Automatically post responses to Reddit"
            )
            
            if auto_post:
                dry_run = st.checkbox(
                    "🧪 Dry Run Mode",
                    value=True,
                    help="Simulate posting without actually posting"
                )
                
                if not dry_run:
                    st.warning("⚠️ **LIVE POSTING MODE** - Comments will be posted to Reddit!")
                    confirm_live = st.checkbox("I understand this will post real comments")
                    if not confirm_live:
                        auto_post = False
                else:
                    st.info("🧪 Dry run mode - no actual posting")
            else:
                dry_run = True
        else:
            auto_post = False
            dry_run = True
            st.warning("⚠️ Configure Reddit credentials to enable posting")
    
    # Action buttons
    st.header("🎯 Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Run Complete Workflow", type="primary", use_container_width=True):
            if not gemini_api_key:
                st.error("❌ Please provide Gemini API key")
                return
            
            if not business_description.strip():
                st.error("❌ Please provide business description")
                return
            
            run_workflow(
                business_description=business_description,
                gemini_api_key=gemini_api_key,
                reddit_config=st.session_state.reddit_config,
                max_questions=max_questions,
                subreddit_limit=subreddit_limit,
                response_style=response_style,
                min_upvotes=min_upvotes,
                days_back=days_back,
                include_nsfw=include_nsfw,
                auto_post=auto_post,
                dry_run=dry_run
            )
    
    with col2:
        if st.button("📊 Show Posting Statistics", use_container_width=True):
            show_posting_stats()
    
    with col3:
        if st.button("🧪 Test Reddit Connection", use_container_width=True):
            test_reddit_connection()
    
    # Display results
    if st.session_state.workflow_results:
        display_results(st.session_state.workflow_results)

def run_workflow(business_description, gemini_api_key, reddit_config, **kwargs):
    """Run the complete workflow"""
    with st.spinner("🔄 Running Reddit Marketing Workflow..."):
        try:
            # Initialize workflow manager
            workflow_manager = WorkflowManager(
                gemini_api_key=gemini_api_key,
                reddit_client_id=reddit_config['client_id'],
                reddit_client_secret=reddit_config['client_secret'],
                reddit_username=reddit_config['username'] if kwargs.get('auto_post') else None,
                reddit_password=reddit_config['password'] if kwargs.get('auto_post') else None
            )
            
            # Run workflow
            results = asyncio.run(
                workflow_manager.run_complete_workflow(
                    business_description=business_description,
                    **kwargs
                )
            )
            
            st.session_state.workflow_results = results
            
            if results.get('workflow_summary', {}).get('success', False):
                st.success("✅ Workflow completed successfully!")
            else:
                st.error("❌ Workflow completed with errors")
                
        except Exception as e:
            st.error(f"❌ Workflow failed: {str(e)}")

def show_posting_stats():
    """Show posting statistics"""
    if not st.session_state.posting_enabled:
        st.warning("⚠️ Reddit credentials not configured")
        return
    
    try:
        config = st.session_state.reddit_config
        poster = RedditPoster(
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            username=config['username'],
            password=config['password']
        )
        
        # Load posting history
        poster.load_posting_history()
        
        stats = poster.get_posting_stats()
        
        st.subheader("📊 Posting Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Today's Posts", stats['daily_posts'])
        
        with col2:
            st.metric("Daily Limit", stats['daily_limit'])
        
        with col3:
            st.metric("Total Posted", stats['total_posted'])
        
        with col4:
            st.metric("Can Post Now", "✅" if stats['can_post_now'] else "❌")
        
        if stats['last_post']:
            st.info(f"🕒 Last post: {stats['last_post']}")
        
        if stats['next_post_available'] != 'Now':
            st.info(f"⏰ Next post available: {stats['next_post_available']}")
        
    except Exception as e:
        st.error(f"❌ Error getting posting stats: {str(e)}")

def test_reddit_connection():
    """Test Reddit connection"""
    if not st.session_state.reddit_credentials_valid:
        st.warning("⚠️ Please configure Reddit credentials first")
        return
    
    with st.spinner("🔄 Testing Reddit connection..."):
        try:
            config = st.session_state.reddit_config
            
            # Test basic connection
            from reddit_analyzer import RedditAnalyzer
            analyzer = RedditAnalyzer(config['client_id'], config['client_secret'])
            
            # Test posting connection if credentials provided
            if config['username'] and config['password']:
                poster = RedditPoster(
                    client_id=config['client_id'],
                    client_secret=config['client_secret'],
                    username=config['username'],
                    password=config['password']
                )
                
                success = asyncio.run(poster.initialize())
                if success:
                    stats = poster.get_posting_stats()
                    st.success(f"✅ Reddit connection successful!")
                    st.info(f"📊 Connected as u/{stats['username']} with {stats['total_posted']} posts in history")
                else:
                    st.error("❌ Reddit posting authentication failed")
            else:
                st.success("✅ Reddit read-only connection successful!")
                
        except Exception as e:
            st.error(f"❌ Reddit connection failed: {str(e)}")

def display_results(results):
    """Display workflow results"""
    st.header("📊 Workflow Results")
    
    # Summary metrics
    summary = results.get('workflow_summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Questions Found", summary.get('total_questions_found', 0))
    
    with col2:
        st.metric("Responses Generated", summary.get('responses_generated', 0))
    
    with col3:
        success_rate = "100%" if summary.get('success', False) else "Failed"
        st.metric("Success Rate", success_rate)
    
    with col4:
        posting_results = results.get('posting_results', {})
        if posting_results:
            posted_count = posting_results.get('posted', 0)
            st.metric("Comments Posted", posted_count)
    
    # Posting Results (if available)
    if results.get('posting_results'):
        posting_results = results['posting_results']
        
        st.subheader("📝 Posting Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Posted", posting_results.get('posted', 0))
        with col2:
            st.metric("Skipped", posting_results.get('skipped', 0))
        with col3:
            st.metric("Failed", posting_results.get('failed', 0))
        
        # Show posting details
        if posting_results.get('details'):
            with st.expander("📋 Posting Details", expanded=True):
                for detail in posting_results['details']:
                    status_emoji = "✅" if detail['success'] else "❌"
                    st.write(f"{status_emoji} **{detail['question_title']}** (r/{detail['subreddit']})")
                    st.write(f"   {detail['message']}")
                    if detail.get('comment_url'):
                        st.write(f"   🔗 [View Comment]({detail['comment_url']})")
    
    # Business Analysis
    business_analysis = results.get('business_analysis', {})
    if business_analysis:
        st.subheader("🏢 Business Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Product Summary:**")
            st.write(business_analysis.get('product_summary', 'N/A'))
            
            st.write("**Target Audience:**")
            st.write(business_analysis.get('target_audience', 'N/A'))
        
        with col2:
            st.write("**Industry Category:**")
            st.write(business_analysis.get('industry_category', 'N/A'))
            
            st.write("**Key Benefits:**")
            benefits = business_analysis.get('key_benefits', [])
            for benefit in benefits[:3]:
                st.write(f"• {benefit}")
    
    # Questions and Responses
    qa_pairs = results.get('question_answer_pairs', [])
    if qa_pairs:
        st.subheader("💬 Generated Responses")
        
        for i, qa in enumerate(qa_pairs, 1):
            with st.expander(f"#{i} - r/{qa.get('subreddit', 'unknown')} - {qa.get('title', 'Untitled')[:60]}..."):
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write("**Question Details:**")
                    st.write(f"**Subreddit:** r/{qa.get('subreddit', 'unknown')}")
                    st.write(f"**Score:** {qa.get('score', 0)} upvotes")
                    st.write(f"**Comments:** {qa.get('num_comments', 0)}")
                    
                    if qa.get('relevance_score'):
                        st.write(f"**Relevance:** {qa.get('relevance_score', 0):.2f}/1.0")
                    
                    if qa.get('url'):
                        st.write(f"🔗 [View Original]({qa.get('url')})")
                
                with col2:
                    st.write("**Original Question:**")
                    st.write(qa.get('title', 'N/A'))
                    
                    if qa.get('selftext'):
                        st.write("**Question Body:**")
                        st.write(qa.get('selftext', '')[:200] + "..." if len(qa.get('selftext', '')) > 200 else qa.get('selftext', ''))
                    
                    st.write("**Generated Response:**")
                    st.write(qa.get('ai_response', 'No response generated'))
    
    # Errors (if any)
    errors = results.get('errors', [])
    if errors:
        st.subheader("⚠️ Errors")
        for error in errors:
            st.error(error)
    
    # Download results
    st.subheader("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 Download JSON Results"):
            results_json = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="💾 Download Results.json",
                data=results_json,
                file_name=f"reddit_marketing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📝 Download CSV Report"):
            # Create CSV content
            csv_content = generate_csv_report(results)
            st.download_button(
                label="💾 Download Report.csv",
                data=csv_content,
                file_name=f"reddit_marketing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def generate_csv_report(results):
    """Generate CSV report from results"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Question_Title', 'Subreddit', 'Score', 'Comments', 'Relevance_Score',
        'Generated_Response', 'URL', 'Posted', 'Post_Status'
    ])
    
    # Data rows
    qa_pairs = results.get('question_answer_pairs', [])
    posting_details = {d['question_id']: d for d in results.get('posting_results', {}).get('details', [])}
    
    for qa in qa_pairs:
        posting_detail = posting_details.get(qa.get('id', ''), {})
        
        writer.writerow([
            qa.get('title', ''),
            qa.get('subreddit', ''),
            qa.get('score', 0),
            qa.get('num_comments', 0),
            qa.get('relevance_score', 0),
            qa.get('ai_response', ''),
            qa.get('url', ''),
            'Yes' if posting_detail.get('success') else 'No',
            posting_detail.get('message', 'Not posted')
        ])
    
    return output.getvalue()

if __name__ == "__main__":
    main()