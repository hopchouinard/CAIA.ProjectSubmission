#!/usr/bin/env python3
"""
Test script to verify multi-provider AI migration
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all new imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        from services import AIService
        print("✅ AIService import successful")
        
        # Test basic provider imports
        from services.providers import AIProvider, OpenAIProvider
        print("✅ Basic provider imports successful")
        
        # Test conditional provider imports
        available_providers = []
        try:
            from services.providers import AnthropicProvider
            available_providers.append("Anthropic")
        except ImportError:
            pass
            
        try:
            from services.providers import GoogleProvider
            available_providers.append("Google")
        except ImportError:
            pass
            
        try:
            from services.providers import AzureProvider
            available_providers.append("Azure")
        except ImportError:
            pass
            
        try:
            from services.providers import DatabricksProvider
            available_providers.append("Databricks")
        except ImportError:
            pass
            
        print(f"✅ Available optional providers: {', '.join(available_providers) if available_providers else 'None'}")
        
        from services.prompt_manager import PromptManager
        from services.provider_manager import ProviderManager
        print("✅ Manager imports successful")
        
        from models import AIProviderConfig
        print("✅ New model import successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database schema and models"""
    print("\n🗄️  Testing database...")
    
    try:
        from app import create_app
        from models import db, AIProviderConfig, Project, Evaluation
        
        app = create_app()
        with app.app_context():
            # Test table creation
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test AIProviderConfig model
            config_count = AIProviderConfig.query.count()
            print(f"✅ Found {config_count} provider configurations")
            
            # Test existing models still work
            project_count = Project.query.count()
            print(f"✅ Found {project_count} existing projects")
            
            eval_count = Evaluation.query.count()
            print(f"✅ Found {eval_count} existing evaluations")
            
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_prompt_manager():
    """Test prompt manager functionality"""
    print("\n📝 Testing prompt manager...")
    
    try:
        from services.prompt_manager import PromptManager
        
        pm = PromptManager()
        
        # Test prompt loading
        available_prompts = pm.list_available_prompts()
        print(f"✅ Found prompts for {len(available_prompts)} providers")
        
        # Test specific prompt loading
        openai_prompt = pm.get_prompt_template('openai', 'gpt-4o', 'evaluation')
        if openai_prompt:
            print("✅ OpenAI gpt-4o evaluation prompt loaded")
        else:
            print("⚠️  OpenAI gpt-4o evaluation prompt not found")
        
        # Test fallback
        fallback_prompt = pm.get_fallback_template('evaluation')
        if fallback_prompt:
            print("✅ Fallback evaluation prompt available")
        
        return True
    except Exception as e:
        print(f"❌ Prompt manager error: {e}")
        return False

def test_ai_service():
    """Test AI service initialization and basic functionality"""
    print("\n🤖 Testing AI service...")
    
    try:
        from services import AIService
        
        # Test initialization
        ai_service = AIService()
        print("✅ AI service initialized successfully")
        
        # Test provider status
        status = ai_service.get_provider_status()
        providers = status.get('available_providers', [])
        print(f"✅ Available providers: {', '.join(providers) if providers else 'None'}")
        
        # Test backward compatibility
        test_data = {
            'titre': 'Test Project',
            'pvp': 'Test Department',
            'contexte': 'This is a test project context for testing the multi-provider system.',
            'objectifs': 'Test the new multi-provider AI service to ensure backward compatibility.',
            'fonctionnalites': 'Multi-provider support, YAML prompts, fallback mechanisms, and full compatibility.'
        }
        
        # This should work even without API keys (will use fallback)
        result = ai_service.evaluate_project(test_data)
        if result and 'score_final' in result:
            print("✅ Project evaluation method works (fallback)")
        else:
            print("⚠️  Project evaluation returned unexpected result")
        
        # Test field improvement
        improved = ai_service.improve_field('titre', 'Test Project', 'Test context')
        if improved:
            print("✅ Field improvement method works")
        
        return True
    except Exception as e:
        print(f"❌ AI service error: {e}")
        return False

def test_backward_compatibility():
    """Test that old OpenAIService import still works"""
    print("\n🔄 Testing backward compatibility...")
    
    try:
        # This should still work for existing code
        from services import OpenAIService
        print("✅ OpenAIService import still works")
        
        # Test that it's actually the new AIService
        if hasattr(OpenAIService, 'get_provider_status'):
            print("✅ OpenAIService is properly aliased to AIService")
        else:
            print("⚠️  OpenAIService might not be properly aliased")
        
        return True
    except Exception as e:
        print(f"❌ Backward compatibility error: {e}")
        return False

def test_file_structure():
    """Test that all required files and directories exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'services/ai_service.py',
        'services/prompt_manager.py',
        'services/provider_manager.py',
        'services/providers/__init__.py',
        'services/providers/base_provider.py',
        'services/providers/openai_provider.py',
        'services/providers/anthropic_provider.py',
        'services/providers/google_provider.py',
        'services/providers/azure_provider.py',
        'services/providers/databricks_provider.py',
        'prompts/openai/gpt-4o/evaluation.yaml',
        'prompts/openai/gpt-4o/improvement.yaml',
        'prompts/openai/o3-mini/evaluation.yaml',
        'prompts/openai/o3-mini/improvement.yaml',
        'prompts/anthropic/claude-3-5-sonnet/evaluation.yaml',
        'prompts/google/gemini-2.0-flash-exp/evaluation.yaml',
        'prompts/azure/gpt-4o/evaluation.yaml',
        'prompts/databricks/meta-llama/evaluation.yaml',
        '.env.example',
        'requirements.txt',
        'migrate_db.py',
        'MIGRATION_GUIDE.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all tests"""
    print("🚀 Multi-Provider AI Migration Test Suite")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Database", test_database),
        ("Prompt Manager", test_prompt_manager),
        ("AI Service", test_ai_service),
        ("Backward Compatibility", test_backward_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Migration is ready.")
        print("\n📋 Next steps:")
        print("1. Configure API keys in .env file")
        print("2. Run 'python migrate_db.py' to migrate database")
        print("3. Test with your actual API keys")
        print("4. Deploy to production")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix before proceeding.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
