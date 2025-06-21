"""
Prompt manager for loading and managing YAML prompt templates
"""
import yaml
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages loading and caching of YAML prompt templates"""
    
    def __init__(self, prompts_dir: str = None):
        """
        Initialize prompt manager
        
        Args:
            prompts_dir: Directory containing prompt templates
        """
        if prompts_dir is None:
            # Default to prompts directory relative to project root
            project_root = Path(__file__).parent.parent
            self.prompts_dir = project_root / 'prompts'
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self._cache = {}
        self._ensure_prompts_dir()
    
    def get_prompt_template(self, provider: str, model: str, prompt_type: str) -> Optional[Dict[str, Any]]:
        """
        Get a prompt template for a specific provider, model, and type
        
        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')
            model: Model name (e.g., 'gpt-4o', 'claude-3-5-sonnet')
            prompt_type: Type of prompt ('evaluation' or 'improvement')
            
        Returns:
            Prompt template dictionary or None if not found
        """
        cache_key = f"{provider}/{model}/{prompt_type}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build file path
        prompt_file = self.prompts_dir / provider / model / f"{prompt_type}.yaml"
        
        # Try to load the prompt
        template = self._load_prompt_file(prompt_file)
        
        # If specific model not found, try fallback to provider default
        if template is None:
            fallback_file = self.prompts_dir / provider / f"{prompt_type}.yaml"
            template = self._load_prompt_file(fallback_file)
        
        # Cache the result (even if None)
        self._cache[cache_key] = template
        
        return template
    
    def _load_prompt_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a YAML prompt file
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Parsed YAML content or None if file doesn't exist or can't be parsed
        """
        try:
            if not file_path.exists():
                logger.debug(f"Prompt file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            # Validate required fields
            if not self._validate_prompt_template(content):
                logger.error(f"Invalid prompt template: {file_path}")
                return None
            
            logger.debug(f"Loaded prompt template: {file_path}")
            return content
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading prompt file {file_path}: {e}")
            return None
    
    def _validate_prompt_template(self, template: Dict[str, Any]) -> bool:
        """
        Validate that a prompt template has required fields
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(template, dict):
            return False
        
        # Check for required top-level fields
        required_fields = ['metadata', 'user_prompt_template']
        for field in required_fields:
            if field not in template:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Check metadata
        metadata = template.get('metadata', {})
        required_metadata = ['provider', 'model', 'prompt_type']
        for field in required_metadata:
            if field not in metadata:
                logger.error(f"Missing required metadata field: {field}")
                return False
        
        return True
    
    def _ensure_prompts_dir(self):
        """Ensure prompts directory exists and create default templates if needed"""
        if not self.prompts_dir.exists():
            logger.info(f"Creating prompts directory: {self.prompts_dir}")
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default prompt templates"""
        # This will be populated when we create the YAML templates
        pass
    
    def clear_cache(self):
        """Clear the prompt template cache"""
        self._cache = {}
        logger.info("Prompt template cache cleared")
    
    def list_available_prompts(self) -> Dict[str, Dict[str, List[str]]]:
        """
        List all available prompt templates
        
        Returns:
            Dictionary mapping provider -> model -> [prompt_types]
        """
        available = {}
        
        if not self.prompts_dir.exists():
            return available
        
        for provider_dir in self.prompts_dir.iterdir():
            if not provider_dir.is_dir():
                continue
            
            provider_name = provider_dir.name
            available[provider_name] = {}
            
            for model_dir in provider_dir.iterdir():
                if not model_dir.is_dir():
                    continue
                
                model_name = model_dir.name
                prompt_types = []
                
                for prompt_file in model_dir.glob('*.yaml'):
                    prompt_type = prompt_file.stem
                    prompt_types.append(prompt_type)
                
                if prompt_types:
                    available[provider_name][model_name] = prompt_types
        
        return available
    
    def get_fallback_template(self, prompt_type: str) -> Dict[str, Any]:
        """
        Get a fallback template when no specific template is found
        
        Args:
            prompt_type: Type of prompt ('evaluation' or 'improvement')
            
        Returns:
            Basic fallback template
        """
        if prompt_type == 'evaluation':
            return {
                'metadata': {
                    'provider': 'fallback',
                    'model': 'fallback',
                    'prompt_type': 'evaluation',
                    'version': '1.0',
                    'language': 'fr-CA'
                },
                'system_message': "Vous êtes un expert en évaluation de projets d'investissement technologique. Vous devez analyser les projets selon 6 critères spécifiques et fournir des suggestions d'amélioration en français québécois formel. Répondez uniquement en JSON valide.",
                'user_prompt_template': '''Évaluez ce projet d'investissement selon les 6 critères suivants (score de 1 à 10) :

PROJET À ÉVALUER :
Titre : {titre}
Département PVP : {pvp}
Contexte : {contexte}
Objectifs : {objectifs}
Fonctionnalités : {fonctionnalites}

CRITÈRES D'ÉVALUATION :
1. Valeur Business (25%) : Impact et ROI pour l'entreprise (1=faible, 10=très élevé)
2. Faisabilité Technique (20%) : Complexité et maturité technologique (1=très difficile, 10=très faisable)
3. Effort Requis (15%) : Ressources et temps nécessaires (1=effort énorme, 10=effort minimal)
4. Niveau de Risque (15%) : Risques techniques, légaux, éthiques (1=très risqué, 10=très sûr)
5. Urgence (15%) : Pression temporelle et opportunité (1=pas urgent, 10=très urgent)
6. Alignement Stratégique (10%) : Cohérence avec les objectifs (1=pas aligné, 10=parfaitement aligné)

Répondez en JSON avec cette structure exacte :
{{
  "scores": {{
    "valeur_business": 7.5,
    "faisabilite_technique": 6.0,
    "effort_requis": 4.0,
    "niveau_risque": 8.0,
    "urgence": 5.5,
    "alignement_strategique": 9.0
  }},
  "suggestions": {{
    "valeur_business": "Suggestion d'amélioration pour la valeur business...",
    "faisabilite_technique": "Suggestion pour améliorer la faisabilité...",
    "effort_requis": "Suggestion pour optimiser l'effort...",
    "niveau_risque": "Suggestion pour réduire les risques...",
    "urgence": "Suggestion concernant l'urgence...",
    "alignement_strategique": "Suggestion pour l'alignement stratégique..."
  }},
  "defis_techniques": [
    "Défi technique 1",
    "Défi technique 2",
    "Défi technique 3"
  ],
  "duree_estimee": 180
}}

Assurez-vous que :
- Tous les scores sont entre 1.0 et 10.0
- Les suggestions sont spécifiques et actionables
- Les défis techniques sont réalistes
- La durée est en jours ouvrables
- Tout le texte est en français québécois formel''',
                'parameters': {
                    'temperature': 0.7,
                    'max_tokens': 2000
                }
            }
        else:  # improvement
            return {
                'metadata': {
                    'provider': 'fallback',
                    'model': 'fallback',
                    'prompt_type': 'improvement',
                    'version': '1.0',
                    'language': 'fr-CA'
                },
                'system_message': "Vous êtes un consultant expert en rédaction de projets d'investissement. Améliorez le contenu fourni en français québécois formel et professionnel.",
                'user_prompt_template': '''Analysez et améliorez le contenu suivant pour un projet d'investissement :

Champ : {field_name}
Contenu actuel : {field_content}
Contexte du projet : {project_context}

Fournissez une version améliorée qui soit :
- Plus claire et précise
- Mieux structurée
- Plus convaincante pour les investisseurs
- Conforme aux meilleures pratiques

Répondez uniquement avec le texte amélioré, sans explication additionnelle.''',
                'parameters': {
                    'temperature': 0.7,
                    'max_tokens': 800
                }
            }
