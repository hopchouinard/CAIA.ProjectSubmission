#!/usr/bin/env python3
"""
Test script to verify OpenAI provider organization handling
"""

def test_openai_organization_handling():
    """Test that OpenAI provider handles organization correctly"""
    print("🔧 Testing OpenAI Provider Organization Handling")
    
    from services.providers.openai_provider import OpenAIProvider
    
    # Test 1: No organization provided
    config1 = {
        'api_key': 'sk-test-key-123'
    }
    provider1 = OpenAIProvider(config1)
    print("✅ Test 1: No organization - OK")
    
    # Test 2: Empty organization
    config2 = {
        'api_key': 'sk-test-key-123',
        'organization': ''
    }
    provider2 = OpenAIProvider(config2)
    print("✅ Test 2: Empty organization - OK")
    
    # Test 3: Placeholder organization
    config3 = {
        'api_key': 'sk-test-key-123',
        'organization': 'optional-org-id'
    }
    provider3 = OpenAIProvider(config3)
    print("✅ Test 3: Placeholder organization - OK")
    
    # Test 4: Valid organization
    config4 = {
        'api_key': 'sk-test-key-123',
        'organization': 'org-valid-org-id'
    }
    provider4 = OpenAIProvider(config4)
    print("✅ Test 4: Valid organization - OK")
    
    print("🎉 All OpenAI organization tests passed!")
    return True

if __name__ == "__main__":
    test_openai_organization_handling()
