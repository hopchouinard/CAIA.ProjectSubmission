#!/usr/bin/env python3
"""
Test script to verify configuration and prompt loading
"""
import os
from services.ai_service import AIService
from services.prompt_manager import PromptManager

def test_config():
    """Test configuration loading"""
    print("Testing configuration loading...")
    
    # Test configuration loading
    ai_service = AIService()
    print('AI Service Config:')
    print(f'  Default Provider: {ai_service.config["default_provider"]}')
    print(f'  Default Model: {ai_service.config["default_model"]}')
    print()
    
    # Test prompt template loading
    prompt_manager = PromptManager()
    template = prompt_manager.get_prompt_template('openai', 'gpt-4.1-2025-04-14', 'evaluation')
    if template:
        print('✅ Prompt template found for openai/gpt-4.1-2025-04-14/evaluation')
        print(f'  Provider: {template["metadata"]["provider"]}')
        print(f'  Model: {template["metadata"]["model"]}')
        print(f'  Type: {template["metadata"]["prompt_type"]}')
    else:
        print('❌ Prompt template NOT found for openai/gpt-4.1-2025-04-14/evaluation')
    
    # Test all available models
    print('\nTesting all available model templates:')
    models = ['gpt-4.1-2025-04-14', 'gpt-4.1-mini-2025-04-14', 'o3-2025-04-16', 'o4-mini-2025-04-16']
    for model in models:
        template = prompt_manager.get_prompt_template('openai', model, 'evaluation')
        status = '✅' if template else '❌'
        print(f'  {status} openai/{model}/evaluation')

if __name__ == '__main__':
    test_config()
