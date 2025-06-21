"""
Anthropic (Claude) provider implementation
"""
import anthropic
import json
import logging
from typing import Dict, Any, List
from .base_provider import AIProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(AIProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Anthropic provider"""
        super().__init__(config)
        
        if self.is_configured():
            self.client = anthropic.Anthropic(
                api_key=config.get('api_key')
            )
        else:
            self.client = None
    
    def evaluate_project(self, project_data: Dict[str, Any], prompt_template: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a project using Anthropic Claude"""
        if not self.client:
            logger.error("Anthropic client not initialized")
            return self._get_fallback_evaluation()
        
        try:
            # Get model and parameters from template
            model = prompt_template.get('metadata', {}).get('model', 'claude-3-5-sonnet-20241022')
            parameters = prompt_template.get('parameters', {})
            
            # Build system message and user prompt
            system_message = prompt_template.get('system_message', '')
            user_prompt = self._substitute_template_variables(
                prompt_template.get('user_prompt_template', ''), 
                project_data
            )
            
            # Map OpenAI parameters to Anthropic parameters
            anthropic_params = self._map_parameters(parameters)
            
            response = self.client.messages.create(
                model=model,
                system=system_message,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }],
                **anthropic_params
            )
            
            content = response.content[0].text.strip()
            
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
            logger.error(f"Anthropic API error: {e}")
            return self._get_fallback_evaluation()
    
    def improve_field(self, field_name: str, field_content: str, project_context: str, 
                     prompt_template: Dict[str, Any]) -> str:
        """Improve a field using Anthropic Claude"""
        if not self.client:
            logger.error("Anthropic client not initialized")
            return field_content
        
        try:
            # Get model and parameters from template
            model = prompt_template.get('metadata', {}).get('model', 'claude-3-5-sonnet-20241022')
            parameters = prompt_template.get('parameters', {})
            
            # Substitute variables in prompt
            variables = {
                'field_name': field_name,
                'field_content': field_content,
                'project_context': project_context
            }
            
            system_message = prompt_template.get('system_message', '')
            user_prompt = self._substitute_template_variables(
                prompt_template.get('user_prompt_template', ''), 
                variables
            )
            
            # Map parameters
            anthropic_params = self._map_parameters(parameters)
            
            response = self.client.messages.create(
                model=model,
                system=system_message,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }],
                **anthropic_params
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Error improving field {field_name}: {e}")
            return field_content
    
    def supports_feature(self, feature: str) -> bool:
        """Check if Anthropic supports a feature"""
        supported_features = {
            'system_messages': True,
            'temperature': True,
            'max_tokens': True,
            'top_p': True,
            'top_k': True,
            'thinking_mode': False
        }
        return supported_features.get(feature, False)
    
    def get_available_models(self) -> List[str]:
        """Get available Anthropic models"""
        return [
            'claude-3-5-haiku',
            'claude-4-opus',
            'claude-4-sonnet'
        ]
    
    def _validate_config(self) -> bool:
        """Validate Anthropic configuration"""
        api_key = self.config.get('api_key')
        return bool(api_key and api_key.startswith('sk-ant-'))
    
    def _map_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Map OpenAI-style parameters to Anthropic parameters"""
        mapped = {}
        
        # Direct mappings
        if 'temperature' in parameters:
            mapped['temperature'] = parameters['temperature']
        if 'max_tokens' in parameters:
            mapped['max_tokens'] = parameters['max_tokens']
        if 'top_p' in parameters:
            mapped['top_p'] = parameters['top_p']
        if 'top_k' in parameters:
            mapped['top_k'] = parameters['top_k']
        
        # Default max_tokens if not specified
        if 'max_tokens' not in mapped:
            mapped['max_tokens'] = 2000
        
        return mapped
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON response from Anthropic"""
        # Remove code block markers
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
