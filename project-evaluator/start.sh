#!/bin/bash

echo "Démarrage de l'Évaluateur de Projets d'Investissement..."
echo

# Vérifier si Python est installé
if ! command -v python3 &>/dev/null; then
    echo "ERREUR: Python3 n'est pas installé"
    echo "Veuillez installer Python 3.8+ depuis https://python.org"
    exit 1
fi

# Naviguer vers le dossier du projet
cd "$(dirname "$0")"

# Vérifier si l'environnement virtuel existe
if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv .venv
fi

# Activer l'environnement virtuel
source .venv/bin/activate

# Installer les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Vérifier si le fichier .env existe
if [ ! -f ".env" ]; then
    echo "ATTENTION: Fichier .env manquant"
    echo "Copie du fichier d'exemple..."
    cp .env.example .env
    echo
    echo "IMPORTANT: Veuillez éditer le fichier .env pour ajouter votre clé API OpenAI"
    echo "Ouvrez .env et remplacez 'your_openai_api_key_here' par votre vraie clé API"
    echo
    read -p "Appuyez sur Entrée pour continuer..."
fi

# Lancer l'application
echo "Lancement de l'application Flask..."
echo "L'application sera accessible sur http://localhost:5000"
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo
python app.py
