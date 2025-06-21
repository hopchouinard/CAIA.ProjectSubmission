#!/usr/bin/env python3
"""Simple test to check basic imports"""

print("🔧 Starting simple import test...")

try:
    print("1. Testing basic Python imports...")
    import sys
    import os
    print("✅ Basic imports ok")
    
    print("2. Testing services import...")
    from services import AIService
    print("✅ AIService import ok")
    
    print("3. Testing provider imports...")
    from services.providers import AIProvider, OpenAIProvider
    print("✅ Basic provider imports ok")
    
    print("4. Testing conditional provider imports...")
    try:
        from services.providers import GoogleProvider
        print("✅ Google provider available")
    except ImportError as e:
        print(f"⚠️ Google provider not available: {e}")
    
    try:
        from services.providers import AnthropicProvider
        print("✅ Anthropic provider available")
    except ImportError as e:
        print(f"⚠️ Anthropic provider not available: {e}")
        
    print("5. Testing manager imports...")
    from services.prompt_manager import PromptManager
    from services.provider_manager import ProviderManager
    print("✅ Manager imports ok")
    
    print("6. Testing model imports...")
    from models import AIProviderConfig
    print("✅ Model imports ok")
    
    print("🎉 All basic imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
