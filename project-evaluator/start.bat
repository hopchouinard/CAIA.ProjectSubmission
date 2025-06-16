@echo off
echo Démarrage de l'Évaluateur de Projets d'Investissement...
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERREUR: Python n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Python 3.8+ depuis https://python.org
    pause
    exit /b 1
)

REM Naviguer vers le dossier du projet
cd /d "%~dp0"

REM Vérifier si l'environnement virtuel existe
if not exist ".venv" (
    echo Création de l'environnement virtuel...
    python -m venv .venv
)

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

REM Installer les dépendances
echo Installation des dépendances...
pip install -r requirements.txt

REM Vérifier si le fichier .env existe
if not exist ".env" (
    echo ATTENTION: Fichier .env manquant
    echo Copie du fichier d'exemple...
    copy .env.example .env
    echo.
    echo IMPORTANT: Veuillez éditer le fichier .env pour ajouter votre clé API OpenAI
    echo Ouvrez .env et remplacez "your_openai_api_key_here" par votre vraie clé API
    echo.
    pause
)

REM Lancer l'application
echo Lancement de l'application Flask...
echo L'application sera accessible sur http://localhost:5000
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.
python app.py

pause
