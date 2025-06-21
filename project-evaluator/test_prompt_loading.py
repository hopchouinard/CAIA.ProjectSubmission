import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.prompt_manager import PromptManager
from pathlib import Path
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_prompt_loading():
    print("Testing detailed prompt loading...")
    
    # Initialize prompt manager
    pm = PromptManager()
    
    print(f"Prompts directory: {pm.prompts_dir}")
    print(f"Directory exists: {pm.prompts_dir.exists()}")
    
    # Check the exact path being constructed
    provider = "openai"
    model = "gpt-4.1-2025-04-14"
    prompt_type = "evaluation"
    
    prompt_file = pm.prompts_dir / provider / model / f"{prompt_type}.yaml"
    print(f"Constructed path: {prompt_file}")
    print(f"File exists: {prompt_file.exists()}")
    
    if prompt_file.exists():
        print("File exists, trying to load...")
        template = pm._load_prompt_file(prompt_file)
        print(f"Loaded template: {template is not None}")
        
        if template:
            print(f"Template metadata: {template.get('metadata', {})}")
            print(f"Has user_prompt_template: {'user_prompt_template' in template}")
        else:
            print("Template is None - check validation")
            
            # Try loading raw YAML
            import yaml
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    raw_content = yaml.safe_load(f)
                print(f"Raw YAML content keys: {list(raw_content.keys()) if raw_content else 'None'}")
                
                # Test validation
                is_valid = pm._validate_prompt_template(raw_content)
                print(f"Template validation: {is_valid}")
                
            except Exception as e:
                print(f"Error loading raw YAML: {e}")
    else:
        print("File does not exist!")
        
        # List what's actually in the directory
        model_dir = pm.prompts_dir / provider / model
        if model_dir.exists():
            print(f"Model directory contents: {list(model_dir.iterdir())}")
        else:
            print(f"Model directory doesn't exist: {model_dir}")
            
            provider_dir = pm.prompts_dir / provider
            if provider_dir.exists():
                print(f"Provider directory contents: {list(provider_dir.iterdir())}")
            else:
                print(f"Provider directory doesn't exist: {provider_dir}")

if __name__ == "__main__":
    test_prompt_loading()
