"""
Demonstration script for the Project Evaluator application
This script shows how to interact with the application programmatically
"""

import os
import sys
import time

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Project, Evaluation

def demo_application():
    """Demonstrate the application functionality"""
    print("=" * 60)
    print("ÉVALUATEUR DE PROJETS D'INVESTISSEMENT - DÉMONSTRATION")
    print("=" * 60)
    print()
    
    # Create the app
    app = create_app()
    
    with app.app_context():
        # Show existing projects
        projects = Project.query.all()
        print(f"📊 Projets dans la base de données: {len(projects)}")
        print()
        
        for i, project in enumerate(projects, 1):
            evaluation = project.latest_evaluation
            print(f"{i}. {project.titre}")
            print(f"   Département: {project.pvp}")
            print(f"   Créé le: {project.created_at.strftime('%Y-%m-%d') if project.created_at else 'N/A'}")
            
            if evaluation:
                print(f"   Score final: {evaluation.score_final:.1f}/10")
                print(f"   Priorité: {project.priority_text}")
                print(f"   Action: {project.action_text}")
                
                # Show detailed scores
                print(f"   Scores détaillés:")
                print(f"     • Valeur Business: {evaluation.valeur_business:.1f}/10")
                print(f"     • Faisabilité Technique: {evaluation.faisabilite_technique:.1f}/10")
                print(f"     • Effort Requis: {evaluation.effort_requis:.1f}/10")
                print(f"     • Niveau de Risque: {evaluation.niveau_risque:.1f}/10")
                print(f"     • Urgence: {evaluation.urgence:.1f}/10")
                print(f"     • Alignement Stratégique: {evaluation.alignement_strategique:.1f}/10")
                
                if project.duree_estimee:
                    print(f"   Durée estimée: {project.duree_estimee} jours ouvrables")
                
                if project.defis_techniques:
                    defis = project.defis_techniques.split('\n')
                    print(f"   Défis techniques identifiés:")
                    for defi in defis[:3]:  # Show first 3 challenges
                        if defi.strip():
                            print(f"     • {defi.strip()}")
            else:
                print("   ⚠️  Non évalué")
            
            print()
        
        # Show statistics
        high_priority = sum(1 for p in projects if p.priority_level == 'élevée')
        medium_priority = sum(1 for p in projects if p.priority_level == 'moyenne')
        low_priority = sum(1 for p in projects if p.priority_level == 'faible')
        uneval = sum(1 for p in projects if p.priority_level == 'non-évalué')
        
        print("📈 STATISTIQUES DES PRIORITÉS:")
        print(f"   🔴 Priorité Élevée (≥7.0): {high_priority} projets")
        print(f"   🟠 Priorité Moyenne (4.0-6.9): {medium_priority} projets")
        print(f"   🟢 Priorité Faible (<4.0): {low_priority} projets")
        print(f"   ⚪ Non évalués: {uneval} projets")
        print()
        
        print("🚀 POUR TESTER L'APPLICATION:")
        print("1. Assurez-vous d'avoir configuré votre clé OpenAI dans .env")
        print("2. Lancez l'application avec: python app.py")
        print("3. Ouvrez votre navigateur sur: http://localhost:5000")
        print("4. Explorez les projets existants ou créez-en de nouveaux")
        print()
        
        print("💡 FONCTIONNALITÉS À TESTER:")
        print("• Navigation dans la liste des projets")
        print("• Visualisation des détails avec graphique radar")
        print("• Création d'un nouveau projet avec amélioration IA")
        print("• Réévaluation d'un projet existant")
        print("• Interface entièrement en français québécois")
        print()
        
        return True

if __name__ == "__main__":
    try:
        demo_application()
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        print("Assurez-vous que toutes les dépendances sont installées")
        print("pip install -r requirements.txt")
        sys.exit(1)
