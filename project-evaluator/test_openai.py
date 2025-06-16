#!/usr/bin/env python3
"""
Test script to verify OpenAI service functionality
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.openai_service import OpenAIService
import logging

logging.basicConfig(level=logging.INFO)

def test_openai_service():
    """Test the OpenAI service initialization and basic functionality"""
    
    # Test data
    test_project = {
        'titre': 'Test Project',
        'pvp': 'Test Department',
        'contexte': 'This is a test project for evaluating the OpenAI service',
        'objectifs': 'Test the evaluation functionality',
        'fonctionnalites': 'Basic testing features'
    }
    
    try:
        # Get API key from environment
        from config import Config
        api_key = Config.OPENAI_API_KEY
        
        if not api_key or api_key == "your-openai-api-key-here":
            print("❌ OpenAI API key not configured in .env file")
            return False
        
        print("✅ OpenAI API key found")
        
        # Initialize service
        service = OpenAIService(api_key)
        print("✅ OpenAI service initialized successfully")
        
        # Test fallback evaluation (doesn't require API call)
        fallback = service._get_fallback_evaluation()
        print("✅ Fallback evaluation method works")
        print(f"   Sample score: {fallback['score_final']}")
        
        print("\n🔧 OpenAI service is properly configured for legacy API (0.28.x)")
        print("   To test actual API calls, try using the reevaluate function in the web interface")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAI service: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing OpenAI Service Compatibility...")
    success = test_openai_service()
    sys.exit(0 if success else 1)
