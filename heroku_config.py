"""
Configuration pour le déploiement Heroku avec Cassandra
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Cassandra pour Heroku
# Utilisation d'un service Cassandra cloud (ex: DataStax Astra)
CASSANDRA_CONFIG = {
    'hosts': os.environ.get('CASSANDRA_HOSTS', 'localhost').split(','),
    'port': int(os.environ.get('CASSANDRA_PORT', '9042')),
    'keyspace': os.environ.get('CASSANDRA_KEYSPACE', 'football_injuries'),
    'username': os.environ.get('CASSANDRA_USERNAME'),
    'password': os.environ.get('CASSANDRA_PASSWORD'),
    'datacenter': os.environ.get('CASSANDRA_DATACENTER', 'datacenter1'),
    
    # Configuration pour Cassandra cloud (DataStax Astra)
    'secure_connect_bundle': os.environ.get('CASSANDRA_SECURE_CONNECT_BUNDLE'),
    'client_id': os.environ.get('CASSANDRA_CLIENT_ID'),
    'client_secret': os.environ.get('CASSANDRA_CLIENT_SECRET')
}

# Configuration Streamlit pour Heroku
STREAMLIT_CONFIG = {
    'server.port': int(os.environ.get('PORT', 8501)),
    'server.address': '0.0.0.0',
    'server.enableCORS': False,
    'server.enableXsrfProtection': False
}

# Configuration des APIs
API_CONFIG = {
    'football_api_key': os.environ.get('API_FOOTBALL_KEY'),
    'weather_api_key': os.environ.get('WEATHER_API_KEY')
}

# Configuration pour DataStax Astra (recommandé pour Heroku)
def get_astra_config():
    """Configuration spécifique pour DataStax Astra"""
    return {
        'secure_connect_bundle': CASSANDRA_CONFIG['secure_connect_bundle'],
        'auth_provider': {
            'username': CASSANDRA_CONFIG['client_id'],
            'password': CASSANDRA_CONFIG['client_secret']
        },
        'keyspace': CASSANDRA_CONFIG['keyspace']
    }

# Messages d'aide pour la configuration
SETUP_INSTRUCTIONS = """
🚀 Configuration Heroku + Cassandra:

1. Service Cassandra recommandé: DataStax Astra (gratuit jusqu'à 80GB)
   
2. Variables d'environnement à configurer sur Heroku:
   heroku config:set CASSANDRA_HOSTS=<your-astra-host>
   heroku config:set CASSANDRA_KEYSPACE=football_injuries
   heroku config:set CASSANDRA_CLIENT_ID=<your-client-id>
   heroku config:set CASSANDRA_CLIENT_SECRET=<your-client-secret>
   heroku config:set CASSANDRA_SECURE_CONNECT_BUNDLE=<bundle-url>
   
3. APIs:
   heroku config:set API_FOOTBALL_KEY=<your-key>
   heroku config:set WEATHER_API_KEY=<your-key>

Alternative locale: Cassandra Docker
docker run --name cassandra -p 9042:9042 -d cassandra:latest
"""

if __name__ == "__main__":
    print(SETUP_INSTRUCTIONS)