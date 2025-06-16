import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///projects.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    APP_NAME = os.environ.get('APP_NAME') or 'Évaluateur de Projets d\'Investissement'
    
    # Evaluation criteria weights
    EVALUATION_WEIGHTS = {
        'valeur_business': 0.25,
        'faisabilite_technique': 0.20,
        'effort_requis': 0.15,
        'niveau_risque': 0.15,
        'urgence': 0.15,
        'alignement_strategique': 0.10
    }
    
    # Priority thresholds
    PRIORITY_THRESHOLDS = {
        'high': 7.0,
        'medium': 4.0
    }
    
    # PVP departments
    PVP_DEPARTMENTS = [
        'Direction Générale',
        'Technologies de l\'Information',
        'Ressources Humaines',
        'Finance et Comptabilité',
        'Marketing et Ventes',
        'Opérations',
        'Recherche et Développement',
        'Service à la Clientèle',
        'Conformité et Risque',
        'Stratégie et Développement'
    ]
