# Migration vers Cassandra - Guide complet

## ✅ Migration terminée

La base de données du projet a été **complètement migrée** de PostgreSQL/MongoDB vers **Apache Cassandra**.

## 🔄 Changements effectués

### 1. **Base de données**
- ❌ PostgreSQL + MongoDB 
- ✅ **Apache Cassandra** (architecture NoSQL distribuée)

### 2. **Drivers et dépendances**
- ❌ `psycopg2-binary`, `pymongo`, `sqlalchemy`
- ✅ `cassandra-driver==3.28.0`

### 3. **Modèles de données**
- ❌ SQLAlchemy ORM
- ✅ Modèles Cassandra natifs avec CQL

### 4. **Opérations CRUD**
- ❌ Requêtes SQL et MongoDB queries
- ✅ Requêtes CQL (Cassandra Query Language)

## 📁 Fichiers modifiés

### Base de données
- ✅ `database/models.py` - Modèles Cassandra complets
- ✅ `database/crud.py` - CRUD operations en CQL
- ✅ `.env.example` - Configuration Cassandra

### Scripts
- ✅ `scripts/setup_database.py` - Setup keyspace/tables
- ✅ `scripts/cassandra_admin.py` - Administration Cassandra
- ❌ `scripts/db_admin.py` - Supprimé (PostgreSQL)
- ✅ `scripts/automated_collector.py` - Mis à jour pour Cassandra

### Déploiement
- ✅ `requirements.txt` - Dépendances Cassandra
- ✅ `deploy_heroku.sh` - Déploiement avec DataStax Astra
- ✅ `heroku_config.py` - Configuration cloud Cassandra

### Configuration
- ✅ `setup_local_cassandra.py` - Installation locale automatique
- ✅ `import_data.py` - Import des CSV existants

### Documentation
- ✅ `README.md` - Mis à jour pour Cassandra
- ✅ `docs/TECHNICAL_DOCUMENTATION.md` - Architecture Cassandra
- ✅ `PRESENTATION.md` - Diagrammes mis à jour

## 🚀 Démarrage rapide

### Option 1: Installation locale automatique
```bash
# Installation et configuration automatique de Cassandra
python setup_local_cassandra.py

# Démarrer Cassandra
./start_cassandra.sh  # Linux/Mac
# ou
./start_cassandra.bat  # Windows

# Configurer la base de données
python scripts/setup_database.py

# Importer les données existantes
python import_data.py

# Démarrer l'application
streamlit run webapp/app.py
```

### Option 2: Cassandra Cloud (DataStax Astra)
```bash
# 1. Créer un compte sur https://astra.datastax.com
# 2. Créer une base "football-injuries"
# 3. Télécharger le Secure Connect Bundle
# 4. Configurer les variables d'environnement:

export CASSANDRA_HOSTS="your-astra-host"
export CASSANDRA_KEYSPACE="football_injuries"
export CASSANDRA_CLIENT_ID="your-client-id"
export CASSANDRA_CLIENT_SECRET="your-client-secret"
export CASSANDRA_SECURE_CONNECT_BUNDLE="bundle-url"

# 5. Configurer et importer
python scripts/setup_database.py
python import_data.py
streamlit run webapp/app.py
```

## 🛠️ Commandes utiles

### Administration
```bash
# Informations sur la base
python scripts/cassandra_admin.py --info

# Sauvegarde complète
python scripts/cassandra_admin.py --backup

# Restauration
python scripts/cassandra_admin.py --restore backup_file.json

# Optimisation
python scripts/cassandra_admin.py --optimize
```

### Développement
```bash
# Variables d'environnement locales
cp .env.local .env

# Test de connexion
python -c "from database.models import get_cassandra_session; print('✅ Connexion OK')"

# Import des données
python import_data.py
```

## 📊 Structure Cassandra

### Keyspace: `football_injuries`
```cql
-- Tables principales
players          -- Profils des joueurs
injuries         -- Historique des blessures  
performances     -- Statistiques de match
weather_data     -- Données météorologiques
api_logs         -- Logs des appels API
```

### Exemple de requêtes CQL
```cql
-- Joueurs par position
SELECT * FROM players WHERE position = 'Midfielder';

-- Blessures récentes
SELECT * FROM injuries WHERE from_date >= '2024-01-01';

-- Performances d'un joueur
SELECT * FROM performances WHERE player_id = 123456;
```

## 🔧 Déploiement Heroku

### Avec DataStax Astra (recommandé)
```bash
# Configuration automatique
./deploy_heroku.sh

# Configuration manuelle des variables Cassandra
heroku config:set CASSANDRA_HOSTS="your-astra-host"
heroku config:set CASSANDRA_KEYSPACE="football_injuries"
heroku config:set CASSANDRA_CLIENT_ID="your-client-id"
heroku config:set CASSANDRA_CLIENT_SECRET="your-client-secret"

# Déploiement
git push heroku main
```

## 📈 Avantages de Cassandra

### ✅ Scalabilité
- Distribution automatique des données
- Réplication native
- Performance linéaire

### ✅ Disponibilité
- Pas de point de défaillance unique
- Réplication multi-datacenter
- Tolérance aux pannes

### ✅ Performance
- Lectures/écritures ultra-rapides
- Optimisé pour les gros volumes
- Pas de jointures coûteuses

### ✅ Flexibilité
- Schéma flexible
- Types de données riches
- Partitioning intelligent

## 🔍 Données existantes

Les fichiers CSV sont **entièrement compatibles** :
- ✅ `player_profiles.csv` (92K+ joueurs)
- ✅ `player_injuries.csv` (143K+ blessures)

Import automatique avec `python import_data.py`

## 🆘 Dépannage

### Problème de connexion
```bash
# Vérifier Cassandra local
cqlsh 127.0.0.1 9042

# Vérifier les logs
tail -f ~/cassandra/logs/system.log
```

### Problème d'import
```bash
# Vérifier les tables
python scripts/cassandra_admin.py --info

# Recréer les tables
python scripts/setup_database.py
```

### Performance
```bash
# Optimiser les tables
python scripts/cassandra_admin.py --optimize

# Statistiques
python scripts/cassandra_admin.py --stats
```

## 📞 Support

En cas de problème :
1. Vérifier les logs Cassandra
2. Tester la connexion avec `cqlsh`
3. Consulter la documentation DataStax
4. Utiliser les outils d'administration fournis