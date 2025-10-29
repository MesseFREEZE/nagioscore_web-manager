#!/bin/bash

# Script de démarrage pour Nagios Web Config Manager

echo "==================================================="
echo "  Nagios Web Configuration Manager"
echo "==================================================="
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "⚠️  Environnement virtuel non trouvé"
    echo "   Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "   ✓ Environnement virtuel créé"
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances si nécessaire
if ! pip list | grep -q Flask; then
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt
    echo "   ✓ Dépendances installées"
fi

# Vérifier les droits sur les répertoires Nagios
NAGIOS_ETC="/usr/local/nagios/etc"
if [ ! -r "$NAGIOS_ETC" ]; then
    echo ""
    echo "⚠️  ATTENTION: Pas d'accès en lecture à $NAGIOS_ETC"
    echo "   Exécutez cette commande pour corriger:"
    echo "   sudo usermod -aG nagios $USER"
    echo "   Puis reconnectez-vous"
    echo ""
fi

# Configurer les variables d'environnement si non définies
export FLASK_APP=app.py
export NAGIOS_BASE_PATH=${NAGIOS_BASE_PATH:-/usr/local/nagios/etc}

echo ""
echo "🚀 Démarrage de l'application Flask..."
echo "   URL: http://0.0.0.0:5000"
echo "   Ctrl+C pour arrêter"
echo ""
echo "📝 Logs ci-dessous:"
echo "---------------------------------------------------"

# Démarrer l'application
python app.py
