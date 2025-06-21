from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from models import db, Project, Evaluation
from services import AIService
import logging

main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Home page with list of all projects sorted by score"""
    try:
        # Get all projects with their latest evaluations
        projects = db.session.query(Project).all()
        
        # Sort by score (descending), with unevaluated projects at the end
        def sort_key(project):
            eval = project.latest_evaluation
            if eval:
                return (-eval.score_final, project.created_at)
            else:
                return (float('-inf'), project.created_at)
        
        projects.sort(key=sort_key)
        
        return render_template('index.html', projects=projects)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        flash('Erreur lors du chargement des projets.', 'error')
        return render_template('index.html', projects=[])

@main_bp.route('/projects/new', methods=['GET', 'POST'])
def new_project():
    """Create new project form"""
    if request.method == 'GET':
        departments = current_app.config['PVP_DEPARTMENTS']
        return render_template('new_project.html', departments=departments)
    
    elif request.method == 'POST':
        try:
            # Get form data
            titre = request.form.get('titre', '').strip()
            pvp = request.form.get('pvp', '').strip()
            contexte = request.form.get('contexte', '').strip()
            objectifs = request.form.get('objectifs', '').strip()
            fonctionnalites = request.form.get('fonctionnalites', '').strip()
            
            # Validate required fields
            if not all([titre, pvp, contexte, objectifs, fonctionnalites]):
                flash('Tous les champs sont requis.', 'error')
                return redirect(url_for('main.new_project'))
            
            # Validate field lengths
            if len(contexte) < 100 or len(objectifs) < 100 or len(fonctionnalites) < 100:
                flash('Les champs évaluables doivent contenir au moins 100 caractères.', 'error')
                return redirect(url_for('main.new_project'))
            
            if len(titre) > 200:
                flash('Le titre ne peut pas dépasser 200 caractères.', 'error')
                return redirect(url_for('main.new_project'))
            
            # Create new project
            project = Project(
                titre=titre,
                pvp=pvp,
                contexte=contexte,
                objectifs=objectifs,
                fonctionnalites=fonctionnalites
            )
            
            db.session.add(project)
            db.session.commit()
              # Evaluate the project using AI service
            try:
                ai_service = AIService()
                evaluation_result = ai_service.evaluate_project({
                    'titre': titre,
                    'pvp': pvp,
                    'contexte': contexte,
                    'objectifs': objectifs,
                    'fonctionnalites': fonctionnalites
                })
                
                # Update project with AI-generated fields
                project.defis_techniques = '\n'.join(evaluation_result.get('defis_techniques', []))
                project.duree_estimee = evaluation_result.get('duree_estimee', 90)
                
                # Create evaluation record
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
                
                flash('Projet créé et évalué avec succès !', 'success')
                return redirect(url_for('main.project_detail', id=project.id))
                
            except Exception as e:
                logger.error(f"Error evaluating project: {e}")
                db.session.commit()  # Save project even if evaluation fails
                flash('Projet créé, mais l\'évaluation automatique a échoué. Vous pouvez réévaluer le projet manuellement.', 'warning')
                return redirect(url_for('main.project_detail', id=project.id))
                
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            db.session.rollback()
            flash('Erreur lors de la création du projet.', 'error')
            return redirect(url_for('main.new_project'))

@main_bp.route('/projects/<int:id>')
def project_detail(id):
    """Project detail page"""
    try:
        project = Project.query.get_or_404(id)
        evaluation = project.latest_evaluation
        
        return render_template('project_detail.html', project=project, evaluation=evaluation)
    except Exception as e:
        logger.error(f"Error in project detail route: {e}")
        flash('Erreur lors du chargement du projet.', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/projects/<int:id>/reevaluate')
def reevaluate_project(id):
    """Reevaluate an existing project"""
    try:
        project = Project.query.get_or_404(id)
          # Evaluate the project using AI service
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
        
        # Create new evaluation record
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
        
        flash('Projet réévalué avec succès !', 'success')
        return redirect(url_for('main.project_detail', id=project.id))
        
    except Exception as e:
        logger.error(f"Error reevaluating project: {e}")
        flash('Erreur lors de la réévaluation du projet.', 'error')
        return redirect(url_for('main.project_detail', id=id))
