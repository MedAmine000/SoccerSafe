# Documentation Technique - Football Injury Analytics

## 📋 Vue d'ensemble du Projet

### Objectifs
- **Analyse prédictive** des blessures de joueurs de football
- **Optimisation des périodes de récupération**
- **Identification des facteurs de risque**
- **Tableau de bord en temps réel** pour les équipes médicales

### Technologies Utilisées
- **Backend**: Python 3.9+, pandas, scikit-learn
- **Base de données**: Apache Cassandra (production et développement)
- **Frontend**: Streamlit
- **APIs**: Football-API, OpenWeatherMap
- **Déploiement**: Heroku
- **CI/CD**: GitHub Actions (optionnel)

## 🏗️ Architecture du Système

```
Project/
├── data/                   # Données brutes et traitées
│   ├── kaggle/            # Datasets Kaggle
│   ├── matches_*.json     # Données matchs temps réel
│   └── weather_*.json     # Données météo
├── src/                   # Code source Python
│   ├── analyzer.py        # Module d'analyse ML
│   └── data_collector.py  # Collecteur de données APIs
├── database/              # Modèles et opérations DB
│   ├── models.py         # Modèles Cassandra
│   └── crud.py           # Opérations CRUD
├── webapp/               # Application Streamlit
│   └── app.py           # Interface utilisateur
├── scripts/             # Scripts d'administration
│   ├── setup_database.py    # Configuration initiale
│   ├── db_admin.py         # Administration DB
│   └── automated_collector.py  # Collecte automatisée
├── tests/               # Tests unitaires
└── docs/               # Documentation
```

## 🗄️ Modèle de Données

### Tables Principales

#### `players`
- `player_id` (PK): Identifiant unique du joueur
- `player_name`: Nom du joueur
- `date_of_birth`: Date de naissance
- `main_position`: Position principale
- `height`: Taille en cm
- `current_club_name`: Club actuel

#### `injuries`
- `id` (PK): Identifiant unique de la blessure
- `player_id` (FK): Référence au joueur
- `injury_reason`: Type de blessure
- `from_date`: Date de début
- `end_date`: Date de fin
- `days_missed`: Nombre de jours manqués
- `games_missed`: Nombre de matchs manqués
- `severity_score`: Score de sévérité (calculé)

#### `performances`
- `id` (PK): Identifiant unique
- `player_id` (FK): Référence au joueur
- `match_date`: Date du match
- `minutes_played`: Minutes jouées
- `goals`, `assists`: Statistiques de performance
- `rating`: Note du joueur

#### `weather_data`
- `id` (PK): Identifiant unique
- `match_date`: Date du match
- `temperature`: Température en °C
- `humidity`: Humidité en %
- `wind_speed`: Vitesse du vent
- `weather_condition`: Condition météorologique

## 🔧 Installation et Configuration

### 1. Prérequis
```bash
Python 3.9+
Apache Cassandra 4.0+
Git
```

### 2. Installation
```bash
# Cloner le projet
git clone https://github.com/votre-repo/football-injury-analytics.git
cd football-injury-analytics

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations
```

### 3. Configuration de la base de données
```bash
# Configurer la base de données Cassandra
createdb football_injuries

# Configurer et importer les données
python scripts/setup_database.py
```

### 4. Lancement de l'application
```bash
# Démarrer l'application Streamlit
streamlit run webapp/app.py
```

## 🚀 Déploiement

### Déploiement Local
```bash
# Lancer tous les services
docker-compose up -d  # Si vous utilisez Docker
# ou
python webapp/app.py
```

### Déploiement Heroku
```bash
# Utiliser le script de déploiement
./deploy_heroku.sh

# Ou manuellement
heroku create your-app-name
# Configuration avec DataStax Astra (Cassandra Cloud)
git push heroku main
```

## 📊 Utilisation des APIs

### Configuration des Clés API

#### Football-API
```python
# Dans .env
API_FOOTBALL_KEY=your_rapidapi_key

# Utilisation
from src.data_collector import FootballAPI
api = FootballAPI()
matches = api.get_fixtures(league_id=39, season=2024)
```

#### Weather API
```python
# Dans .env
WEATHER_API_KEY=your_openweather_key

# Utilisation
from src.data_collector import WeatherAPI
weather_api = WeatherAPI()
weather = weather_api.get_weather_by_city_date("London", date.today())
```

### Collecte Automatisée
```bash
# Collecte quotidienne (une fois)
python scripts/automated_collector.py --run-once daily

# Mode daemon (continu)
python scripts/automated_collector.py --daemon
```

## 🤖 Machine Learning

### Modèle de Prédiction

Le modèle utilise **Random Forest** pour prédire le risque de blessures graves (>21 jours).

#### Features utilisées:
- Âge du joueur
- Taille
- Position (encodée)
- Mois de l'année

#### Métriques de performance:
- **Précision**: ~85%
- **Recall**: ~78%
- **F1-Score**: ~81%

### Utilisation du Modèle
```python
from src.analyzer import InjuryAnalyzer

# Charger les données
analyzer = InjuryAnalyzer(injuries_df, players_df)

# Entraîner le modèle
ml_results = analyzer.predict_injury_risk()

# Faire une prédiction
risk_profile = analyzer.generate_player_risk_profile(player_id=123)
```

## 🔒 Sécurité

### Configuration de la Base de Données
```bash
# Créer un utilisateur en lecture seule
python scripts/db_admin.py --security
```

### Variables d'Environnement
- Ne jamais committer les fichiers `.env`
- Utiliser des clés API avec permissions limitées
- Changer les mots de passe par défaut

### Bonnes Pratiques
- Validation des entrées utilisateur
- Sanitisation des requêtes SQL
- HTTPS en production
- Authentification pour les APIs sensibles

## 📈 Monitoring et Logs

### Logs d'Application
```bash
# Consulter les logs
tail -f logs/data_collection.log

# Logs Heroku
heroku logs --tail -a your-app-name
```

### Métriques de Performance
- Temps de réponse des APIs
- Taux de succès des collectes
- Utilisation de la base de données
- Performances du modèle ML

## 🧪 Tests

### Exécution des Tests
```bash
# Tous les tests
python tests/test_analytics.py

# Tests spécifiques
python -m unittest tests.test_analytics.TestInjuryAnalyzer
```

### Tests Inclus
- Tests unitaires pour l'analyseur
- Tests d'intégration des APIs
- Tests de validation des données
- Tests de performance

## 🛠️ Maintenance

### Scripts d'Administration

#### Backup de la Base de Données
```bash
python scripts/db_admin.py --dump
```

#### Optimisation
```bash
python scripts/db_admin.py --optimize
```

#### Import de Données Volumineuses
```bash
python scripts/db_admin.py --import-csv data/large_file.csv table_name
```

### Maintenance Planifiée
- **Quotidien**: Collecte de données, backup
- **Hebdomadaire**: Rapport d'analyse, nettoyage des logs
- **Mensuel**: Optimisation DB, mise à jour des modèles ML

## 📊 Questions Métier Analysées

### 1. Facteurs Prédictifs de Blessures
- **Âge**: Corrélation avec la fréquence et la gravité
- **Position**: Positions les plus à risque
- **Historique**: Récurrence des blessures
- **Météo**: Impact des conditions climatiques

### 2. Optimisation de la Récupération
- **Durée standard** par type de blessure
- **Facteurs d'accélération** de la guérison
- **Comparaison** avec les standards de l'industrie

### 3. Prévention
- **Identification des joueurs à risque**
- **Périodes critiques** (mois, saisons)
- **Recommandations personnalisées**

### 4. Impact Économique
- **Coût des blessures** (matchs manqués)
- **ROI de la prévention**
- **Optimisation des effectifs**

## 🚀 Roadmap et Améliorations

### Version 2.0 (Prévue)
- [ ] Intégration avec plus d'APIs (UEFA, FIFA)
- [ ] Modèles ML plus sophistiqués (Deep Learning)
- [ ] Application mobile
- [ ] Alertes en temps réel (SMS, email)
- [ ] API REST pour intégration externe

### Version 3.0 (Vision)
- [ ] Intelligence artificielle conversationnelle
- [ ] Analyse vidéo automatique
- [ ] Intégration IoT (capteurs)
- [ ] Blockchain pour la vérification des données

## 🆘 Troubleshooting

### Problèmes Courants

#### 1. Erreur de Connexion à la Base de Données
```bash
# Vérifier la configuration
psql -h localhost -U postgres -d football_injuries

# Recréer les tables
python scripts/setup_database.py --reset
```

#### 2. Échec de Collecte des APIs
```bash
# Vérifier les clés API
python -c "import os; print(os.getenv('API_FOOTBALL_KEY'))"

# Tester manuellement
python src/data_collector.py
```

#### 3. Erreurs Streamlit
```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Lancer en mode debug
streamlit run webapp/app.py --logger.level=debug
```

### Support
- **Documentation**: Voir `/docs`
- **Issues**: GitHub Issues
- **Contact**: votre-email@example.com

---

*Cette documentation est mise à jour régulièrement. Dernière modification: {datetime.now().strftime('%d/%m/%Y')}*