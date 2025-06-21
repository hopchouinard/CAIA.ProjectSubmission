"""
Google Gemini provider implementation for google-genai library
"""
import google.genai as genai
import json
import logging
from typing import Dict, Any, List
from .base_provider import AIProvider

logger = logging.getLogger(__name__)

class GoogleProvider(AIProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Google provider"""
        super().__init__(config)
        
        if self.is_configured():
            try:
                # Initialize Google GenAI client
                self.client = genai.Client(api_key=config.get('api_key'))
                self.configured = True
            except Exception as e:
                logger.error(f"Failed to initialize Google client: {e}")
                self.configured = False
                self.client = None
        else:
            self.configured = False
            self.client = None
    
    def evaluate_project(self, project_data: Dict[str, Any], prompt_template: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a project using Google Gemini"""
        if not self.configured or not self.client:
            logger.error("Google client not configured")
            return self._get_fallback_evaluation()
        
        try:
            # Get model and parameters from template
            model_name = prompt_template.get('metadata', {}).get('model', 'gemini-1.5-pro')
            parameters = prompt_template.get('parameters', {})
            
            # Build prompt (Google uses a single prompt, combine system + user)
            system_message = prompt_template.get('system_message', '')
            user_prompt = self._substitute_template_variables(
                prompt_template.get('user_prompt_template', ''), 
                project_data
            )
            
            full_prompt = f"{system_message}\n\n{user_prompt}" if system_message else user_prompt
            
            # Map parameters to Google format
            generation_config = self._map_parameters(parameters)
            
            # Use the new google-genai library
            response = self.client.models.generate_content(
                model=model_name,
                contents=[{
                    "role": "user",
                    "parts": [{"text": full_prompt}]
                }],
                config=generation_config
            )
            
            content = response.text.strip()
            
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
            logger.error(f"Google API error: {e}")
            return self._get_fallback_evaluation()
    
    def improve_field(self, field_name: str, field_content: str, project_context: str, 
                     prompt_template: Dict[str, Any]) -> str:
        """Improve a field using Google Gemini"""
        if not self.configured or not self.client:
            logger.error("Google client not configured")
            return field_content
        
        try:
            # Get model and parameters from template
            model_name = prompt_template.get('metadata', {}).get('model', 'gemini-1.5-pro')
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
            
            full_prompt = f"{system_message}\n\n{user_prompt}" if system_message else user_prompt
            
            # Map parameters
            generation_config = self._map_parameters(parameters)
            
            # Use the new google-genai library
            response = self.client.models.generate_content(
                model=model_name,
                contents=[{
                    "role": "user", 
                    "parts": [{"text": full_prompt}]
                }],
                config=generation_config
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error improving field {field_name}: {e}")
            return field_content
    
    def supports_feature(self, feature: str) -> bool:
        """Check if Google supports a feature"""
        supported_features = {
            'system_messages': True,  # Combined with user prompt
            'temperature': True,
            'max_tokens': True,
            'top_p': True,
            'top_k': True,
            'thinking_mode': False
        }
        return supported_features.get(feature, False)
    
    def get_available_models(self) -> List[str]:
        """Get available Google models"""
        return [
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-1.0-pro'
        ]
    
    def _validate_config(self) -> bool:
        """Validate Google configuration"""
        api_key = self.config.get('api_key')
        return bool(api_key)
    
    def _map_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Map OpenAI-style parameters to Google parameters"""
        mapped = {}
        
        # Direct mappings
        if 'temperature' in parameters:
            mapped['temperature'] = parameters['temperature']
        if 'max_tokens' in parameters:
            mapped['max_output_tokens'] = parameters['max_tokens']
        if 'top_p' in parameters:
            mapped['top_p'] = parameters['top_p']
        if 'top_k' in parameters:
            mapped['top_k'] = parameters['top_k']
        
        return mapped
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON response from Google"""
        # Remove code block markers
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
