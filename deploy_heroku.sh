#!/bin/bash

# Script de déploiement pour Heroku avec Cassandra
# Usage: ./deploy_heroku.sh

echo "🚀 Déploiement sur Heroku avec Cassandra"

# Vérifier si Heroku CLI est installé
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI n'est pas installé"
    echo "Installez-le depuis: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Nom de l'application Heroku
APP_NAME="football-injury-analytics"

echo "📦 Création de l'application Heroku..."
heroku create $APP_NAME --region eu

echo "🔧 Configuration des variables d'environnement..."
heroku config:set -a $APP_NAME \
    API_FOOTBALL_KEY="your_api_key_here" \
    WEATHER_API_KEY="your_weather_api_key" \
    PYTHONPATH="/app"

echo "🗄️ Configuration Cassandra..."
echo "⚠️  IMPORTANT: Configurez manuellement les variables Cassandra:"
echo ""
echo "Option 1 - DataStax Astra (recommandé):"
echo "1. Créez un compte sur https://astra.datastax.com"
echo "2. Créez une base de données 'football-injuries'"
echo "3. Téléchargez le Secure Connect Bundle"
echo "4. Configurez les variables:"
echo ""
echo "heroku config:set -a $APP_NAME \\"
echo "    CASSANDRA_HOSTS=<your-astra-host> \\"
echo "    CASSANDRA_KEYSPACE=football_injuries \\"
echo "    CASSANDRA_CLIENT_ID=<your-client-id> \\"
echo "    CASSANDRA_CLIENT_SECRET=<your-client-secret> \\"
echo "    CASSANDRA_SECURE_CONNECT_BUNDLE=<bundle-url>"
echo ""
echo "Option 2 - Cassandra on Compose/ScaleGrid:"
echo "heroku config:set -a $APP_NAME \\"
echo "    CASSANDRA_HOSTS=<your-host> \\"
echo "    CASSANDRA_PORT=9042 \\"
echo "    CASSANDRA_KEYSPACE=football_injuries \\"
echo "    CASSANDRA_USERNAME=<username> \\"
echo "    CASSANDRA_PASSWORD=<password>"
echo ""
echo "Appuyez sur Entrée quand c'est fait..."
read -p ""

echo "📋 Configuration du buildpack Python..."
heroku buildpacks:set heroku/python -a $APP_NAME

echo "📤 Préparation du code pour le déploiement..."
git add .
git commit -m "Deploy to Heroku with Cassandra"

echo "🚀 Déploiement du code..."
git push heroku main

echo "🏃‍♂️ Démarrage de l'application..."
heroku ps:scale web=1 -a $APP_NAME

echo "🗄️ Configuration initiale de Cassandra..."
echo "Exécution du setup de la base de données..."
heroku run python scripts/setup_database.py -a $APP_NAME

echo "🌐 Ouverture de l'application..."
heroku open -a $APP_NAME

echo "✅ Déploiement terminé!"
echo "📊 URL de l'application: https://$APP_NAME.herokuapp.com"
echo "📋 Logs en temps réel: heroku logs --tail -a $APP_NAME"
echo ""
echo "🔧 Commandes utiles:"
echo "heroku config -a $APP_NAME                    # Voir la config"
echo "heroku logs --tail -a $APP_NAME               # Voir les logs"
echo "heroku run python scripts/setup_database.py -a $APP_NAME # Reconfigurer DB"
echo "heroku run python scripts/cassandra_admin.py --info -a $APP_NAME # Info DB"