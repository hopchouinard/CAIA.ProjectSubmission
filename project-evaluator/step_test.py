#!/usr/bin/env python3
"""Ultra simple test"""

print("Testing step by step...")

print("1. Testing prompt manager...")
try:
    from services.prompt_manager import PromptManager
    print("✅ PromptManager import ok")
except Exception as e:
    print(f"❌ PromptManager error: {e}")
    import traceback
    traceback.print_exc()

print("2. Testing provider manager...")
try:
    from services.provider_manager import ProviderManager
    print("✅ ProviderManager import ok")
except Exception as e:
    print(f"❌ ProviderManager error: {e}")
    import traceback
    traceback.print_exc()

print("3. Testing ai service...")
try:
    from services.ai_service import AIService
    print("✅ AIService import ok")
except Exception as e:
    print(f"❌ AIService error: {e}")
    import traceback
    traceback.print_exc()
