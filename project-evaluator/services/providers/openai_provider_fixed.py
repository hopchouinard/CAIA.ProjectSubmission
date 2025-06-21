"""
OpenAI provider implementation
"""
import openai
import json
import logging
from typing import Dict, Any, List
from .base_provider import AIProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(AIProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI provider"""
        super().__init__(config)
        
        if self.is_configured():
            # Only include organization if it's specifically provided and not empty
            client_kwargs = {
                'api_key': config.get('api_key')
            }
            
            organization = config.get('organization')
            if organization and organization.strip() and organization != 'optional-org-id':
                client_kwargs['organization'] = organization
                
            self.client = openai.OpenAI(**client_kwargs)
        else:
            self.client = None
    
    def evaluate_project(self, project_data: Dict[str, Any], prompt_template: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a project using OpenAI"""
        if not self.client:
            logger.error("OpenAI client not initialized")
            return self._get_fallback_evaluation()
        
        try:
            # Get model and parameters from template
            model = prompt_template.get('metadata', {}).get('model', 'gpt-4o')
            parameters = prompt_template.get('parameters', {})
            
            # Build messages
            messages = self._build_messages(project_data, prompt_template)
            
            # Handle special models (o3/o3-mini thinking models)
            if model.startswith('o3') or 'mini-2025' in model:
                # Thinking models don't support system messages or temperature
                messages = [msg for msg in messages if msg['role'] != 'system']
                parameters = {k: v for k, v in parameters.items() if k != 'temperature'}
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **parameters
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure valid JSON
            content = self._clean_json_response(content)
            
            result = json.loads(content)
            
            # Get weights from Flask config (will be injected by the main service)
            weights = self.config.get('weights', {
                'valeur_business': 0.25,
                'faisabilite_technique': 0.20,
                'effort_requis': 0.15,
                'niveau_risque': 0.15,
                'urgence': 0.15,
                'alignement_strategique': 0.10
            })
            
            return self._validate_evaluation_result(result, weights)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_evaluation()
    
    def improve_field(self, field_name: str, field_content: str, project_context: str, 
                     prompt_template: Dict[str, Any]) -> str:
        """Improve a field using OpenAI"""
        if not self.client:
            logger.error("OpenAI client not initialized")
            return field_content
        
        try:
            # Get model and parameters from template
            model = prompt_template.get('metadata', {}).get('model', 'gpt-4o')
            parameters = prompt_template.get('parameters', {})
            
            # Substitute variables in prompt
            variables = {
                'field_name': field_name,
                'field_content': field_content,
                'project_context': project_context
            }
            
            messages = []
            
            # Add system message if supported and present
            if not (model.startswith('o3') or 'mini-2025' in model):
                system_msg = prompt_template.get('system_message', '')
                if system_msg:
                    messages.append({
                        'role': 'system',
                        'content': system_msg
                    })
            
            # Add user message
            user_prompt = self._substitute_template_variables(
                prompt_template.get('user_prompt_template', ''), 
                variables
            )
            messages.append({
                'role': 'user',
                'content': user_prompt
            })
            
            # Handle special models
            if model.startswith('o3') or 'mini-2025' in model:
                parameters = {k: v for k, v in parameters.items() if k != 'temperature'}
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **parameters
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error improving field {field_name}: {e}")
            return field_content
    
    def supports_feature(self, feature: str) -> bool:
        """Check if OpenAI supports a feature"""
        supported_features = {
            'system_messages': True,
            'temperature': True,
            'max_tokens': True,
            'top_p': True,
            'frequency_penalty': True,
            'presence_penalty': True,
            'thinking_mode': True  # o1/o3 models
        }
        return supported_features.get(feature, False)
    
    def get_available_models(self) -> List[str]:
        """Get available OpenAI models"""
        return [
            'gpt-4.1-2025-04-14',
            'gpt-4.1-mini-2025-04-14', 
            'o3-2025-04-16',
            'o3-mini-2025-04-16',
            'gpt-4o',
            'gpt-4o-mini',
            'gpt-4-turbo',
            'gpt-4',
            'gpt-3.5-turbo',
            'o1-preview',
            'o1-mini'
        ]
    
    def _validate_config(self) -> bool:
        """Validate OpenAI configuration"""
        api_key = self.config.get('api_key')
        return bool(api_key and api_key.startswith('sk-'))
    
    def _build_messages(self, project_data: Dict[str, Any], prompt_template: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages array for OpenAI API"""
        messages = []
        
        model = prompt_template.get('metadata', {}).get('model', 'gpt-4o')
        
        # Add system message if supported
        if not (model.startswith('o3') or 'mini-2025' in model):
            system_msg = prompt_template.get('system_message', '')
            if system_msg:
                messages.append({
                    'role': 'system',
                    'content': system_msg
                })
        
        # Add user message with project data substituted
        user_prompt = self._substitute_template_variables(
            prompt_template.get('user_prompt_template', ''), 
            project_data
        )
        messages.append({
            'role': 'user',
            'content': user_prompt
        })
        
        return messages
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON response from OpenAI"""
        # Remove code block markers
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
