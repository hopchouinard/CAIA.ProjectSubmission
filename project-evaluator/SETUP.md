# Guide d'Installation et de Démarrage

## 🚀 Démarrage Rapide

### Option 1: Script Automatique (Recommandé)

**Windows:**
```bash
# Double-cliquez sur start.bat ou exécutez dans PowerShell:
.\start.bat
```

**Linux/macOS:**
```bash
# Rendez le script exécutable puis lancez-le:
chmod +x start.sh
./start.sh
```

### Option 2: Installation Manuelle

1. **Créer un environnement virtuel:**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

2. **Installer les dépendances:**
```bash
pip install -r requirements.txt
```

3. **Configurer l'environnement:**
```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer .env et ajouter votre clé API OpenAI
# OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

4. **Lancer l'application:**
```bash
python app.py
```

## 🔑 Configuration OpenAI

1. **Obtenir une clé API OpenAI:**
   - Allez sur https://platform.openai.com/api-keys
   - Créez un nouveau projet ou utilisez un existant
   - Générez une nouvelle clé API secrète
   - Copiez la clé (commence par `sk-`)

2. **Configurer la clé dans .env:**
```env
OPENAI_API_KEY=sk-votre-clé-api-openai-ici
```

## 📊 Première Utilisation

1. **Accéder à l'application:**
   - Ouvrez votre navigateur
   - Allez à http://localhost:5000

2. **Découvrir les projets d'exemple:**
   - L'application inclut 3 projets de démonstration
   - Explorez les détails pour comprendre le système d'évaluation

3. **Créer votre premier projet:**
   - Cliquez sur "Nouveau Projet"
   - Remplissez le formulaire
   - Utilisez le bouton "Évaluer" pour améliorer vos textes
   - Soumettez pour évaluation complète

## 🔧 Dépannage

### Erreur: "Module not found"
```bash
# Assurez-vous que l'environnement virtuel est activé
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# Réinstallez les dépendances
pip install -r requirements.txt
```

### Erreur: "OpenAI API Key not found"
- Vérifiez que votre clé API est correctement configurée dans .env
- Assurez-vous que la clé commence par `sk-`
- Vérifiez que votre compte OpenAI a du crédit disponible

### Erreur: "Port already in use"
```bash
# Changer le port dans app.py ligne finale:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Base de données corrompue
```bash
# Supprimez le fichier de base de données pour le régénérer
rm instance/projects.db
# Relancez l'application
python app.py
```

## 🛠 Développement

### Structure du Projet
```
project-evaluator/
├── app.py              # Point d'entrée
├── config.py           # Configuration
├── models.py           # Modèles de données
├── routes/             # Routes web
├── services/           # Services métier
├── templates/          # Templates HTML
├── static/             # CSS/JS
└── instance/           # Base de données
```

### Ajouter de Nouvelles Fonctionnalités

1. **Nouvelle route:**
   - Ajoutez dans `routes/main.py` ou `routes/api.py`

2. **Nouveau modèle:**
   - Modifiez `models.py`
   - Supprimez `instance/projects.db` pour régénérer

3. **Nouveaux critères d'évaluation:**
   - Modifiez `config.py` (EVALUATION_WEIGHTS)
   - Mettez à jour `services/openai_service.py`

## 📝 API Documentation

### Endpoints Principaux
- `GET /` - Page d'accueil
- `GET /projects/new` - Formulaire création
- `POST /projects/new` - Créer projet
- `GET /projects/<id>` - Détails projet

### API REST
- `POST /api/projects` - Créer via API
- `POST /api/improve-field` - Améliorer champ
- `GET /api/projects/<id>/reevaluate` - Réévaluer

## 🔒 Sécurité

- Ne jamais committer le fichier `.env`
- Utilisez des clés secrètes fortes en production
- Configurez HTTPS en production
- Limitez l'accès API OpenAI si nécessaire

## 📞 Support

Si vous rencontrez des problèmes:
1. Vérifiez les logs dans le terminal
2. Consultez ce guide de dépannage
3. Vérifiez que Python 3.8+ est installé
4. Assurez-vous que votre clé OpenAI est valide et a du crédit

## 🎯 Prochaines Étapes

1. **Personnalisation:**
   - Modifiez les critères d'évaluation dans `config.py`
   - Adaptez les prompts dans `services/openai_service.py`
   - Personnalisez l'interface dans `templates/`

2. **Déploiement:**
   - Utilisez PostgreSQL en production
   - Configurez un serveur web (Nginx + Gunicorn)
   - Implémentez la surveillance et les logs

3. **Fonctionnalités Avancées:**
   - Authentification utilisateur
   - Historique des évaluations
   - Exports PDF/Excel
   - Notifications par email
