#!/usr/bin/env python3
"""
Reddit Marketing Bot - Main Entry Point
Professional Reddit marketing automation with AI-powered response generation

Usage:
    python main.py --mode=test       # Run test mode with mock data
    python main.py --mode=analyze    # Analyze business only
    python main.py --mode=full       # Run complete workflow
    python main.py --mode=streamlit  # Launch Streamlit app
"""

import sys
import os
import argparse
import asyncio
from pathlib import Path

# Add src directory to path for imports
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Now we can import our modules
from src.core import WorkflowManager
from config import config

async def run_test_mode():
    """Run in test mode with mock data"""
    print("🧪 Running Reddit Marketing Bot in Test Mode")
    
    # Test business description
    test_business = """
    We offer a SaaS platform that helps small businesses manage their inventory efficiently. 
    Our tool provides real-time tracking, automated reordering, and detailed analytics. 
    Target customers are small to medium retail businesses looking to optimize their stock management.
    """
    
    try:
        # Get configurations
        reddit_config = config.get_reddit_config()
        ai_config = config.get_ai_config()
        
        # Initialize workflow manager
        workflow_manager = WorkflowManager(
            gemini_api_key=ai_config["gemini_api_key"],
            reddit_client_id=reddit_config["client_id"],
            reddit_client_secret=reddit_config["client_secret"],
            reddit_username=reddit_config["username"],
            reddit_password=reddit_config["password"]
        )
        
        # Run workflow
        results = await workflow_manager.run_complete_workflow(
            business_description=test_business,
            max_questions=5,
            subreddit_limit=3,
            response_style="Casual",
            auto_post=True,
            dry_run=True  # Always dry run in test mode
        )
        
        # Display results
        print(f"\n✅ Test completed successfully!")
        print(f"📊 Questions found: {results['workflow_summary']['total_questions_found']}")
        print(f"📝 Responses generated: {results['workflow_summary']['responses_generated']}")
        print(f"🎯 Success: {results['workflow_summary']['success']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def run_streamlit_app():
    """Launch the Streamlit application"""
    print("🚀 Launching Reddit Marketing Bot Streamlit App...")
    
    import subprocess
    import sys
    
    try:
        # Launch the enhanced posting app
        app_path = project_root / "src" / "apps" / "enhanced_posting_app.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped by user")
    except Exception as e:
        print(f"❌ Failed to launch Streamlit app: {str(e)}")

async def run_analysis_mode(business_description: str):
    """Run business analysis only"""
    print("📊 Running Business Analysis Mode")
    
    try:
        from src.core import BusinessAnalyzer
        ai_config = config.get_ai_config()
        
        analyzer = BusinessAnalyzer(ai_config["gemini_api_key"])
        analysis = await analyzer.analyze_business(business_description)
        
        print("\n📋 Business Analysis Results:")
        print(f"Product: {analysis.get('product_summary', 'N/A')}")
        print(f"Target Audience: {analysis.get('target_audience', 'N/A')}")
        print(f"Industry: {analysis.get('industry_category', 'N/A')}")
        print(f"Recommended Subreddits: {analysis.get('recommended_subreddits', [])}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return None

async def run_full_mode(business_description: str, **kwargs):
    """Run complete workflow"""
    print("🚀 Running Full Reddit Marketing Workflow")
    
    try:
        # Get configurations
        reddit_config = config.get_reddit_config()
        ai_config = config.get_ai_config()
        
        # Initialize workflow manager
        workflow_manager = WorkflowManager(
            gemini_api_key=ai_config["gemini_api_key"],
            reddit_client_id=reddit_config["client_id"],
            reddit_client_secret=reddit_config["client_secret"],
            reddit_username=reddit_config["username"],
            reddit_password=reddit_config["password"]
        )
        
        # Run workflow with provided parameters
        results = await workflow_manager.run_complete_workflow(
            business_description=business_description,
            **kwargs
        )
        
        return results
        
    except Exception as e:
        print(f"❌ Full workflow failed: {str(e)}")
        return None

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Reddit Marketing Bot")
    parser.add_argument("--mode", choices=["test", "analyze", "full", "streamlit"], 
                       default="test", help="Operation mode")
    parser.add_argument("--business", type=str, help="Business description")
    parser.add_argument("--max-questions", type=int, default=20, help="Maximum questions to find")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run mode")
    parser.add_argument("--auto-post", action="store_true", help="Enable auto-posting")
    
    args = parser.parse_args()
    
    print("🤖 Reddit Marketing Bot")
    print("=" * 50)
    
    # Validate configuration
    validation = config.validate_config()
    print(f"📊 Configuration Status:")
    print(f"   Reddit API: {'✅' if validation['reddit'] else '❌'}")
    print(f"   AI API: {'✅' if validation['ai'] else '❌'}")
    
    if not validation['overall']:
        print("⚠️  Configuration issues detected. Check your config files.")
    
    # Run based on mode
    if args.mode == "test":
        asyncio.run(run_test_mode())
    
    elif args.mode == "streamlit":
        run_streamlit_app()
    
    elif args.mode == "analyze":
        if not args.business:
            print("❌ Business description required for analysis mode")
            print("Usage: python main.py --mode=analyze --business='Your business description'")
            return
        asyncio.run(run_analysis_mode(args.business))
    
    elif args.mode == "full":
        if not args.business:
            print("❌ Business description required for full mode")
            print("Usage: python main.py --mode=full --business='Your business description'")
            return
        
        kwargs = {
            "max_questions": args.max_questions,
            "dry_run": args.dry_run,
            "auto_post": args.auto_post
        }
        
        results = asyncio.run(run_full_mode(args.business, **kwargs))
        
        if results:
            print(f"\n✅ Workflow completed!")
            print(f"📊 Results: {results['workflow_summary']}")

if __name__ == "__main__":
    main()