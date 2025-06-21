from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    pvp = db.Column(db.String(100), nullable=False)
    contexte = db.Column(db.Text, nullable=False)
    objectifs = db.Column(db.Text, nullable=False)
    fonctionnalites = db.Column(db.Text, nullable=False)
    defis_techniques = db.Column(db.Text)  # AI-generated
    duree_estimee = db.Column(db.Integer)  # AI-generated, in days
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with evaluations
    evaluations = db.relationship('Evaluation', backref='project', lazy=True, cascade='all, delete-orphan')
    
    @property
    def latest_evaluation(self):
        """Get the most recent evaluation for this project"""
        return Evaluation.query.filter_by(project_id=self.id).order_by(Evaluation.created_at.desc()).first()
    
    @property
    def priority_level(self):
        """Get the priority level based on the latest evaluation"""
        eval = self.latest_evaluation
        if not eval:
            return 'non-évalué'
        
        if eval.score_final >= 7.0:
            return 'élevée'
        elif eval.score_final >= 4.0:
            return 'moyenne'
        else:
            return 'faible'
    
    @property
    def priority_badge_class(self):
        """Get CSS class for priority badge"""
        priority = self.priority_level
        if priority == 'élevée':
            return 'badge bg-danger'
        elif priority == 'moyenne':
            return 'badge bg-warning'
        elif priority == 'faible':
            return 'badge bg-success'
        else:
            return 'badge bg-secondary'
    
    @property
    def priority_text(self):
        """Get display text for priority"""
        priority = self.priority_level
        if priority == 'élevée':
            return 'Priorité Élevée'
        elif priority == 'moyenne':
            return 'Priorité Moyenne'
        elif priority == 'faible':
            return 'Priorité Faible'
        else:
            return 'Non Évalué'
    
    @property
    def action_text(self):
        """Get action text based on priority"""
        priority = self.priority_level
        if priority == 'élevée':
            return 'Lancement immédiat'
        elif priority == 'moyenne':
            return 'Planification court terme'
        elif priority == 'faible':
            return 'Évaluation future'
        else:
            return 'Évaluation requise'
    
    def to_dict(self):
        """Convert project to dictionary"""
        evaluation = self.latest_evaluation
        return {
            'id': self.id,
            'titre': self.titre,
            'pvp': self.pvp,
            'contexte': self.contexte,
            'objectifs': self.objectifs,
            'fonctionnalites': self.fonctionnalites,
            'defis_techniques': self.defis_techniques,
            'duree_estimee': self.duree_estimee,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'evaluation': evaluation.to_dict() if evaluation else None,
            'priority': self.priority_level,
            'priority_text': self.priority_text,
            'action_text': self.action_text
        }

class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    # Evaluation scores (1-10)
    valeur_business = db.Column(db.Float, nullable=False)
    faisabilite_technique = db.Column(db.Float, nullable=False)
    effort_requis = db.Column(db.Float, nullable=False)  # Inverted: 10 = low effort
    niveau_risque = db.Column(db.Float, nullable=False)  # Inverted: 10 = low risk
    urgence = db.Column(db.Float, nullable=False)
    alignement_strategique = db.Column(db.Float, nullable=False)
    
    score_final = db.Column(db.Float, nullable=False)
    ai_suggestions = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_suggestions(self):
        """Parse AI suggestions from JSON"""
        if self.ai_suggestions:
            try:
                return json.loads(self.ai_suggestions)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_suggestions(self, suggestions_dict):
        """Store AI suggestions as JSON"""
        self.ai_suggestions = json.dumps(suggestions_dict, ensure_ascii=False)
    
    def to_dict(self):
        """Convert evaluation to dictionary"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'valeur_business': self.valeur_business,
            'faisabilite_technique': self.faisabilite_technique,
            'effort_requis': self.effort_requis,
            'niveau_risque': self.niveau_risque,
            'urgence': self.urgence,
            'alignement_strategique': self.alignement_strategique,
            'score_final': self.score_final,
            'suggestions': self.get_suggestions(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @property
    def criteria_scores(self):
        """Get scores as a list for radar chart"""
        return [
            self.valeur_business,
            self.faisabilite_technique,
            self.effort_requis,
            self.niveau_risque,
            self.urgence,
            self.alignement_strategique
        ]
    
    @property
    def criteria_labels(self):
        """Get labels for radar chart"""
        return [
            'Valeur Business',
            'Faisabilité Technique',
            'Effort Requis',
            'Niveau de Risque',
            'Urgence',
            'Alignement Stratégique'
        ]


class AIProviderConfig(db.Model):
    """Configuration for AI providers at runtime"""
    __tablename__ = 'ai_provider_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional configuration as JSON
    config_data = db.Column(db.Text)  # JSON string for provider-specific config
    
    def get_config_data(self):
        """Parse config data from JSON"""
        if self.config_data:
            try:
                return json.loads(self.config_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_config_data(self, config_dict):
        """Store config data as JSON"""
        self.config_data = json.dumps(config_dict, ensure_ascii=False)
    
    def to_dict(self):
        """Convert provider config to dictionary"""
        return {
            'id': self.id,
            'provider': self.provider,
            'model': self.model,
            'is_active': self.is_active,
            'priority': self.priority,
            'config_data': self.get_config_data(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_active_providers(cls):
        """Get all active providers ordered by priority"""
        return cls.query.filter_by(is_active=True).order_by(cls.priority.asc()).all()
    
    @classmethod
    def get_primary_provider(cls):
        """Get the primary (highest priority) active provider"""
        return cls.query.filter_by(is_active=True).order_by(cls.priority.asc()).first()
