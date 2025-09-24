# Projet d'Analyse des Blessures dans le Football

## 📋 Description du Projet
Analyse complète des blessures de joueurs de football avec intégration de données en temps réel et création d'une webapp analytique.

## 🎯 Objectifs Métier
1. **Prédiction des risques de blessures** par joueur et position
2. **Optimisation des périodes de récupération** 
3. **Analyse des facteurs de risque** (âge, position, météo, charge de travail)
4. **Tableau de bord en temps réel** pour les équipes médicales
 
## 📊 Sources de Données
- **Données historiques** : player_injuries.csv, player_profiles.csv
- **API Football** : matchs en temps réel, calendrier
- **API Météo** : conditions climatiques lors des matchs
- **Kaggle Dataset** : statistiques de performance complémentaires
  
## 🏗️ Architecture

```
Project/
├── data/           # Données brutes et traitées
├── src/            # Code source Python
├── database/       # Scripts DB et modèles
├── webapp/         # Application Streamlit
├── scripts/        # Scripts d'administration
└── docs/          # Documentation
```

## 🚀 Installation

1. Cloner le projet
2. Copier `.env.example` vers `.env` et configurer
3. Installer les dépendances : `pip install -r requirements.txt`
4. Configurer la base de données : `python scripts/setup_database.py`
5. Lancer l'application : `streamlit run webapp/app.py`

## 📈 Questions Métier Analysées
1. Quels sont les facteurs prédictifs de blessures graves ?
2. Quelle est la durée optimale de récupération par type de blessure ?
3. Y a-t-il une corrélation entre conditions météo et blessures ?
4. Comment optimiser la rotation des joueurs pour minimiser les risques ?

## 🛠️ Technologies Utilisées
- **Backend** : Python, pandas, scikit-learn
- **Base de données** : Cassandra (Apache Cassandra)
- **Visualisation** : Streamlit, Plotly, Seaborn
- **APIs** : Football-API, OpenWeatherMap
- **Déploiement** : Heroku (prévu)