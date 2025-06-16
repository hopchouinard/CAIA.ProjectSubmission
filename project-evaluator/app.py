from flask import Flask, render_template
from config import Config
from models import db, Project, Evaluation
from routes import main_bp, api_bp
import logging
import os

def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Template filters
    @app.template_filter('format_number')
    def format_number(value):
        """Format numbers with Quebec French formatting"""
        if value is None:
            return ''
        try:
            # Use space for thousands separator and comma for decimal
            return f"{float(value):,.1f}".replace(',', ' ').replace('.', ',')
        except (ValueError, TypeError):
            return str(value)
    
    @app.template_filter('format_score')
    def format_score(value):
        """Format score with 1 decimal place"""
        if value is None:
            return '0,0'
        try:
            return f"{float(value):.1f}".replace('.', ',')
        except (ValueError, TypeError):
            return '0,0'
    
    @app.template_filter('format_date')
    def format_date(value):
        """Format date in Quebec French format (AAAA-MM-JJ)"""
        if value is None:
            return ''
        try:
            return value.strftime('%Y-%m-%d')
        except:
            return str(value)
    
    @app.template_filter('format_datetime')
    def format_datetime(value):
        """Format datetime in Quebec French format"""
        if value is None:
            return ''
        try:
            return value.strftime('%Y-%m-%d %H:%M')
        except:
            return str(value)
    
    @app.template_filter('split_lines')
    def split_lines(value):
        """Split text into lines for display"""
        if not value:
            return []
        return value.split('\n')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Add sample data if database is empty
        if Project.query.count() == 0:
            create_sample_data()
    
    return app

def create_sample_data():
    """Create sample projects for demonstration"""
    sample_projects = [
        {
            'titre': 'Plateforme de Commerce Électronique B2B',
            'pvp': 'Technologies de l\'Information',
            'contexte': 'Notre entreprise souhaite développer une plateforme de commerce électronique dédiée aux transactions B2B pour améliorer l\'expérience client et automatiser les processus de vente. La solution doit permettre aux clients professionnels de passer des commandes en ligne, de gérer leurs comptes et de suivre leurs livraisons en temps réel.',
            'objectifs': 'Créer une plateforme intuitive qui augmente les ventes B2B de 40% en 18 mois, réduit les coûts de traitement des commandes de 30%, améliore la satisfaction client et facilite l\'expansion vers de nouveaux marchés. La plateforme doit être évolutive et intégrable avec nos systèmes existants.',
            'fonctionnalites': 'Catalogue produits interactif avec recherche avancée, système de commandes automatisé, gestion des comptes clients avec historique, suivi de livraisons en temps réel, intégration ERP/CRM, tableau de bord analytique, système de facturation automatique, support multi-devises et notifications personnalisées.'
        },
        {
            'titre': 'Système de Gestion des Ressources Humaines',
            'pvp': 'Ressources Humaines',
            'contexte': 'Le département des ressources humaines fait face à des défis croissants de gestion des employés avec des processus manuels chronophages. Il devient urgent de moderniser notre approche RH pour améliorer l\'efficacité opérationnelle et l\'expérience employé dans un contexte de croissance rapide de l\'entreprise.',
            'objectifs': 'Implémenter un SIRH complet qui automatise 80% des processus RH actuels, améliore l\'engagement employé de 25%, réduit le temps de traitement administratif de 50% et fournit des analyses prédictives pour la prise de décision stratégique en matière de talents.',
            'fonctionnalites': 'Portail employé self-service, gestion automatisée des congés et absences, évaluations de performance digitales, recrutement et onboarding automatisés, formation en ligne intégrée, analyses RH avancées, gestion de la paie, planification des effectifs et tableaux de bord décisionnels.'
        },
        {
            'titre': 'Application Mobile de Service Client',
            'pvp': 'Service à la Clientèle',
            'contexte': 'Nos clients demandent un accès mobile pour gérer leurs interactions avec notre service client. L\'absence d\'une solution mobile nuit à notre compétitivité et limite notre capacité à offrir un support client moderne et réactif conforme aux attentes actuelles du marché.',
            'objectifs': 'Développer une application mobile native qui améliore la satisfaction client de 35%, réduit le temps de résolution des tickets de 40%, augmente l\'utilisation du self-service de 60% et permet un support client disponible 24/7 avec des fonctionnalités de chat en temps réel.',
            'fonctionnalites': 'Interface utilisateur intuitive, système de tickets intégré, chat en temps réel avec agents, base de connaissances consultable, notifications push personnalisées, historique des interactions, évaluations de service, support multilingue et mode hors-ligne pour consultation.'
        }
    ]
    
    for project_data in sample_projects:
        project = Project(**project_data)
        db.session.add(project)
    
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
