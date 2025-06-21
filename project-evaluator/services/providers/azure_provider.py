"""
Azure OpenAI provider implementation
"""
import openai
import json
import logging
from typing import Dict, Any, List
from .base_provider import AIProvider

logger = logging.getLogger(__name__)

class AzureProvider(AIProvider):
    """Azure OpenAI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Azure OpenAI provider"""
        super().__init__(config)
        
        if self.is_configured():
            self.client = openai.AzureOpenAI(
                api_key=config.get('api_key'),
                azure_endpoint=config.get('endpoint'),
                api_version=config.get('api_version', '2024-02-15-preview')
            )
        else:
            self.client = None
    
    def evaluate_project(self, project_data: Dict[str, Any], prompt_template: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a project using Azure OpenAI"""
        if not self.client:
            logger.error("Azure OpenAI client not initialized")
            return self._get_fallback_evaluation()
        
        try:
            # Get deployment name (model) and parameters from template
            deployment_name = prompt_template.get('metadata', {}).get('model', 'gpt-4')
            parameters = prompt_template.get('parameters', {})
            
            # Build messages
            messages = self._build_messages(project_data, prompt_template)
            
            response = self.client.chat.completions.create(
                model=deployment_name,  # This is the deployment name in Azure
                messages=messages,
                **parameters
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure valid JSON
            content = self._clean_json_response(content)
            
            result = json.loads(content)
            
            # Get weights from Flask config
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
            logger.error(f"Azure OpenAI API error: {e}")
            return self._get_fallback_evaluation()
    
    def improve_field(self, field_name: str, field_content: str, project_context: str, 
                     prompt_template: Dict[str, Any]) -> str:
        """Improve a field using Azure OpenAI"""
        if not self.client:
            logger.error("Azure OpenAI client not initialized")
            return field_content
        
        try:
            # Get deployment name and parameters from template
            deployment_name = prompt_template.get('metadata', {}).get('model', 'gpt-4')
            parameters = prompt_template.get('parameters', {})
            
            # Substitute variables in prompt
            variables = {
                'field_name': field_name,
                'field_content': field_content,
                'project_context': project_context
            }
            
            messages = []
            
            # Add system message if present
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
            
            response = self.client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                **parameters
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error improving field {field_name}: {e}")
            return field_content
    
    def supports_feature(self, feature: str) -> bool:
        """Check if Azure OpenAI supports a feature"""
        supported_features = {
            'system_messages': True,
            'temperature': True,
            'max_tokens': True,
            'top_p': True,
            'frequency_penalty': True,
            'presence_penalty': True,
            'thinking_mode': False  # Azure typically doesn't have o3/o4-mini
        }
        return supported_features.get(feature, False)
    
    def get_available_models(self) -> List[str]:
        """Get available Azure OpenAI deployment names"""
        # Note: These would typically be deployment names configured in Azure
        return [
            'gpt-4',
            'gpt-4-32k',
            'gpt-35-turbo',
            'gpt-35-turbo-16k'
        ]
    
    def _validate_config(self) -> bool:
        """Validate Azure OpenAI configuration"""
        api_key = self.config.get('api_key')
        endpoint = self.config.get('endpoint')
        return bool(api_key and endpoint and endpoint.startswith('https://'))
    
    def _build_messages(self, project_data: Dict[str, Any], prompt_template: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages array for Azure OpenAI API"""
        messages = []
        
        # Add system message if present
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
        """Clean JSON response from Azure OpenAI"""
        # Remove code block markers
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
