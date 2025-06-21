"""
Provider manager for handling provider selection and fallback logic
"""
import logging
from typing import Dict, Any, List, Optional, Type
from .providers import AIProvider, OpenAIProvider

# Import other providers conditionally
try:
    from .providers import AnthropicProvider
except ImportError:
    AnthropicProvider = None

try:
    from .providers import GoogleProvider
except ImportError:
    GoogleProvider = None

try:
    from .providers import AzureProvider
except ImportError:
    AzureProvider = None

try:
    from .providers import DatabricksProvider
except ImportError:
    DatabricksProvider = None

logger = logging.getLogger(__name__)

class ProviderManager:
    """Manages AI provider selection and fallback logic"""
    
    # Registry of available providers (only include if imported successfully)
    PROVIDER_REGISTRY: Dict[str, Type[AIProvider]] = {
        'openai': OpenAIProvider,
    }
    
    # Add conditional providers
    if AnthropicProvider:
        PROVIDER_REGISTRY['anthropic'] = AnthropicProvider
    if GoogleProvider:
        PROVIDER_REGISTRY['google'] = GoogleProvider
    if AzureProvider:
        PROVIDER_REGISTRY['azure'] = AzureProvider
    if DatabricksProvider:
        PROVIDER_REGISTRY['databricks'] = DatabricksProvider
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider manager
        
        Args:
            config: Configuration containing provider settings and credentials
        """
        self.config = config
        self._providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers"""
        for provider_name, provider_class in self.PROVIDER_REGISTRY.items():
            try:
                provider_config = self.config.get(provider_name, {})
                if provider_config:
                    provider_instance = provider_class(provider_config)
                    if provider_instance.is_configured():
                        self._providers[provider_name] = provider_instance
                        logger.info(f"Initialized provider: {provider_name}")
                    else:
                        logger.warning(f"Provider {provider_name} not properly configured")
                else:
                    logger.debug(f"No configuration found for provider: {provider_name}")
            except Exception as e:
                logger.error(f"Error initializing provider {provider_name}: {e}")
    
    def get_primary_provider(self) -> Optional[AIProvider]:
        """
        Get the primary configured provider
        
        Returns:
            Primary provider instance or None if not available
        """
        primary_name = self.config.get('default_provider', 'openai')
        return self._providers.get(primary_name)
    
    def get_provider(self, provider_name: str) -> Optional[AIProvider]:
        """
        Get a specific provider by name
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Provider instance or None if not available
        """
        return self._providers.get(provider_name)
    
    def get_fallback_providers(self, exclude: str = None) -> List[AIProvider]:
        """
        Get list of fallback providers in priority order
        
        Args:
            exclude: Provider name to exclude from fallbacks
            
        Returns:
            List of provider instances
        """
        fallback_order = self.config.get('fallback_order', [
            'openai', 'anthropic', 'google', 'azure', 'databricks'
        ])
        
        fallbacks = []
        for provider_name in fallback_order:
            if provider_name != exclude and provider_name in self._providers:
                fallbacks.append(self._providers[provider_name])
        
        return fallbacks
    
    def evaluate_with_fallback(self, project_data: Dict[str, Any], 
                             prompt_template: Dict[str, Any],
                             preferred_provider: str = None) -> Dict[str, Any]:
        """
        Evaluate a project with automatic fallback to other providers
        
        Args:
            project_data: Project data to evaluate
            prompt_template: Prompt template to use
            preferred_provider: Preferred provider name (optional)
            
        Returns:
            Evaluation result
        """
        # Determine provider order
        providers_to_try = []
        
        # Try preferred provider first if specified
        if preferred_provider and preferred_provider in self._providers:
            providers_to_try.append(self._providers[preferred_provider])
        
        # Add primary provider if not already added
        primary = self.get_primary_provider()
        if primary and primary not in providers_to_try:
            providers_to_try.append(primary)
        
        # Add fallback providers
        exclude = preferred_provider if preferred_provider in self._providers else None
        if not exclude and primary:
            exclude = primary.name
        
        fallbacks = self.get_fallback_providers(exclude)
        providers_to_try.extend(fallbacks)
        
        # Try each provider in order
        last_error = None
        for provider in providers_to_try:
            try:
                logger.info(f"Attempting evaluation with provider: {provider.name}")
                result = provider.evaluate_project(project_data, prompt_template)
                
                # Check if we got a valid result (not fallback)
                if result.get('score_final', 0) != 5.0 or any(
                    'Évaluation automatique non disponible' not in suggestion 
                    for suggestion in result.get('suggestions', {}).values()
                ):
                    logger.info(f"Successful evaluation with provider: {provider.name}")
                    return result
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider.name} failed: {e}")
                continue
        
        # If all providers failed, return fallback
        logger.error(f"All providers failed. Last error: {last_error}")
        return self._get_ultimate_fallback()
    
    def improve_field_with_fallback(self, field_name: str, field_content: str, 
                                  project_context: str, prompt_template: Dict[str, Any],
                                  preferred_provider: str = None) -> str:
        """
        Improve a field with automatic fallback to other providers
        
        Args:
            field_name: Name of the field to improve
            field_content: Current field content
            project_context: Project context
            prompt_template: Prompt template to use
            preferred_provider: Preferred provider name (optional)
            
        Returns:
            Improved field content
        """
        # Determine provider order (same logic as evaluate_with_fallback)
        providers_to_try = []
        
        if preferred_provider and preferred_provider in self._providers:
            providers_to_try.append(self._providers[preferred_provider])
        
        primary = self.get_primary_provider()
        if primary and primary not in providers_to_try:
            providers_to_try.append(primary)
        
        exclude = preferred_provider if preferred_provider in self._providers else None
        if not exclude and primary:
            exclude = primary.name
        
        fallbacks = self.get_fallback_providers(exclude)
        providers_to_try.extend(fallbacks)
        
        # Try each provider in order
        for provider in providers_to_try:
            try:
                logger.info(f"Attempting field improvement with provider: {provider.name}")
                result = provider.improve_field(field_name, field_content, project_context, prompt_template)
                
                # Check if content was actually improved (not just returned as-is)
                if result != field_content:
                    logger.info(f"Successful field improvement with provider: {provider.name}")
                    return result
                    
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed for field improvement: {e}")
                continue
        
        # If all providers failed, return original content
        logger.error("All providers failed for field improvement")
        return field_content
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available provider names
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all providers
        
        Returns:
            Dictionary with provider information
        """
        info = {}
        for name, provider in self._providers.items():
            info[name] = {
                'name': name,
                'configured': provider.is_configured(),
                'available_models': provider.get_available_models(),
                'supported_features': {
                    'system_messages': provider.supports_feature('system_messages'),
                    'temperature': provider.supports_feature('temperature'),
                    'max_tokens': provider.supports_feature('max_tokens'),
                    'thinking_mode': provider.supports_feature('thinking_mode')
                }
            }
        return info
    
    def _get_ultimate_fallback(self) -> Dict[str, Any]:
        """
        Get ultimate fallback evaluation when all providers fail
        
        Returns:
            Fallback evaluation result
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
