# Évaluateur de Projets d'Investissement

Une application web Flask complète pour la gestion et l'évaluation automatique de projets d'investissement utilisant l'IA OpenAI GPT-4o.

## 🎯 Objectif

Cette application permet aux entreprises d'investissement de soumettre, évaluer et prioriser automatiquement leurs projets selon 6 critères pondérés, avec classification en 3 niveaux de priorité et suggestions d'amélioration générées par l'IA.

## ✨ Fonctionnalités Principales

### 🏠 Tableau de Bord
- Liste de tous les projets triés par score décroissant
- Statistiques en temps réel (priorités élevée, moyenne, faible)
- Navigation intuitive vers les détails des projets

### ➕ Création de Projets
- Formulaire interactif avec validation
- Amélioration des champs en temps réel via IA
- Auto-sauvegarde en cours de saisie
- Évaluation automatique complète

### 📊 Évaluation par IA
- 6 critères d'évaluation pondérés :
  - **Valeur Business** (25%) - Impact et ROI
  - **Faisabilité Technique** (20%) - Complexité technologique
  - **Effort Requis** (15%) - Ressources nécessaires (inversé)
  - **Niveau de Risque** (15%) - Risques globaux (inversé)
  - **Urgence** (15%) - Pression temporelle
  - **Alignement Stratégique** (10%) - Cohérence objectifs

### 🎨 Visualisation
- Graphique radar interactif (Chart.js)
- Barres de progression animées
- Badges de priorité colorés
- Interface responsive en français québécois

## 🛠 Architecture Technique

### Stack Technologique
- **Backend** : Python Flask 3.0+ avec SQLAlchemy
- **Base de données** : SQLite (development)
- **Frontend** : Bootstrap 5 + Chart.js
- **IA** : OpenAI GPT-4o
- **Styles** : CSS personnalisé avec design système cohérent

### Structure du Projet
```
project-evaluator/
├── app.py                 # Point d'entrée Flask
├── config.py             # Configuration et variables d'environnement
├── models.py             # Modèles SQLAlchemy (Project, Evaluation)
├── routes/               # Routes organisées par fonctionnalité
│   ├── main.py          # Routes principales (index, détails, création)
│   ├── api.py           # API REST pour AJAX
│   └── __init__.py
├── services/             # Services métier
│   ├── openai_service.py # Service d'intégration OpenAI
│   └── __init__.py
├── templates/            # Templates Jinja2
│   ├── base.html        # Template de base
│   ├── index.html       # Page d'accueil
│   ├── new_project.html # Formulaire création
│   ├── project_detail.html # Détails projet
│   └── errors/          # Pages d'erreur
├── static/               # Assets statiques
│   ├── css/style.css    # Styles personnalisés
│   └── js/app.js        # JavaScript principal
├── requirements.txt      # Dépendances Python
└── .env.example         # Exemple de configuration
```

## 🚀 Installation et Configuration

### 1. Prérequis
- Python 3.8+
- Clé API OpenAI GPT-4o
- Git

### 2. Installation
```bash
# Cloner le repository
cd project-evaluator

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate

# Ou sur Linux/macOS
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer .env avec vos valeurs
# OPENAI_API_KEY=votre_clé_api_openai
# SECRET_KEY=votre_clé_secrète_flask
```

### 4. Lancement
```bash
# Lancer l'application
python app.py

# L'application sera accessible sur http://localhost:5000
```

## 📋 Variables d'Environnement

Créez un fichier `.env` basé sur `.env.example` :

```env
# Configuration OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here

# Configuration Flask
SECRET_KEY=your-secret-key-for-sessions
FLASK_ENV=development
FLASK_DEBUG=True

# Base de données
DATABASE_URL=sqlite:///projects.db

# Application
APP_NAME=Évaluateur de Projets d'Investissement
```

## 🎯 Système de Scoring

### Formule de Calcul
```
Score Final = (Valeur Business × 0.25) + (Faisabilité × 0.20) + 
              (Effort × 0.15) + (Risque × 0.15) + 
              (Urgence × 0.15) + (Alignement × 0.10)
```

### Classification des Priorités
- **🔴 Priorité Élevée** (≥ 7.0) : "Lancement immédiat"
- **🟠 Priorité Moyenne** (4.0 - 6.9) : "Planification court terme"  
- **🟢 Priorité Faible** (< 4.0) : "Évaluation future"

## 🎨 Guide de Style

### Couleurs Principales
- **Vert principal** : #046B67
- **Bleu principal** : #9AC9D3  
- **Marine** : #232C55
- **Orange accent** : #DC6137

### Interface Utilisateur
- Tous les textes en français québécois formel
- Formatage des nombres : espaces pour milliers, virgules pour décimales
- Format de date : AAAA-MM-JJ
- Animations fluides (max 0.5s)

## 🔧 API Endpoints

### Routes Principales
- `GET /` - Page d'accueil avec liste des projets
- `GET /projects/new` - Formulaire de création
- `POST /projects/new` - Création et évaluation du projet
- `GET /projects/<id>` - Détails du projet
- `GET /projects/<id>/reevaluate` - Réévaluation du projet

### API REST
- `POST /api/projects` - Créer un projet via API
- `POST /api/improve-field` - Améliorer un champ spécifique
- `GET /api/projects/<id>/reevaluate` - Réévaluer via API
- `GET /api/projects/<id>` - Récupérer les détails via API

## 🤖 Intégration OpenAI

### Prompts Utilisés
1. **Évaluation complète** : Analyse globale selon les 6 critères
2. **Amélioration de champs** : Suggestions d'amélioration contextuelles
3. **Format de réponse** : JSON structuré pour parsing fiable

### Gestion d'Erreurs
- Timeout après 30 secondes
- Messages d'erreur en français
- Valeurs de fallback en cas d'échec
- Logs détaillés pour débogage

## 📊 Données de Démonstration

L'application inclut 3 projets d'exemple :
1. **Plateforme de Commerce Électronique B2B**
2. **Système de Gestion des Ressources Humaines**  
3. **Application Mobile de Service Client**

## 🔐 Sécurité

- Variables d'environnement pour les clés API
- Validation côté serveur de tous les inputs
- Protection CSRF intégrée à Flask-WTF
- Sanitisation des données utilisateur

## 🚀 Déploiement

### Configuration Production
```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://user:pass@host:port/db
```

### Recommandations
- Utiliser PostgreSQL en production
- Configurer HTTPS
- Implémenter la mise en cache
- Monitorer les logs et performances

## 🧪 Tests et Qualité

### Validation
- Validation des formulaires côté client et serveur
- Gestion d'erreurs complète
- Messages d'erreur localisés en français
- Tests de charge pour l'API OpenAI

### Performance
- Pagination automatique (si > 20 projets)
- Mise en cache des évaluations
- Chargement asynchrone des suggestions
- Optimisation des requêtes base de données

## 📱 Responsive Design

- Interface optimisée pour desktop (min 1200px)
- Navigation tactile sur mobile
- Composants Bootstrap 5 responsive
- Icônes Bootstrap Icons

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Consulter les logs dans la console
- Vérifier la configuration OpenAI
- S'assurer que toutes les dépendances sont installées
- Contacter l'équipe de développement

## 🔄 Mise à Jour

### Version 1.0.0
- ✅ Création et évaluation de projets
- ✅ Interface en français québécois
- ✅ Intégration OpenAI GPT-4o
- ✅ Visualisations interactives
- ✅ Système de priorités automatique
- ✅ Suggestions d'amélioration IA

---

**Développé avec ❤️ pour l'évaluation intelligente de projets d'investissement**
