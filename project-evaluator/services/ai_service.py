"""
Main AI service that replaces the original OpenAIService
This service manages multiple AI providers and external YAML prompts
"""
import logging
from typing import Dict, Any, Optional
from flask import current_app
from .provider_manager import ProviderManager
from .prompt_manager import PromptManager

logger = logging.getLogger(__name__)

class AIService:
    """    Main AI service that provides the same interface as OpenAIService
    but supports multiple providers and external YAML prompts
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI service
        
        Args:
            config: Optional configuration. If None, will use Flask app config
        """
        if config is None:
            # Build config from Flask app configuration
            try:
                config = self._build_config_from_flask()
            except Exception:
                # If Flask context is not available, use basic configuration
                config = self._build_basic_config()
        
        self.config = config
        self.prompt_manager = PromptManager()
        self.provider_manager = ProviderManager(config)
        
        logger.info("AI Service initialized with multi-provider support")
    
    def evaluate_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a complete project and return scores, suggestions, challenges, and duration
        
        Args:
            project_data: Dictionary containing project information
            
        Returns:
            Dictionary with evaluation results including scores, suggestions, etc.
        """
        try:
            # Get the appropriate prompt template
            provider_name = self.config.get('default_provider', 'openai')
            model_name = self.config.get('default_model', 'gpt-4o')
            
            prompt_template = self.prompt_manager.get_prompt_template(
                provider_name, model_name, 'evaluation'
            )
            
            # Use fallback template if none found
            if prompt_template is None:
                logger.warning(f"No prompt template found for {provider_name}/{model_name}/evaluation, using fallback")
                prompt_template = self.prompt_manager.get_fallback_template('evaluation')
            
            # Inject evaluation weights into provider config
            for provider_config in self.config.values():
                if isinstance(provider_config, dict):
                    provider_config['weights'] = current_app.config['EVALUATION_WEIGHTS']
            
            # Evaluate using provider manager with fallback
            result = self.provider_manager.evaluate_with_fallback(
                project_data, prompt_template
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in evaluate_project: {e}")
            return self._get_fallback_evaluation()
    
    def improve_field(self, field_name: str, field_content: str, project_context: str = "") -> str:
        """
        Suggest improvements for a specific field
        
        Args:
            field_name: Name of the field being improved
            field_content: Current content of the field
            project_context: Additional context about the project
            
        Returns:
            Improved field content as string
        """
        try:
            # Get the appropriate prompt template
            provider_name = self.config.get('default_provider', 'openai')
            model_name = self.config.get('default_model', 'gpt-4o')
            
            prompt_template = self.prompt_manager.get_prompt_template(
                provider_name, model_name, 'improvement'
            )
            
            # Use fallback template if none found
            if prompt_template is None:
                logger.warning(f"No prompt template found for {provider_name}/{model_name}/improvement, using fallback")
                prompt_template = self.prompt_manager.get_fallback_template('improvement')
            
            # Improve field using provider manager with fallback
            result = self.provider_manager.improve_field_with_fallback(
                field_name, field_content, project_context, prompt_template
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error improving field {field_name}: {e}")
            return field_content  # Return original content on error
    
    def _build_config_from_flask(self) -> Dict[str, Any]:
        """
        Build provider configuration from Flask app config and environment variables
        
        Returns:
            Configuration dictionary for providers        """
        import os
        
        config = {
            'default_provider': os.environ.get('DEFAULT_AI_PROVIDER', 'openai'),
            'default_model': os.environ.get('DEFAULT_AI_MODEL', 'gpt-4.1-2025-04-14'),
            'enable_fallback': os.environ.get('ENABLE_PROVIDER_FALLBACK', 'true').lower() == 'true',
            'fallback_order': ['openai', 'anthropic', 'google', 'azure', 'databricks']
        }
        
        # OpenAI configuration
        openai_config = {}
        if os.environ.get('OPENAI_API_KEY'):
            openai_config['api_key'] = os.environ.get('OPENAI_API_KEY')
        if os.environ.get('OPENAI_ORG_ID'):
            openai_config['organization'] = os.environ.get('OPENAI_ORG_ID')
        if openai_config:
            config['openai'] = openai_config
        
        # Anthropic configuration
        if os.environ.get('ANTHROPIC_API_KEY'):
            config['anthropic'] = {
                'api_key': os.environ.get('ANTHROPIC_API_KEY')
            }
        
        # Google configuration
        google_config = {}
        if os.environ.get('GOOGLE_API_KEY'):
            google_config['api_key'] = os.environ.get('GOOGLE_API_KEY')
        if os.environ.get('GOOGLE_PROJECT_ID'):
            google_config['project_id'] = os.environ.get('GOOGLE_PROJECT_ID')
        if google_config:
            config['google'] = google_config
        
        # Azure OpenAI configuration
        azure_config = {}
        if os.environ.get('AZURE_OPENAI_API_KEY'):
            azure_config['api_key'] = os.environ.get('AZURE_OPENAI_API_KEY')
        if os.environ.get('AZURE_OPENAI_ENDPOINT'):
            azure_config['endpoint'] = os.environ.get('AZURE_OPENAI_ENDPOINT')
        if os.environ.get('AZURE_OPENAI_API_VERSION'):
            azure_config['api_version'] = os.environ.get('AZURE_OPENAI_API_VERSION')
        if azure_config:
            config['azure'] = azure_config
        
        # Databricks configuration
        databricks_config = {}
        if os.environ.get('DATABRICKS_TOKEN'):
            databricks_config['token'] = os.environ.get('DATABRICKS_TOKEN')
        if os.environ.get('DATABRICKS_HOST'):
            databricks_config['host'] = os.environ.get('DATABRICKS_HOST')
        if databricks_config:
            config['databricks'] = databricks_config
        
        return config
    
    def _build_basic_config(self) -> Dict[str, Any]:
        """
        Build basic configuration when Flask context is not available
        
        Returns:
            Basic configuration dictionary
        """
        import os
        
        # Basic configuration with minimal settings
        config = {
            'default_provider': 'openai',
            'default_model': 'gpt-4o',
            'enable_fallback': True,
            'fallback_order': ['openai']
        }
        
        # Only add OpenAI if API key is available
        if os.environ.get('OPENAI_API_KEY'):
            config['openai'] = {
                'api_key': os.environ.get('OPENAI_API_KEY')
            }
        
        return config
    
    def _get_fallback_evaluation(self) -> Dict[str, Any]:
        """
        Return fallback evaluation in case of complete service failure
        
        Returns:
            Default evaluation result
        """
        return {
            'scores': {
                'valeur_business': 5.0,
                'faisabilite_technique': 5.0,
                'effort_requis': 5.0,
                'niveau_risque': 5.0,
                'urgence': 5.0,
                'alignement_strategique': 5.0
            },
            'score_final': 5.0,
            'suggestions': {
                'valeur_business': 'Service d\'évaluation temporairement indisponible. Veuillez réviser manuellement.',
                'faisabilite_technique': 'Service d\'évaluation temporairement indisponible. Veuillez réviser manuellement.',
                'effort_requis': 'Service d\'évaluation temporairement indisponible. Veuillez réviser manuellement.',
                'niveau_risque': 'Service d\'évaluation temporairement indisponible. Veuillez réviser manuellement.',
                'urgence': 'Service d\'évaluation temporairement indisponible. Veuillez réviser manuellement.',
                'alignement_strategique': 'Service d\'évaluation temporairement indisponible. Veuillez réviser manuellement.'
            },
            'defis_techniques': [
                'Service d\'analyse temporairement indisponible',
                'Validation manuelle requise',
                'Contactez l\'administrateur système'
            ],
            'duree_estimee': 90
        }
    
    # Legacy compatibility methods - these maintain the same interface as OpenAIService
    def _build_evaluation_prompt(self, project_data: Dict[str, Any]) -> str:
        """
        Legacy method for backward compatibility
        This is no longer used but kept for compatibility
        """
        return ""
    
    def _validate_evaluation_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility
        Validation is now done in the base provider
        """
        return result
    
    def _get_fallback_evaluation_legacy(self) -> Dict[str, Any]:
        """
        Legacy method name for backward compatibility
        """
        return self._get_fallback_evaluation()
    
    # Administrative methods
    def get_provider_status(self) -> Dict[str, Any]:
        """
        Get status of all providers for administrative purposes
        
        Returns:
            Dictionary with provider status information
        """
        return {
            'available_providers': self.provider_manager.get_available_providers(),
            'provider_info': self.provider_manager.get_provider_info(),
            'default_provider': self.config.get('default_provider'),
            'default_model': self.config.get('default_model'),
            'fallback_enabled': self.config.get('enable_fallback', True)
        }
    
    def switch_provider(self, provider_name: str, model_name: str = None):
        """
        Switch the default provider and model
        
        Args:
            provider_name: Name of the provider to switch to
            model_name: Optional model name
        """
        if provider_name in self.provider_manager.get_available_providers():
            self.config['default_provider'] = provider_name
            if model_name:
                self.config['default_model'] = model_name
            logger.info(f"Switched to provider: {provider_name}, model: {model_name}")
        else:
            raise ValueError(f"Provider {provider_name} not available")


# For backward compatibility - create an alias with the original name
# This allows existing code to continue working without changes
OpenAIService = AIService
