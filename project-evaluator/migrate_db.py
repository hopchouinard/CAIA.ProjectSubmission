#!/usr/bin/env python3
"""
Database migration script for adding AIProviderConfig table
Run this script to migrate from single-provider to multi-provider architecture
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, AIProviderConfig

def migrate_database():
    """Migrate database to add AIProviderConfig table"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Starting database migration...")
        
        try:
            # Create the new table
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if we need to add default provider configurations
            existing_configs = AIProviderConfig.query.count()
            
            if existing_configs == 0:
                print("📝 Adding default provider configurations...")
                
                # Add default OpenAI configuration
                openai_config = AIProviderConfig(
                    provider='openai',
                    model='gpt-4o',
                    is_active=True,
                    priority=1
                )
                openai_config.set_config_data({
                    'description': 'Default OpenAI GPT-4o configuration',
                    'supports_system_messages': True,
                    'supports_temperature': True,
                    'supports_thinking_mode': False
                })
                db.session.add(openai_config)
                
                # Add o3-mini configuration (if user wants to use thinking models)
                o3_config = AIProviderConfig(
                    provider='openai',
                    model='o3-mini',
                    is_active=False,
                    priority=2
                )
                o3_config.set_config_data({
                    'description': 'OpenAI o3-mini thinking model',
                    'supports_system_messages': False,
                    'supports_temperature': False,
                    'supports_thinking_mode': True
                })
                db.session.add(o3_config)
                
                # Add Anthropic configuration (inactive by default)
                anthropic_config = AIProviderConfig(
                    provider='anthropic',
                    model='claude-3-5-sonnet-20241022',
                    is_active=False,
                    priority=3
                )
                anthropic_config.set_config_data({
                    'description': 'Anthropic Claude 3.5 Sonnet',
                    'supports_system_messages': True,
                    'supports_temperature': True,
                    'supports_thinking_mode': False
                })
                db.session.add(anthropic_config)
                
                # Add Google configuration (inactive by default)
                google_config = AIProviderConfig(
                    provider='google',
                    model='gemini-2.0-flash-exp',
                    is_active=False,
                    priority=4
                )
                google_config.set_config_data({
                    'description': 'Google Gemini 2.0 Flash',
                    'supports_system_messages': True,
                    'supports_temperature': True,
                    'supports_thinking_mode': False
                })
                db.session.add(google_config)
                
                # Add Azure configuration (inactive by default)
                azure_config = AIProviderConfig(
                    provider='azure',
                    model='gpt-4o',
                    is_active=False,
                    priority=5
                )
                azure_config.set_config_data({
                    'description': 'Azure OpenAI GPT-4o',
                    'supports_system_messages': True,
                    'supports_temperature': True,
                    'supports_thinking_mode': False
                })
                db.session.add(azure_config)
                
                # Add Databricks configuration (inactive by default)
                databricks_config = AIProviderConfig(
                    provider='databricks',
                    model='meta-llama/Llama-3.1-70B-Instruct',
                    is_active=False,
                    priority=6
                )
                databricks_config.set_config_data({
                    'description': 'Databricks Meta Llama 3.1 70B',
                    'supports_system_messages': True,
                    'supports_temperature': True,
                    'supports_thinking_mode': False
                })
                db.session.add(databricks_config)
                
                db.session.commit()
                print("✅ Default provider configurations added")
            else:
                print(f"ℹ️  Found {existing_configs} existing provider configurations")
            
            print("🎉 Migration completed successfully!")
            print("\n📋 Next steps:")
            print("1. Configure API keys in your .env file")
            print("2. Activate additional providers via the admin interface")
            print("3. Test the multi-provider functionality")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    print("🚀 Multi-Provider AI Service Migration")
    print("=" * 50)
    
    if migrate_database():
        print("\n✅ Migration successful!")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
