#!/usr/bin/env python3
"""
Quick Setup Script - Reddit Marketing Bot
Validates the new organized structure and provides setup guidance
"""

import os
import sys
from pathlib import Path

def check_structure():
    """Check if the new folder structure is properly set up"""
    print("🔍 Checking Reddit Marketing Bot Structure...")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    
    # Required directories
    required_dirs = [
        "src",
        "src/core", 
        "src/apps",
        "config",
        "tests",
        "tests/unit",
        "tests/integration", 
        "docs",
        "scripts",
        "data",
        "data/outputs"
    ]
    
    # Required files
    required_files = [
        "src/__init__.py",
        "src/core/__init__.py",
        "src/core/workflow_manager.py",
        "src/core/business_analyzer.py",
        "src/core/reddit_analyzer.py",
        "src/core/ai_response_generator.py", 
        "src/core/reddit_poster.py",
        "config/__init__.py",
        "config/reddit_config.py",
        "config/ai_config.py",
        "config/app_config.py",
        "main.py"
    ]
    
    print("📁 Directory Structure:")
    all_dirs_exist = True
    for directory in required_dirs:
        dir_path = project_root / directory
        status = "✅" if dir_path.exists() else "❌"
        print(f"   {status} {directory}/")
        if not dir_path.exists():
            all_dirs_exist = False
    
    print("\n📄 Required Files:")
    all_files_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        status = "✅" if full_path.exists() else "❌"
        print(f"   {status} {file_path}")
        if not full_path.exists():
            all_files_exist = False
    
    print("\n📊 Structure Summary:")
    if all_dirs_exist and all_files_exist:
        print("   ✅ All required directories and files present")
        print("   🎉 Project structure is properly organized!")
        return True
    else:
        print("   ❌ Some required directories or files are missing")
        print("   🔧 Please run the organization script again")
        return False

def test_imports():
    """Test if imports work with the new structure"""
    print("\n🧪 Testing Import Structure...")
    print("-" * 30)
    
    # Add src to path
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Test config import
        from config import config
        print("   ✅ Configuration system")
        
        # Test core imports
        from src.core import WorkflowManager
        print("   ✅ WorkflowManager")
        
        from src.core import BusinessAnalyzer
        print("   ✅ BusinessAnalyzer")
        
        from src.core import RedditAnalyzer  
        print("   ✅ RedditAnalyzer")
        
        from src.core import AIResponseGenerator
        print("   ✅ AIResponseGenerator")
        
        from src.core import RedditPoster
        print("   ✅ RedditPoster")
        
        print("   🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {str(e)}")
        return False

def show_usage_guide():
    """Show how to use the organized structure"""
    print("\n🚀 Usage Guide:")
    print("-" * 20)
    print("1. 🧪 Test Mode:")
    print("   python main.py --mode=test")
    print("")
    print("2. 🌐 Launch Web Interface:")
    print("   python main.py --mode=streamlit")
    print("")
    print("3. 📊 Business Analysis Only:")
    print("   python main.py --mode=analyze --business='Your business description'")
    print("")
    print("4. 🎯 Full Workflow:")
    print("   python main.py --mode=full --business='Your business' --auto-post")
    print("")
    print("5. 🧪 Run Tests:")
    print("   python tests/test_posting_system.py")
    print("   python tests/test_reddit_auth.py")
    print("")
    print("6. 📚 Check Documentation:")
    print("   See docs/PROJECT_STRUCTURE.md for complete guide")

def main():
    """Main setup check function"""
    print("🤖 Reddit Marketing Bot - Structure Validation")
    print("=" * 60)
    
    # Check structure
    structure_ok = check_structure()
    
    # Test imports
    imports_ok = test_imports()
    
    # Overall status
    print("\n🎯 Overall Status:")
    print("-" * 20)
    
    if structure_ok and imports_ok:
        print("✅ Project structure is properly organized and functional!")
        print("🚀 Your Reddit Marketing Bot is ready to use!")
        show_usage_guide()
    else:
        print("❌ Some issues found with the project structure")
        print("🔧 Please check the errors above and fix them")
        
        if not structure_ok:
            print("\n💡 Tips:")
            print("- Ensure all files were moved correctly")
            print("- Check if any files are missing")
            
        if not imports_ok:
            print("- Check Python path configuration")
            print("- Ensure __init__.py files are present")
    
    print(f"\n📍 Project Root: {Path(__file__).parent}")
    print("📚 See docs/PROJECT_STRUCTURE.md for detailed documentation")

if __name__ == "__main__":
    main()