from flask import Blueprint, request, jsonify, current_app
from models import db, Project, Evaluation
from services import AIService
import logging

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

@api_bp.route('/projects', methods=['POST'])
def create_project():
    """API endpoint to create and evaluate a project"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        # Validate required fields
        required_fields = ['titre', 'pvp', 'contexte', 'objectifs', 'fonctionnalites']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Le champ {field} est requis'}), 400
        
        # Validate field lengths
        if len(data['titre']) > 200:
            return jsonify({'error': 'Le titre ne peut pas dépasser 200 caractères'}), 400
        
        for field in ['contexte', 'objectifs', 'fonctionnalites']:
            if len(data[field]) < 100:
                return jsonify({'error': f'Le champ {field} doit contenir au moins 100 caractères'}), 400
        
        # Create project
        project = Project(
            titre=data['titre'],
            pvp=data['pvp'],
            contexte=data['contexte'],
            objectifs=data['objectifs'],
            fonctionnalites=data['fonctionnalites']
        )
        
        db.session.add(project)
        db.session.commit()
          # Evaluate project
        try:
            ai_service = AIService()
            evaluation_result = ai_service.evaluate_project(data)
            
            # Update project with AI-generated fields
            project.defis_techniques = '\n'.join(evaluation_result.get('defis_techniques', []))
            project.duree_estimee = evaluation_result.get('duree_estimee', 90)
            
            # Create evaluation
            evaluation = Evaluation(
                project_id=project.id,
                valeur_business=evaluation_result['scores']['valeur_business'],
                faisabilite_technique=evaluation_result['scores']['faisabilite_technique'],
                effort_requis=evaluation_result['scores']['effort_requis'],
                niveau_risque=evaluation_result['scores']['niveau_risque'],
                urgence=evaluation_result['scores']['urgence'],
                alignement_strategique=evaluation_result['scores']['alignement_strategique'],
                score_final=evaluation_result['score_final']
            )
            
            evaluation.set_suggestions(evaluation_result.get('suggestions', {}))
            
            db.session.add(evaluation)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'project': project.to_dict(),
                'message': 'Projet créé et évalué avec succès'
            }), 201
            
        except Exception as e:
            logger.error(f"Error evaluating project: {e}")
            db.session.commit()  # Save project even if evaluation fails
            return jsonify({
                'success': True,
                'project': project.to_dict(),
                'message': 'Projet créé, mais évaluation échouée',
                'warning': 'L\'évaluation automatique a échoué'
            }), 201
            
    except Exception as e:
        logger.error(f"Error creating project via API: {e}")
        db.session.rollback()
        return jsonify({'error': 'Erreur lors de la création du projet'}), 500

@api_bp.route('/improve-field', methods=['POST'])
def improve_field():
    """API endpoint to get field improvement suggestions"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        field_name = data.get('field_name')
        field_content = data.get('field_content')
        project_context = data.get('project_context', '')
        
        if not field_name or not field_content:
            return jsonify({'error': 'field_name et field_content sont requis'}), 400
          # Get improvement suggestion
        ai_service = AIService()
        improved_content = ai_service.improve_field(field_name, field_content, project_context)
        
        return jsonify({
            'success': True,
            'original_content': field_content,
            'improved_content': improved_content,
            'field_name': field_name
        })
        
    except Exception as e:
        logger.error(f"Error improving field: {e}")
        return jsonify({
            'error': 'Erreur lors de l\'amélioration du champ',
            'original_content': data.get('field_content', '') if data else ''
        }), 500

@api_bp.route('/projects/<int:project_id>/reevaluate', methods=['GET'])
def reevaluate_project_api(project_id):
    """API endpoint to reevaluate a project"""
    try:
        project = Project.query.get_or_404(project_id)
          # Evaluate project
        ai_service = AIService()
        evaluation_result = ai_service.evaluate_project({
            'titre': project.titre,
            'pvp': project.pvp,
            'contexte': project.contexte,
            'objectifs': project.objectifs,
            'fonctionnalites': project.fonctionnalites
        })
        
        # Update project with new AI-generated fields
        project.defis_techniques = '\n'.join(evaluation_result.get('defis_techniques', []))
        project.duree_estimee = evaluation_result.get('duree_estimee', 90)
        
        # Create new evaluation
        evaluation = Evaluation(
            project_id=project.id,
            valeur_business=evaluation_result['scores']['valeur_business'],
            faisabilite_technique=evaluation_result['scores']['faisabilite_technique'],
            effort_requis=evaluation_result['scores']['effort_requis'],
            niveau_risque=evaluation_result['scores']['niveau_risque'],
            urgence=evaluation_result['scores']['urgence'],
            alignement_strategique=evaluation_result['scores']['alignement_strategique'],
            score_final=evaluation_result['score_final']
        )
        
        evaluation.set_suggestions(evaluation_result.get('suggestions', {}))
        
        db.session.add(evaluation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': 'Projet réévalué avec succès'
        })
        
    except Exception as e:
        logger.error(f"Error reevaluating project via API: {e}")
        return jsonify({'error': 'Erreur lors de la réévaluation'}), 500

@api_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """API endpoint to get project details"""
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify({
            'success': True,
            'project': project.to_dict()
        })
    except Exception as e:
        logger.error(f"Error getting project via API: {e}")
        return jsonify({'error': 'Projet non trouvé'}), 404

@api_bp.route('/projects', methods=['GET'])
def get_projects():
    """API endpoint to get all projects"""
    try:
        projects = Project.query.all()
        
        # Sort by score (descending)
        def sort_key(project):
            eval = project.latest_evaluation
            if eval:
                return -eval.score_final
            else:
                return float('-inf')
        
        projects.sort(key=sort_key)
        
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects]
        })
        
    except Exception as e:
        logger.error(f"Error getting projects via API: {e}")
        return jsonify({'error': 'Erreur lors du chargement des projets'}), 500
