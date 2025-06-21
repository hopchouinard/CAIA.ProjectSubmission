# Guide de Migration Multi-Providers IA

## Vue d'ensemble

Ce guide explique comment migrer votre installation existante de l'évaluateur de projets d'investissement vers la nouvelle architecture multi-providers IA, qui prend en charge OpenAI, Anthropic, Google, Azure OpenAI et Databricks.

## Architecture Mise à Jour

### Nouvelle Structure

```
services/
├── ai_service.py           # Service principal (remplace openai_service.py)
├── providers/
│   ├── base_provider.py    # Classe abstraite de base
│   ├── openai_provider.py  # Implémentation OpenAI
│   ├── anthropic_provider.py
│   ├── google_provider.py
│   ├── azure_provider.py
│   └── databricks_provider.py
├── prompt_manager.py       # Gestion des prompts YAML
└── provider_manager.py     # Logique de sélection/fallback
```

### Prompts Externalisés

```
prompts/
├── openai/
│   ├── gpt-4o/
│   ├── o3-mini/
│   └── o1-preview/
├── anthropic/
│   └── claude-3-5-sonnet/
├── google/
│   └── gemini-2.0-flash-exp/
├── azure/
│   └── gpt-4o/
└── databricks/
    └── meta-llama/
```

## Instructions de Migration

### 1. Sauvegarde

```bash
# Sauvegardez votre base de données
cp instance/projects.db instance/projects.db.backup

# Sauvegardez votre fichier .env
cp .env .env.backup
```

### 2. Installation des Nouvelles Dépendances

```bash
pip install -r requirements.txt
```

Nouvelles dépendances ajoutées :
- `anthropic>=0.52.2`
- `google-genai>=1.21.1`
- `databricks-sdk>=0.57.0`
- `PyYAML>=6.0`

### 3. Migration de la Base de Données

```bash
python migrate_db.py
```

Cette commande :
- Ajoute la table `ai_provider_configs`
- Crée les configurations par défaut pour tous les providers
- Active OpenAI comme provider principal

### 4. Configuration des Variables d'Environnement

Mettez à jour votre fichier `.env` avec les nouvelles variables :

```env
# Configuration existante (conservée)
OPENAI_API_KEY=sk-your-openai-key-here

# Nouvelles configurations (ajoutez selon vos besoins)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-api-key-here
AZURE_OPENAI_API_KEY=your-azure-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
DATABRICKS_TOKEN=your-databricks-token-here
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com

# Configuration du provider par défaut
DEFAULT_AI_PROVIDER=openai
DEFAULT_AI_MODEL=gpt-4o
ENABLE_PROVIDER_FALLBACK=true
```

### 5. Test de l'Installation

```bash
python test_migration.py
```

## Fonctionnalités Clés

### 1. Compatibilité Rétroactive

✅ **Aucun changement de l'interface utilisateur**
✅ **Même API et comportement**
✅ **Projets existants continuent de fonctionner**
✅ **Localisation française maintenue**

### 2. Gestion Multi-Providers

- **Provider Principal** : OpenAI (par défaut)
- **Fallback Automatique** : Anthropic → Google → Azure → Databricks
- **Gestion Spécialisée** : Modèles o3/o4-mini (thinking models)
- **Configuration Runtime** : Base de données pour la sélection des providers

### 3. Prompts Externalisés

- **YAML Structure** : Prompts organisés par provider/modèle
- **Templates Variables** : Substitution automatique `{variable}`
- **Paramètres Spécifiques** : Configuration par modèle
- **Fallback Templates** : Templates par défaut si spécifique non trouvé

## Utilisation Avancée

### Changement de Provider Programmatique

```python
from services import AIService

# Initialiser le service
ai_service = AIService()

# Changer le provider par défaut
ai_service.switch_provider('anthropic', 'claude-3-5-sonnet-20241022')

# Obtenir le statut des providers
status = ai_service.get_provider_status()
```

### Configuration de Nouveaux Modèles

1. **Ajout de Prompts** : Créez les fichiers YAML dans `prompts/provider/model/`
2. **Configuration DB** : Ajoutez l'entrée dans `AIProviderConfig`
3. **Activation** : Marquez `is_active=True` pour utilisation

### Gestion des Modèles Spéciaux

**Modèles Thinking (o3/o4-mini)** :
- Pas de system messages
- Pas de paramètre température
- Gestion automatique dans OpenAIProvider

**Modèles Azure** :
- Utilise deployment names au lieu de model names
- Configuration endpoint spécifique
- Authentification Azure AD supportée

## Dépannage

### Provider Non Disponible

```bash
# Vérifiez la configuration
python -c "from services import AIService; print(AIService().get_provider_status())"
```

### Erreurs de Prompts

```bash
# Listez les prompts disponibles
python -c "from services.prompt_manager import PromptManager; print(PromptManager().list_available_prompts())"
```

### Fallback Activé

Si vous voyez "Service d'évaluation temporairement indisponible" :
1. Vérifiez vos clés API
2. Testez la connectivité réseau
3. Consultez les logs d'application

## Monitoring et Logs

### Activation du Logging

```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Métriques Importantes

- Taux de succès par provider
- Temps de réponse moyen
- Utilisation du fallback
- Erreurs d'API

## Sécurité

### Bonnes Pratiques

1. **Rotation des Clés** : Planifiez la rotation régulière des clés API
2. **Environnements Séparés** : Utilisez des clés différentes pour dev/prod
3. **Monitoring** : Surveillez l'utilisation et les coûts
4. **Backup** : Maintenez des providers de secours configurés

### Variables d'Environnement

- Toutes les clés API sont chargées depuis l'environnement
- Aucune clé stockée en dur dans le code
- Configuration de production séparée

## Migration de Retour

Si vous devez revenir à l'ancienne version :

```bash
# Restaurer la base de données
cp instance/projects.db.backup instance/projects.db

# Restaurer les variables d'environnement
cp .env.backup .env

# Revenir aux imports précédents dans le code
git checkout [previous-commit] -- routes/
```

## Support

Pour obtenir de l'aide :

1. **Documentation** : Consultez `DEVELOPER_GUIDE.md`
2. **Logs** : Vérifiez les logs d'application
3. **Tests** : Lancez les scripts de test
4. **Configuration** : Validez vos variables d'environnement

## Prochaines Étapes

1. **Testez** l'évaluation avec différents providers
2. **Configurez** les providers additionnels selon vos besoins
3. **Surveillez** les performances et coûts
4. **Optimisez** la configuration des prompts

La migration preserve entièrement la fonctionnalité existante tout en ajoutant la flexibilité multi-provider pour l'avenir.
