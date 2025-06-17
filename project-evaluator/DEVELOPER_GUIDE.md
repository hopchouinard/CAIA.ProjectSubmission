# Guide Développeur - Évaluateur de Projets d'Investissement

## 🏗️ Architecture Générale

Cette application Flask suit une architecture modulaire avec séparation des responsabilités :

```
project-evaluator/
├── app.py                    # Point d'entrée et factory
├── config.py                 # Configuration centralisée
├── models.py                 # Modèles de données SQLAlchemy
├── routes/                   # Contrôleurs organisés par domaine
├── services/                 # Services métier et intégrations
├── templates/                # Vues Jinja2
├── static/                   # Assets front-end
└── requirements.txt          # Dépendances Python
```

### Flux de Données Principal
1. **Entrée** : Formulaires HTML ou API REST
2. **Validation** : Routes Flask avec validation côté serveur
3. **Traitement** : Services métier (OpenAI, calculs)
4. **Persistance** : Modèles SQLAlchemy
5. **Sortie** : Templates Jinja2 ou JSON

---

## 📁 Guide des Fichiers

### `app.py` - Point d'Entrée Principal

**Rôle** : Factory Flask, configuration globale et initialisation

**Structure** :
```python
def create_app(config_class=Config):
    # Création de l'instance Flask
    # Configuration des extensions
    # Enregistrement des blueprints
    # Gestionnaires d'erreurs
    # Filtres de templates
    # Initialisation base de données
```

**Modification Courante - Ajouter un nouveau filtre de template** :
```python
@app.template_filter('format_currency')
def format_currency(value):
    """Format currency in CAD format"""
    if value is None:
        return '0,00 $'
    return f"{float(value):,.2f} $".replace(',', ' ').replace('.', ',')
```

**Modification Courante - Ajouter un gestionnaire d'erreur** :
```python
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403
```

**Extension - Ajouter une extension Flask** :
```python
from flask_login import LoginManager

def create_app(config_class=Config):
    app = Flask(__name__)
    # ...existing code...
    
    # Initialize new extension
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
```
---

### `config.py` - Configuration Centralisée

**Rôle** : Gestion des variables d'environnement et paramètres

**Structure Actuelle** :
```python
class Config:
    # Variables d'environnement
    # Poids d'évaluation
    # Seuils de priorité
    # Départements PVP
```

**Modification Courante - Ajouter un nouveau critère d'évaluation** :
```python
EVALUATION_WEIGHTS = {
    'valeur_business': 0.20,        # Réduire de 0.25 à 0.20
    'faisabilite_technique': 0.20,
    'effort_requis': 0.15,
    'niveau_risque': 0.15,
    'urgence': 0.15,
    'alignement_strategique': 0.10,
    'impact_environnemental': 0.05  # Nouveau critère
}
```

**Extension - Configuration par environnement** :
```python
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_projects.db'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```
---

### `models.py` - Modèles de Données

**Rôle** : Définition des entités et relations de base de données

#### Modèle `Project`

**Propriétés Principales** :
- Champs de base : `titre`, `pvp`, `contexte`, etc.
- Champs générés par IA : `defis_techniques`, `duree_estimee`
- Relations : `evaluations` (one-to-many)
- Propriétés calculées : `latest_evaluation`, `priority_level`

**Modification Courante - Ajouter un champ** :
```python
class Project(db.Model):
    # ...existing code...
    budget_estime = db.Column(db.Integer)  # Nouveau champ
    responsable = db.Column(db.String(100))
    
    def to_dict(self):
        # ...existing code...
        return {
            # ...existing fields...
            'budget_estime': self.budget_estime,
            'responsable': self.responsable
        }
```

**Extension - Ajouter des validations** :
```python
from sqlalchemy.orm import validates

class Project(db.Model):
    # ...existing code...
    
    @validates('titre')
    def validate_titre(self, key, titre):
        if not titre or len(titre.strip()) < 5:
            raise ValueError("Le titre doit contenir au moins 5 caractères")
        return titre.strip()
    
    @validates('budget_estime')
    def validate_budget(self, key, budget):
        if budget is not None and budget < 0:
            raise ValueError("Le budget ne peut pas être négatif")
        return budget
```
#### Modèle `Evaluation`

**Propriétés Principales** :
- Scores des 6 critères (1-10)
- Score final calculé
- Suggestions IA (JSON)
- Méthodes helper pour radar charts

**Modification Courante - Ajouter un critère** :
```python
class Evaluation(db.Model):
    # ...existing code...
    impact_environnemental = db.Column(db.Float, nullable=False, default=5.0)
    
    @property
    def criteria_scores(self):
        return [
            self.valeur_business,
            self.faisabilite_technique,
            self.effort_requis,
            self.niveau_risque,
            self.urgence,
            self.alignement_strategique,
            self.impact_environnemental  # Nouveau critère
        ]
    
    @property
    def criteria_labels(self):
        return [
            'Valeur Business',
            'Faisabilité Technique',
            'Effort Requis',
            'Niveau de Risque',
            'Urgence',
            'Alignement Stratégique',
            'Impact Environnemental'  # Nouveau label
        ]
```
---

### `services/openai_service.py` - Service IA

**Rôle** : Intégration avec OpenAI pour évaluation et amélioration

#### Méthodes Principales

1. **`evaluate_project()`** : Évaluation complète d'un projet
2. **`improve_field()`** : Amélioration d'un champ spécifique
3. **`_build_evaluation_prompt()`** : Construction du prompt d'évaluation

**Modification Courante - Changer le modèle OpenAI** :
```python
def evaluate_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
    # ...existing code...
    response = self.client.chat.completions.create(
        model="gpt-4o",  # Changé de gpt-4.1 à gpt-4o
        messages=[...],
        temperature=0.5,  # Réduire la créativité
        max_tokens=3000   # Augmenter la limite
    )
```

**Extension - Ajouter une nouvelle méthode d'évaluation** :
```python
def evaluate_risk_assessment(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Évaluation spécialisée des risques"""
    prompt = f"""
    Analysez les risques spécifiques de ce projet :
    
    Projet : {project_data.get('titre', '')}
    Contexte : {project_data.get('contexte', '')}
    
    Identifiez et classez les risques par catégorie :
    - Risques techniques
    - Risques financiers  
    - Risques opérationnels
    - Risques légaux/conformité
    
    Format de réponse JSON requis...
    """
    
    try:
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Vous êtes un expert en analyse de risques..."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        logger.error(f"Risk assessment error: {e}")
        return {"risks": [], "error": "Analyse de risques indisponible"}
```
---

### `routes/main.py` - Routes Principales

**Rôle** : Contrôleurs pour les pages web principales

#### Routes Disponibles

1. **`/`** : Page d'accueil avec liste des projets
2. **`/projects/new`** : Formulaire de création (GET/POST)
3. **`/projects/<id>`** : Détails d'un projet
4. **`/projects/<id>/reevaluate`** : Réévaluation

**Modification Courante - Ajouter une route de recherche** :
```python
@main_bp.route('/projects/search')
def search_projects():
    """Recherche de projets"""
    query = request.args.get('q', '').strip()
    department = request.args.get('dept', '')
    
    if not query:
        return redirect(url_for('main.index'))
    
    # Recherche dans titre, contexte et objectifs
    projects = Project.query.filter(
        db.or_(
            Project.titre.contains(query),
            Project.contexte.contains(query),
            Project.objectifs.contains(query)
        )
    )
    
    if department:
        projects = projects.filter(Project.pvp == department)
    
    projects = projects.all()
    
    return render_template('search_results.html', 
                         projects=projects, 
                         query=query, 
                         department=department)
```

**Extension - Ajouter la pagination** :
```python
@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('PROJECTS_PER_PAGE', 10)
    
    projects = Project.query.order_by(Project.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return render_template('index.html', projects=projects)
```

**Validation Avancée** :
```python
def validate_project_form(form_data):
    """Validation centralisée des formulaires projet"""
    errors = []
    
    # Validation titre
    if not form_data.get('titre', '').strip():
        errors.append("Le titre est requis")
    elif len(form_data['titre']) > 200:
        errors.append("Le titre ne peut dépasser 200 caractères")
    
    # Validation contenus minimums
    required_fields = ['contexte', 'objectifs', 'fonctionnalites']
    for field in required_fields:
        content = form_data.get(field, '').strip()
        if len(content) < 100:
            errors.append(f"Le champ {field} doit contenir au moins 100 caractères")
    
    # Validation PVP
    if form_data.get('pvp') not in current_app.config['PVP_DEPARTMENTS']:
        errors.append("Département PVP invalide")
    
    return errors
```
---

### `routes/api.py` - API REST

**Rôle** : Endpoints API pour interactions AJAX et intégrations

#### Endpoints Disponibles

1. **`POST /api/projects`** : Création via API
2. **`POST /api/improve-field`** : Amélioration de champ
3. **`GET /api/projects/<id>/reevaluate`** : Réévaluation via API

**Modification Courante - Ajouter un endpoint de statistiques** :
```python
@api_bp.route('/stats', methods=['GET'])
def get_statistics():
    """Statistiques globales des projets"""
    try:
        total_projects = Project.query.count()
        
        # Statistiques par priorité
        high_priority = Project.query.join(Evaluation).filter(
            Evaluation.score_final >= current_app.config['PRIORITY_THRESHOLDS']['high']
        ).count()
        
        medium_priority = Project.query.join(Evaluation).filter(
            db.and_(
                Evaluation.score_final >= current_app.config['PRIORITY_THRESHOLDS']['medium'],
                Evaluation.score_final < current_app.config['PRIORITY_THRESHOLDS']['high']
            )
        ).count()
        
        low_priority = Project.query.join(Evaluation).filter(
            Evaluation.score_final < current_app.config['PRIORITY_THRESHOLDS']['medium']
        ).count()
        
        # Statistiques par département
        dept_stats = db.session.query(
            Project.pvp, 
            db.func.count(Project.id).label('count')
        ).group_by(Project.pvp).all()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_projects': total_projects,
                'priorities': {
                    'high': high_priority,
                    'medium': medium_priority,
                    'low': low_priority,
                    'unevaluated': total_projects - (high_priority + medium_priority + low_priority)
                },
                'departments': {dept: count for dept, count in dept_stats}
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': 'Erreur lors du calcul des statistiques'}), 500
```

**Extension - Middleware d'authentification API** :
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config.get('API_KEY'):
            return jsonify({'error': 'Clé API requise'}), 401
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/projects', methods=['POST'])
@require_api_key
def create_project():
    # ...existing code...
```
---

## 🔧 Patterns d'Extension Courantes

### 1. Ajouter un Nouveau Service

Créer `services/notification_service.py` :
```python
# filepath: services/notification_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class NotificationService:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def notify_project_evaluated(self, project, evaluation):
        """Notify stakeholders when project is evaluated"""
        subject = f"Projet évalué : {project.titre}"
        body = f"""
        Le projet "{project.titre}" a été évalué.
        Score final : {evaluation.score_final}
        Priorité : {project.priority_text}
        
        Consultez les détails : {url_for('main.project_detail', id=project.id, _external=True)}
        """
        
        self._send_email(
            to_email=self._get_stakeholder_email(project.pvp),
            subject=subject,
            body=body
        )
```
### 2. Ajouter une Nouvelle Page

Créer la route dans `routes/main.py` :
```python
@main_bp.route('/dashboard')
def dashboard():
    """Tableau de bord analytique"""
    # Calculs de métriques
    stats = {
        'total_projects': Project.query.count(),
        'avg_score': db.session.query(db.func.avg(Evaluation.score_final)).scalar(),
        'projects_by_month': get_projects_by_month(),
        'top_departments': get_top_departments()
    }
    
    return render_template('dashboard.html', stats=stats)
```

Créer le template `templates/dashboard.html` :
```html
{% extends "base.html" %}

{% block title %}Tableau de Bord{% endblock %}

{% block content %}
<div class="container-fluid">
    <h1>Tableau de Bord Analytique</h1>
    
    <div class="row">
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">Total Projets</h5>
                    <h2 class="text-primary">{{ stats.total_projects }}</h2>
                </div>
            </div>
        </div>
        <!-- Plus de métriques... -->
    </div>
</div>
{% endblock %}
```
### 3. Ajouter une Nouvelle Migration

Quand vous modifiez les modèles, créez une migration :
```python
# migrations/add_budget_field.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('projects', sa.Column('budget_estime', sa.Integer(), nullable=True))
    op.add_column('projects', sa.Column('responsable', sa.String(100), nullable=True))

def downgrade():
    op.drop_column('projects', 'budget_estime')
    op.drop_column('projects', 'responsable')
```
---

## 🎨 Frontend et Templates

### Structure des Templates

```
templates/
├── base.html           # Template de base avec header/footer
├── index.html          # Page d'accueil
├── new_project.html    # Formulaire création
├── project_detail.html # Détails projet avec graphiques
└── errors/             # Pages d'erreur
```

### Modification des Templates

**Ajouter un nouveau bloc dans base.html** :
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <!-- ...existing head... -->
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    
    <!-- Scripts de base -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

**Utiliser le nouveau bloc** :
```html
{% extends "base.html" %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
{% endblock %}
```
---

## 🧪 Tests et Débogage

### Structure de Tests Recommandée

```python
# tests/test_models.py
import pytest
from models import Project, Evaluation, db

class TestProjectModel:
    def test_project_creation(self, app):
        with app.app_context():
            project = Project(
                titre="Test Project",
                pvp="Technologies de l'Information",
                contexte="Context de test" * 20,
                objectifs="Objectifs de test" * 20,
                fonctionnalites="Fonctionnalités de test" * 20
            )
            db.session.add(project)
            db.session.commit()
            
            assert project.id is not None
            assert project.priority_level == 'non-évalué'

# tests/test_routes.py
def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Évaluateur de Projets' in response.data.decode()

def test_create_project_api(client):
    data = {
        'titre': 'Test API Project',
        'pvp': 'Technologies de l\'Information',
        'contexte': 'Contexte de test via API' * 10,
        'objectifs': 'Objectifs de test via API' * 10,
        'fonctionnalites': 'Fonctionnalités de test via API' * 10
    }
    
    response = client.post('/api/projects', 
                          json=data,
                          content_type='application/json')
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['success'] is True
```
### Configuration de Tests

```python
# conftest.py
import pytest
from app import create_app
from models import db
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    OPENAI_API_KEY = 'test-key'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
```
---

## 🚀 Déploiement et Production

### Variables d'Environnement Production

```bash
# .env.production
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
OPENAI_API_KEY=sk-your-real-openai-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-email-password
```

### Configuration Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
```

### Script de Déploiement

```bash
#!/bin/bash
# deploy.sh

echo "Déploiement de l'évaluateur de projets..."

# Pull latest code
git pull origin main

# Install/update dependencies
pip install -r requirements.txt

# Run migrations
python migrations/run_migrations.py

# Restart application
sudo systemctl restart project-evaluator

echo "Déploiement terminé!"
```
---

## 📝 Conventions de Développement

### Style de Code
- **PEP 8** pour Python
- **Docstrings** pour toutes les fonctions publiques
- **Type hints** pour les nouvelles fonctions
- **Logging** au lieu de `print()`

### Nomenclature
- **Français** pour les noms de variables métier
- **Anglais** pour les noms techniques
- **Snake_case** pour Python
- **CamelCase** pour les classes

### Structure des Commits
```
type(scope): description

feat(api): ajouter endpoint de statistiques
fix(models): corriger calcul score final
docs(readme): mettre à jour guide installation
style(templates): améliorer responsive design
```
---

## 🔍 Debugging et Monitoring

### Logs Structurés
```python
import logging
import json

logger = logging.getLogger(__name__)

def log_project_evaluation(project_id, scores, duration):
    """Log structured evaluation data"""
    log_data = {
        'event': 'project_evaluated',
        'project_id': project_id,
        'scores': scores,
        'evaluation_duration_ms': duration,
        'timestamp': datetime.utcnow().isoformat()
    }
    logger.info(json.dumps(log_data))
```

### Métriques de Performance
```python
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start) * 1000
        logger.info(f"{func.__name__} executed in {duration:.2f}ms")
        return result
    return wrapper

@measure_time
def evaluate_project(self, project_data):
    # ...existing code...
```
