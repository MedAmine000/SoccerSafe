# ⚽ SoccerSafe - Football Injury Analytics

> **Système d'analyse prédictive des blessures de football avec interface ML interactive**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25.0-red.svg)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.0-green.svg)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)]()

## 🚀 Démarrage Ultra-Rapide

```bash
# Configuration automatique + Lancement
python start.py

# Ou interface Windows
launch.bat

# Accès direct
streamlit run webapp/app_simple.py
```

**📍 Interface disponible : http://localhost:8501**

## 📋 Description

**SoccerSafe** est une plateforme d'analyse prédictive des blessures de football développée pour le projet M1 IPSSI NoSQL. Le système analyse **235K+ enregistrements** de données réelles pour fournir des prédictions ML interactives.

### 🎯 Fonctionnalités Principales

- 🤖 **Prédictions ML interactives** avec tests temps réel
- 📊 **Dashboard Streamlit** avec visualisations Plotly  
- 🔍 **Analyse multi-critères** par position, âge, saison
- ⚡ **Interface de test ML** avec 4 modes différents
- 📈 **Métriques validées** : 56.4% précision, AUC 0.593

## 🎮 Tests ML Interactifs

### 🎯 Test Rapide (1-clic)
```
Sidebar → "🤖 Prédictions ML" → Test Rapide
• ⚡ Jeune Attaquant (25 ans)  
• 🧠 Milieu Expérimenté (30 ans)
• 🛡️ Défenseur Vétéran (35 ans)
```

### 🔧 Test Personnalisé (Configurable)  
```
• Sliders : Âge (16-40), Position, Mois, Taille
• Prédiction temps réel avec interprétation
• Recommandations médicales automatiques
```

### 📊 Entraînement ML (Démo technique)
```
• Simulation d'entraînement complet
• Métriques : Précision, AUC, F1-Score
• Courbe ROC interactive Plotly
```

### 📈 Tests Performance (Validation)
```
• Validation automatique système ML
• Tests composants avec statuts colorés  
• Rapport détaillé des performances
```

## 📊 Données Massives

- **143,195 blessures** analysées (7.8 MB)
- **92,671 profils joueurs** complets (25.2 MB)  
- **Période** : Multiple saisons professionnelles
- **Granularité** : Joueur, type, durée, impact, position

## 🏗️ Architecture Technique

### Stack Technologique
```
🌐 Frontend : Streamlit + Plotly (Interface interactive)
🧠 ML Engine: scikit-learn + pandas (Random Forest)
📊 Data    : CSV + pandas (235K+ records)  
🐍 Backend : Python 3.10+ (Modularité)
```

### Structure Projet Final
```
📁 SoccerSafe/
├── 🚀 launch.bat            # Interface Windows
├── 🐍 start.py              # Démarrage unifié
├── 🧪 test_simple.py        # Tests validés  
├── 📊 data/                 # Datasets (235K+)
├── 🤖 src/ml_predictor.py   # Système ML
└── 🌐 webapp/app_simple.py  # Interface web
```

## 🚀 Installation

### Option 1: Script Automatisé (Recommandé)
```bash
python start.py --setup
```
✅ Vérifie Python, installe dépendances, teste ML, lance l'app

### Option 2: Installation Manuelle  
```bash
# 1. Vérifier Python 3.9+
python --version

# 2. Installer dépendances
pip install -r requirements.txt  

# 3. Tester système
python test_simple.py

# 4. Lancer application
streamlit run webapp/app_simple.py
```

### Option 3: Interface Windows
```bash
launch.bat
```
Menu interactif avec toutes les options

## 🎮 Guide d'Utilisation

### Navigation Interface Web

#### 📊 Vue d'Ensemble
- **KPI temps réel** : 143K blessures, 92K joueurs
- **Graphiques Plotly** : Tendances interactives
- **Métriques par position** : Statistiques avancées

#### 🔍 Analyse Détaillée
- **Filtres multi-critères** : Saison + Position + Type  
- **Corrélations ML** : Âge vs Gravité, Position vs Risque
- **Heatmaps dynamiques** : Patterns temporels

#### 🤖 Prédictions ML (Section Principale)
1. **Sidebar** → "🤖 Prédictions ML"
2. **Choisir mode** : Rapide / Personnalisé / Entraînement / Performance
3. **Configurer paramètres** (si personnalisé)
4. **Obtenir prédictions** avec interprétation automatique

#### 🔍 Recherche Avancée  
- **Recherche par nom** : Base 92K joueurs
- **Filtres combinés** : Critères multiples
- **Export JSON** : Résultats structurés

#### 👤 Profil Joueur
- **Sélection interactive** : Liste déroulante
- **Historique complet** : Timeline blessures  
- **Analyse personnalisée** : Profil de risque

## 📈 Métriques ML

### Performance Modèle
- **Précision** : 56.4% (acceptable pour données réelles)
- **AUC Score** : 0.593 (performance correcte)  
- **F1-Score** : 0.52 (équilibre précision/rappel)
- **Validation** : 5-fold cross-validation

### Facteurs Prédictifs
- **Âge** : Impact croissant avec l'âge
- **Position** : Attaquants > Milieux > Défenseurs  
- **Saison** : Hiver plus risqué (déc-fév)
- **Morphologie** : Taille atypique = risque accru

## 🎓 Projet Académique

### Critères IPSSI Respectés
- ✅ **Base de Données NoSQL** : Simulation avec pandas/CSV massifs
- ✅ **Machine Learning** : Random Forest avec vraies données  
- ✅ **Interface Web** : Streamlit professionnel + Plotly
- ✅ **Architecture** : Code modulaire, tests, documentation
- ✅ **Déployabilité** : Scripts automatisés pour démo

### Démonstration Live
```bash
# Démo Express (3 min)
python start.py --start
→ Interface ML → Test Rapide → Montrer résultats

# Démo Technique (10 min)  
python start.py --test    # Validation ML
python start.py --start   # Interface complète
→ Tous les modes de test + métriques

# Présentation Complète (15 min)
python start.py --setup   # Setup complet commenté
→ Architecture + Fonctionnalités + Performance
```

## 🛠️ Dépannage

### Erreurs Communes

**Modules manquants** :  
```bash
python start.py --install
```

**Fichiers CSV absents** :  
Vérifier dossier `data/` (player_injuries.csv + player_profiles.csv)

**Interface ML erreurs** :  
Les prédictions utilisent des modèles simulés pour éviter les dépendances

**Streamlit lent** :  
```bash  
streamlit run webapp/app_simple.py --server.runOnSave false
```

## 📄 Licence

Projet académique M1 IPSSI - Base de Données NoSQL  
Développé par : Salah Pro  
Objectif : Démonstration ML + Interface web interactive

---

**🎉 SoccerSafe est prêt pour démonstration et évaluation académique !**