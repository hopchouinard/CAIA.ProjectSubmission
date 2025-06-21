"""
Databricks provider implementation
"""
import requests
import json
import logging
from typing import Dict, Any, List
from .base_provider import AIProvider

logger = logging.getLogger(__name__)

class DatabricksProvider(AIProvider):
    """Databricks provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Databricks provider"""
        super().__init__(config)
        
        if self.is_configured():
            self.host = config.get('host')
            self.token = config.get('token')
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
        else:
            self.host = None
            self.token = None
            self.headers = None
    
    def evaluate_project(self, project_data: Dict[str, Any], prompt_template: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a project using Databricks"""
        if not self.host or not self.token:
            logger.error("Databricks not configured")
            return self._get_fallback_evaluation()
        
        try:
            # Get model and parameters from template
            model = prompt_template.get('metadata', {}).get('model', 'meta-llama/Meta-Llama-3.1-70B-Instruct')
            parameters = prompt_template.get('parameters', {})
            
            # Build messages
            messages = self._build_messages(project_data, prompt_template)
            
            # Map parameters to Databricks format
            databricks_params = self._map_parameters(parameters)
            
            # Make API request
            endpoint = f"{self.host}/serving-endpoints/{model}/invocations"
            payload = {
                'messages': messages,
                **databricks_params
            }
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result_data = response.json()
            content = result_data['choices'][0]['message']['content'].strip()
            
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
            logger.error(f"Databricks API error: {e}")
            return self._get_fallback_evaluation()
    
    def improve_field(self, field_name: str, field_content: str, project_context: str, 
                     prompt_template: Dict[str, Any]) -> str:
        """Improve a field using Databricks"""
        if not self.host or not self.token:
            logger.error("Databricks not configured")
            return field_content
        
        try:
            # Get model and parameters from template
            model = prompt_template.get('metadata', {}).get('model', 'meta-llama/Meta-Llama-3.1-70B-Instruct')
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
            
            # Map parameters
            databricks_params = self._map_parameters(parameters)
            
            # Make API request
            endpoint = f"{self.host}/serving-endpoints/{model}/invocations"
            payload = {
                'messages': messages,
                **databricks_params
            }
            
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result_data = response.json()
            return result_data['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"Error improving field {field_name}: {e}")
            return field_content
    
    def supports_feature(self, feature: str) -> bool:
        """Check if Databricks supports a feature"""
        supported_features = {
            'system_messages': True,
            'temperature': True,
            'max_tokens': True,
            'top_p': True,
            'thinking_mode': False
        }
        return supported_features.get(feature, False)
    
    def get_available_models(self) -> List[str]:
        """Get available Databricks models"""
        return [
            'meta-llama/Meta-Llama-3.1-70B-Instruct',
            'meta-llama/Meta-Llama-3.1-8B-Instruct',
            'mistralai/Mixtral-8x7B-Instruct-v0.1',
            'databricks/dbrx-instruct'
        ]
    
    def _validate_config(self) -> bool:
        """Validate Databricks configuration"""
        host = self.config.get('host')
        token = self.config.get('token')
        return bool(host and token and host.startswith('https://'))
    
    def _build_messages(self, project_data: Dict[str, Any], prompt_template: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages array for Databricks API"""
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
    
    def _map_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Map OpenAI-style parameters to Databricks parameters"""
        mapped = {}
        
        # Direct mappings
        if 'temperature' in parameters:
            mapped['temperature'] = parameters['temperature']
        if 'max_tokens' in parameters:
            mapped['max_tokens'] = parameters['max_tokens']
        if 'top_p' in parameters:
            mapped['top_p'] = parameters['top_p']
        
        return mapped
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON response from Databricks"""
        # Remove code block markers
        if content.startswith('```json'):
            content = content[7:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
