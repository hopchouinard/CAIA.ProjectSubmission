import openai
import json
import logging
from typing import Dict, Any, Optional
from flask import current_app

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, api_key: str):
        """Initialize OpenAI service with API key"""
        # Set the API key for legacy OpenAI library (0.28.x)
        openai.api_key = api_key
    
    def evaluate_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a complete project and return scores, suggestions, challenges, and duration
        """
        prompt = self._build_evaluation_prompt(project_data)
        
        try:
            # Use legacy OpenAI API (0.28.x)
            response = openai.ChatCompletion.create(
                model="gpt-4.1",  # Use gpt-4.1 for better compatibility
                messages=[
                    {
                        "role": "system",
                        "content": "Vous êtes un expert en évaluation de projets d'investissement technologique. Vous devez analyser les projets selon 6 critères spécifiques et fournir des suggestions d'amélioration en français québécois formel. Répondez uniquement en JSON valide."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            content = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure valid JSON
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            result = json.loads(content)
            return self._validate_evaluation_result(result)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_evaluation()
    
    def improve_field(self, field_name: str, field_content: str, project_context: str = "") -> str:
        """
        Suggest improvements for a specific field
        """
        prompt = f"""
Analysez et améliorez le contenu suivant pour un projet d'investissement :

Champ : {field_name}
Contenu actuel : {field_content}
Contexte du projet : {project_context}

Fournissez une version améliorée qui soit :
- Plus claire et précise
- Mieux structurée
- Plus convaincante pour les investisseurs
- Conforme aux meilleures pratiques

Répondez uniquement avec le texte amélioré, sans explication additionnelle.
"""
        
        try:
            # Use legacy OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "system",
                        "content": "Vous êtes un consultant expert en rédaction de projets d'investissement. Améliorez le contenu fourni en français québécois formel et professionnel."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error improving field {field_name}: {e}")
            return field_content  # Return original content on error
    
    def _build_evaluation_prompt(self, project_data: Dict[str, Any]) -> str:
        """Build the evaluation prompt for OpenAI"""
        return f"""
Évaluez ce projet d'investissement selon les 6 critères suivants (score de 1 à 10) :

PROJET À ÉVALUER :
Titre : {project_data.get('titre', '')}
Département PVP : {project_data.get('pvp', '')}
Contexte : {project_data.get('contexte', '')}
Objectifs : {project_data.get('objectifs', '')}
Fonctionnalités : {project_data.get('fonctionnalites', '')}

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
- Tout le texte est en français québécois formel
"""
    
    def _validate_evaluation_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the evaluation result"""
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
        weights = current_app.config['EVALUATION_WEIGHTS']
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
        """Return fallback evaluation in case of API failure"""
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
