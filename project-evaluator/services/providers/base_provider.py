"""
Abstract base class for AI providers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the provider with configuration
        
        Args:
            config: Provider configuration including API keys, endpoints, etc.
        """
        self.config = config
        self.name = self.__class__.__name__.replace('Provider', '').lower()
    
    @abstractmethod
    def evaluate_project(self, project_data: Dict[str, Any], prompt_template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a complete project and return scores, suggestions, challenges, and duration
        
        Args:
            project_data: Dictionary containing project information
            prompt_template: YAML prompt template with system/user messages and parameters
            
        Returns:
            Dictionary with evaluation results including scores, suggestions, etc.
        """
        pass
    
    @abstractmethod
    def improve_field(self, field_name: str, field_content: str, project_context: str, 
                     prompt_template: Dict[str, Any]) -> str:
        """
        Suggest improvements for a specific field
        
        Args:
            field_name: Name of the field being improved
            field_content: Current content of the field
            project_context: Additional context about the project
            prompt_template: YAML prompt template for field improvement
            
        Returns:
            Improved field content as string
        """
        pass
    
    @abstractmethod
    def supports_feature(self, feature: str) -> bool:
        """
        Check if the provider supports a specific feature
        
        Args:
            feature: Feature name (e.g., 'system_messages', 'temperature', 'thinking_mode')
            
        Returns:
            True if feature is supported, False otherwise
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for this provider
        
        Returns:
            List of model names
        """
        pass
    
    def is_configured(self) -> bool:
        """
        Check if the provider is properly configured
        
        Returns:
            True if configured, False otherwise
        """
        return self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> bool:
        """
        Validate provider-specific configuration
        
        Returns:
            True if configuration is valid, False otherwise
        """
        pass
    
    def _substitute_template_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in template string
        
        Args:
            template: Template string with {variable} placeholders
            variables: Dictionary of variables to substitute
            
        Returns:
            Template with variables substituted
        """
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return template
        except Exception as e:
            logger.error(f"Error substituting template variables: {e}")
            return template
    
    def _validate_evaluation_result(self, result: Dict[str, Any], weights: Dict[str, float]) -> Dict[str, Any]:
        """
        Validate and clean the evaluation result - common logic for all providers
        
        Args:
            result: Raw evaluation result
            weights: Evaluation criteria weights
            
        Returns:
            Validated and cleaned evaluation result
        """
        # Ensure all required fields exist
        if 'scores' not in result:
            result['scores'] = {}
        if 'suggestions' not in result:
            result['suggestions'] = {}
        if 'defis_techniques' not in result:
            result['defis_techniques'] = []
        if 'duree_estimee' not in result:
            result['duree_estimee'] = 90
        
        # Validate scores
        required_scores = ['valeur_business', 'faisabilite_technique', 'effort_requis', 
                          'niveau_risque', 'urgence', 'alignement_strategique']
        
        for score_key in required_scores:
            if score_key not in result['scores']:
                result['scores'][score_key] = 5.0
            else:
                # Ensure score is between 1 and 10
                score = float(result['scores'][score_key])
                result['scores'][score_key] = max(1.0, min(10.0, score))
        
        # Calculate final score using weights
        final_score = (
            result['scores']['valeur_business'] * weights['valeur_business'] +
            result['scores']['faisabilite_technique'] * weights['faisabilite_technique'] +
            result['scores']['effort_requis'] * weights['effort_requis'] +
            result['scores']['niveau_risque'] * weights['niveau_risque'] +
            result['scores']['urgence'] * weights['urgence'] +
            result['scores']['alignement_strategique'] * weights['alignement_strategique']
        )
        
        result['score_final'] = round(final_score, 2)
        
        return result
    
    def _get_fallback_evaluation(self) -> Dict[str, Any]:
        """
        Return fallback evaluation in case of API failure - common for all providers
        
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
                'valeur_business': 'Évaluation automatique non disponible. Veuillez réviser manuellement.',
                'faisabilite_technique': 'Évaluation automatique non disponible. Veuillez réviser manuellement.',
                'effort_requis': 'Évaluation automatique non disponible. Veuillez réviser manuellement.',
                'niveau_risque': 'Évaluation automatique non disponible. Veuillez réviser manuellement.',
                'urgence': 'Évaluation automatique non disponible. Veuillez réviser manuellement.',
                'alignement_strategique': 'Évaluation automatique non disponible. Veuillez réviser manuellement.'
            },
            'defis_techniques': [
                'Analyse technique requise',
                'Validation des exigences nécessaire',
                'Évaluation des risques à compléter'
            ],
            'duree_estimee': 90
        }
