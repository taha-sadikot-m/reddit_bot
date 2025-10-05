"""
Quick Test Script - Test individual components of the Reddit Marketing Bot
Run this to verify all components are working correctly
"""

import asyncio
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Test data
TEST_BUSINESS_DESCRIPTION = """
CloudStock Pro is a comprehensive SaaS inventory management platform designed specifically for small to medium retail businesses. Our software provides:

• Real-time inventory tracking across multiple store locations
• Automated reorder notifications based on sales patterns and lead times
• Detailed analytics and reporting dashboards with customizable metrics
• Seamless integration with popular POS systems like Square, Shopify, and Clover
• Mobile app for on-the-go inventory checks and updates
• Barcode scanning capabilities for easy product management

Target customers: Small retail businesses (5-50 employees) currently struggling with manual inventory processes, frequent stockouts, or overstock situations. Perfect for boutiques, electronics stores, sporting goods retailers, bookstores, and similar businesses looking to optimize their inventory management and reduce carrying costs.

Key benefits include 40% reduction in stockouts, 25% decrease in excess inventory, and 3-5 hours saved per week on inventory management tasks.
"""

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title):
    """Print a formatted subsection header"""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

async def test_business_analyzer():
    """Test the Business Analyzer component"""
    print_section("TESTING BUSINESS ANALYZER")
    
    try:
        # You'll need to set your actual API key here for testing
        GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with actual key
        
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("❌ Please set your actual Gemini API key in the test script")
            return False
        
        from business_analyzer import BusinessAnalyzer
        
        print("🔄 Initializing Business Analyzer...")
        analyzer = BusinessAnalyzer(GEMINI_API_KEY)
        
        print("🔄 Analyzing test business description...")
        result = await analyzer.analyze_business(TEST_BUSINESS_DESCRIPTION)
        
        if result and isinstance(result, dict):
            print("✅ Business analysis successful!")
            print_subsection("Analysis Results")
            
            print(f"Product Summary: {result.get('product_summary', 'N/A')[:100]}...")
            print(f"Target Audience: {result.get('target_audience', 'N/A')[:100]}...")
            print(f"Industry: {result.get('industry_category', 'N/A')}")
            print(f"Key Benefits: {len(result.get('key_benefits', []))} identified")
            print(f"Recommended Subreddits: {len(result.get('recommended_subreddits', []))} found")
            
            return True
        else:
            print("❌ Business analysis failed - no valid result")
            return False
            
    except Exception as e:
        print(f"❌ Business analyzer test failed: {str(e)}")
        return False

async def test_reddit_analyzer():
    """Test the Reddit Analyzer component"""
    print_section("TESTING REDDIT ANALYZER")
    
    try:
        # You'll need to set your actual Reddit API credentials here
        REDDIT_CLIENT_ID = "YOUR_CLIENT_ID_HERE"  # Replace with actual client ID
        REDDIT_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"  # Replace with actual secret
        
        if REDDIT_CLIENT_ID == "YOUR_CLIENT_ID_HERE":
            print("❌ Please set your actual Reddit API credentials in the test script")
            return False
        
        from reddit_analyzer import RedditAnalyzer
        
        print("🔄 Initializing Reddit Analyzer...")
        analyzer = RedditAnalyzer(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)
        
        print("🔄 Testing subreddit access...")
        subreddit_info = analyzer.get_subreddit_info("entrepreneur")
        
        if subreddit_info and subreddit_info.get('name'):
            print("✅ Reddit API connection successful!")
            print_subsection("Subreddit Info")
            print(f"Name: {subreddit_info.get('name', 'N/A')}")
            print(f"Subscribers: {subreddit_info.get('subscribers', 0):,}")
            print(f"Title: {subreddit_info.get('title', 'N/A')}")
            
            # Test subreddit validation
            print("\n🔄 Testing subreddit validation...")
            test_subreddits = ["entrepreneur", "smallbusiness", "invalidsubreddit123"]
            valid_subreddits = analyzer.validate_subreddits(test_subreddits)
            print(f"Valid subreddits: {valid_subreddits}")
            
            return True
        else:
            print("❌ Reddit API test failed - could not access subreddit")
            return False
            
    except Exception as e:
        print(f"❌ Reddit analyzer test failed: {str(e)}")
        return False

async def test_ai_response_generator():
    """Test the AI Response Generator component"""
    print_section("TESTING AI RESPONSE GENERATOR")
    
    try:
        # You'll need to set your actual API key here
        GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with actual key
        
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("❌ Please set your actual Gemini API key in the test script")
            return False
        
        from ai_response_generator import AIResponseGenerator
        
        print("🔄 Initializing AI Response Generator...")
        generator = AIResponseGenerator(GEMINI_API_KEY)
        
        # Test question data
        test_question = {
            'title': 'Best inventory management software for small retail business?',
            'selftext': 'I run a small electronics store and I\'m tired of tracking inventory manually. What are some good software options that won\'t break the bank? Looking for something that can handle multiple locations and integrates with Square POS.',
            'subreddit': 'smallbusiness',
            'score': 15,
            'num_comments': 8,
            'created_utc': 1699123456,
            'url': 'https://reddit.com/r/smallbusiness/example'
        }
        
        # Test business info
        test_business_info = {
            'product_summary': 'CloudStock Pro - inventory management software for small retail businesses',
            'key_benefits': ['Real-time tracking', 'Automated reordering', 'POS integration'],
            'target_audience': 'Small retail business owners',
            'use_cases': ['Multi-location inventory', 'Automated reordering', 'Analytics'],
            'marketing_angles': ['Cost-effective solution', 'Time-saving automation']
        }
        
        print("🔄 Generating test response...")
        response = await generator.generate_response(
            question_data=test_question,
            business_info=test_business_info,
            response_style="Professional"
        )
        
        if response and len(response) > 50:
            print("✅ Response generation successful!")
            print_subsection("Generated Response")
            print(f"{response[:200]}...")
            
            # Test quality analysis
            print("\n🔄 Testing quality analysis...")
            quality = generator.analyze_response_quality(response, test_question)
            print(f"Overall Quality Score: {quality.get('overall_score', 0):.2f}")
            print(f"Helpfulness: {quality.get('helpfulness_score', 0):.2f}")
            print(f"Naturalness: {quality.get('naturalness_score', 0):.2f}")
            print(f"Marketing Subtlety: {quality.get('marketing_subtlety', 0):.2f}")
            
            return True
        else:
            print("❌ Response generation failed - response too short or empty")
            return False
            
    except Exception as e:
        print(f"❌ AI response generator test failed: {str(e)}")
        return False

async def test_workflow_integration():
    """Test the complete workflow integration"""
    print_section("TESTING WORKFLOW INTEGRATION")
    
    try:
        # Check if API keys are set
        GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
        REDDIT_CLIENT_ID = "YOUR_CLIENT_ID_HERE"
        REDDIT_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
        
        if (GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE" or 
            REDDIT_CLIENT_ID == "YOUR_CLIENT_ID_HERE"):
            print("❌ Please set actual API credentials for workflow testing")
            return False
        
        from workflow_manager import WorkflowManager
        
        print("🔄 Initializing Workflow Manager...")
        workflow = WorkflowManager(
            gemini_api_key=GEMINI_API_KEY,
            reddit_client_id=REDDIT_CLIENT_ID,
            reddit_client_secret=REDDIT_CLIENT_SECRET
        )
        
        print("🔄 Testing component connectivity...")
        test_results = await workflow.test_components()
        
        print_subsection("Component Test Results")
        for component, status in test_results.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {component}: {'PASS' if status else 'FAIL'}")
        
        if all(test_results.values()):
            print("\n✅ All components working correctly!")
            
            print("\n🔄 Testing configuration validation...")
            config = {
                "max_questions": 5,
                "subreddit_limit": 3,
                "response_style": "Professional",
                "min_upvotes": 1,
                "days_back": 7
            }
            
            errors = workflow.validate_configuration(config)
            if not errors:
                print("✅ Configuration validation passed!")
                return True
            else:
                print(f"❌ Configuration errors: {errors}")
                return False
        else:
            print("\n❌ Some components failed - check your API credentials")
            return False
            
    except Exception as e:
        print(f"❌ Workflow integration test failed: {str(e)}")
        return False

def test_imports():
    """Test that all required modules can be imported"""
    print_section("TESTING IMPORTS")
    
    modules_to_test = [
        ('streamlit', 'Streamlit UI framework'),
        ('pandas', 'Data manipulation'),
        ('PyPDF2', 'PDF processing'),
        ('praw', 'Reddit API'),
        ('google.generativeai', 'Google Gemini API'),
        ('langchain', 'LangChain framework'),
        ('langchain_google_genai', 'LangChain Google integration'),
        ('langgraph', 'LangGraph workflow management'),
        ('plotly', 'Data visualization')
    ]
    
    success_count = 0
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}: {description}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module_name}: {description} - {str(e)}")
    
    print(f"\n📊 Import Results: {success_count}/{len(modules_to_test)} modules successfully imported")
    
    if success_count == len(modules_to_test):
        print("✅ All required modules are available!")
        return True
    else:
        print("❌ Some modules are missing. Run: pip install -r requirements.txt")
        return False

def test_file_structure():
    """Test that all required files are present"""
    print_section("TESTING FILE STRUCTURE")
    
    required_files = [
        ('app.py', 'Basic Streamlit app'),
        ('enhanced_app.py', 'Enhanced Streamlit app'),
        ('business_analyzer.py', 'Business analysis module'),
        ('reddit_analyzer.py', 'Reddit API module'),
        ('ai_response_generator.py', 'AI response generation'),
        ('workflow_manager.py', 'Workflow orchestration'),
        ('requirements.txt', 'Dependencies list'),
        ('README.md', 'Documentation'),
        ('.env.template', 'Environment template')
    ]
    
    success_count = 0
    
    for filename, description in required_files:
        filepath = os.path.join(current_dir, filename)
        if os.path.exists(filepath):
            print(f"✅ {filename}: {description}")
            success_count += 1
        else:
            print(f"❌ {filename}: {description} - File not found")
    
    print(f"\n📊 File Structure: {success_count}/{len(required_files)} files found")
    
    if success_count == len(required_files):
        print("✅ All required files are present!")
        return True
    else:
        print("❌ Some files are missing")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Reddit Marketing Bot Component Tests")
    print(f"📁 Testing in directory: {current_dir}")
    
    test_results = {}
    
    # Test 1: File Structure
    test_results['file_structure'] = test_file_structure()
    
    # Test 2: Imports
    test_results['imports'] = test_imports()
    
    # Only run API tests if files and imports are OK
    if test_results['file_structure'] and test_results['imports']:
        print("\n⚠️  API TESTS REQUIRE ACTUAL API KEYS")
        print("Please edit this script and add your API keys to test the following components:")
        print("- Business Analyzer (requires Gemini API key)")
        print("- Reddit Analyzer (requires Reddit API credentials)")
        print("- AI Response Generator (requires Gemini API key)")
        print("- Workflow Integration (requires both)")
        
        proceed = input("\nDo you want to proceed with API tests? (y/N): ").lower().strip()
        
        if proceed == 'y':
            # Test 3: Business Analyzer
            test_results['business_analyzer'] = await test_business_analyzer()
            
            # Test 4: Reddit Analyzer
            test_results['reddit_analyzer'] = await test_reddit_analyzer()
            
            # Test 5: AI Response Generator
            test_results['ai_response_generator'] = await test_ai_response_generator()
            
            # Test 6: Workflow Integration
            test_results['workflow_integration'] = await test_workflow_integration()
        else:
            print("⏭️  Skipping API tests")
    
    # Print final results
    print_section("FINAL TEST RESULTS")
    
    for test_name, result in test_results.items():
        status_icon = "✅" if result else "❌"
        status_text = "PASS" if result else "FAIL"
        print(f"{status_icon} {test_name.replace('_', ' ').title()}: {status_text}")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\n📊 Overall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your Reddit Marketing Bot is ready to use!")
        print("\nNext steps:")
        print("1. Copy .env.template to .env and add your API keys")
        print("2. Run: streamlit run enhanced_app.py")
    else:
        print("\n⚠️  Some tests failed. Please address the issues above.")
        
        if not test_results.get('imports', True):
            print("\n💡 To fix import issues:")
            print("   pip install -r requirements.txt")
        
        if not test_results.get('file_structure', True):
            print("\n💡 Ensure all required files are in the same directory")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
