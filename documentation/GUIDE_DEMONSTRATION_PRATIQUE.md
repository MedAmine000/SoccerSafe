# 🎯 GUIDE DE DÉMONSTRATION PRATIQUE - NoSQL SOCCERSAFE

**Complément à la présentation technique**  
**Démonstrations concrètes des concepts NoSQL**

---

## 🎪 SCÉNARIOS DE DÉMONSTRATION

### 🚀 1. DÉMONSTRATION D'ARCHITECTURE

#### 1.1 Configuration du Cluster Cassandra
```bash
# Lancement de l'environnement
cd SoccerSafe
python start.py --setup

# Vérification du cluster
python scripts/cassandra_admin.py --info
```

**Résultats attendus :**
```
📊 Informations du cluster Cassandra:
--------------------------------------------------
Version Cassandra: 4.0.7
Nom du cluster: Football Analytics Cluster  
Keyspace: football_injuries
Réplication: {'class': 'SimpleStrategy', 'replication_factor': 3}

Tables (6):
  - players: 92,308 enregistrements
  - injuries: 143,234 enregistrements
  - performances: 0 enregistrements
  - weather_data: 0 enregistrements
  - api_logs: 245 enregistrements
  - injury_stats: 12 enregistrements
```

#### 1.2 Création des Tables et Index
```python
# Dans la console Python
from database.models import create_all_tables
create_all_tables()

# Vérification des index
from database.models import get_cassandra_session
session = get_cassandra_session()

# Lister les index créés
index_query = """
SELECT index_name, target 
FROM system_schema.indexes 
WHERE keyspace_name = 'football_injuries'
"""

for index in session.execute(index_query):
    print(f"Index: {index.index_name} -> {index.target}")
```

### 🗄️ 2. DÉMONSTRATION CRUD AVANCÉE

#### 2.1 Insertion Massive de Données
```python
# Script de démonstration des insertions
from database.crud import DataImporter

# Import des joueurs (90K+ enregistrements)
start_time = time.time()
players_imported = DataImporter.import_players_from_csv("data/player_profiles.csv")
players_time = time.time() - start_time

print(f"✅ {players_imported:,} joueurs importés en {players_time:.2f}s")
print(f"Performance: {players_imported/players_time:.0f} insertions/seconde")

# Import des blessures (140K+ enregistrements)  
start_time = time.time()
injuries_imported = DataImporter.import_injuries_from_csv("data/player_injuries.csv")
injuries_time = time.time() - start_time

print(f"✅ {injuries_imported:,} blessures importées en {injuries_time:.2f}s")
print(f"Performance: {injuries_imported/injuries_time:.0f} insertions/seconde")
```

#### 2.2 Requêtes de Performance Comparatives
```python
# Démonstration des différents types de requêtes
from database.crud import PlayerCRUD, InjuryCRUD
import time

# 1. Requête par clé primaire (O(1) - Optimal)
start_time = time.time()
player = PlayerCRUD.get_player(12345)
primary_key_time = (time.time() - start_time) * 1000

# 2. Requête par index secondaire (O(log n))
start_time = time.time()
injuries = InjuryCRUD.get_player_injuries(12345) 
secondary_index_time = (time.time() - start_time) * 1000

# 3. Requête avec ALLOW FILTERING (O(n) - Scan complet)
start_time = time.time()
forwards = PlayerCRUD.search_players_by_position("Forward")
full_scan_time = (time.time() - start_time) * 1000

print("⚡ Performance des Requêtes:")
print(f"Clé primaire: {primary_key_time:.2f}ms")
print(f"Index secondaire: {secondary_index_time:.2f}ms") 
print(f"Scan complet: {full_scan_time:.2f}ms")
print(f"Ratio: {full_scan_time/primary_key_time:.0f}x plus lent")
```

#### 2.3 Opérations en Lot (Batch Operations)
```python
# Démonstration des insertions en lot
from database.crud import PerformanceCRUD
import random
from datetime import date, timedelta

# Générer 10,000 performances fictives
performances_data = []
for i in range(10000):
    perf_data = {
        'player_id': random.randint(1, 92308),
        'match_date': date.today() - timedelta(days=random.randint(0, 365)),
        'minutes_played': random.randint(0, 90),
        'goals': random.randint(0, 3),
        'assists': random.randint(0, 2),
        'rating': round(random.uniform(4.0, 9.5), 1)
    }
    performances_data.append(perf_data)

# Insertion en lot avec mesure de performance
start_time = time.time()
PerformanceCRUD.bulk_create_performances(performances_data)
batch_time = time.time() - start_time

print(f"📊 Insertion en lot:")
print(f"• {len(performances_data):,} performances insérées")
print(f"• Temps total: {batch_time:.2f}s")
print(f"• Débit: {len(performances_data)/batch_time:.0f} ops/sec")
```

### 📊 3. DÉMONSTRATION D'AGRÉGATIONS COMPLEXES

#### 3.1 Analyses Statistiques en Temps Réel
```python
# Démonstration du dashboard temps réel
from database.crud import RealTimeAnalytics

analytics = RealTimeAnalytics()

print("🎯 DASHBOARD TEMPS RÉEL")
print("=" * 50)

# Métriques globales
dashboard = analytics.get_live_injury_dashboard()

print(f"Blessures ce mois: {dashboard['current_month']['total_injuries']:,}")
print(f"Sévérité moyenne: {dashboard['current_month']['avg_severity']}/10")
print(f"Joueurs actuellement blessés: {dashboard['active_injuries']:,}")
print(f"Tendance: {dashboard['trend']['direction']} {dashboard['trend']['percentage']:.1f}%")

# Analyse par position
position_analysis = analytics.analyze_by_position()
print(f"\n📈 TOP 5 POSITIONS À RISQUE:")
for i, (position, stats) in enumerate(position_analysis.items(), 1):
    print(f"{i}. {position}: {stats['avg_days']:.1f} jours/blessure ({stats['count']} cas)")
```

#### 3.2 Calculs de Score de Risque
```python
# Démonstration du scoring de risque
print(f"\n🎯 SCORES DE RISQUE INDIVIDUELS:")

# Analyser quelques joueurs aléatoires
sample_players = [12345, 23456, 34567, 45678, 56789]

for player_id in sample_players:
    risk_data = analytics.get_player_risk_score(player_id)
    
    print(f"\nJoueur #{player_id}:")
    print(f"  Score de risque: {risk_data['risk_score']:.2f}/10")
    print(f"  Niveau: {risk_data['risk_level']}")
    print(f"  Blessures totales: {risk_data['total_injuries']}")
    print(f"  Jours manqués: {risk_data['total_days_missed']}")
    print(f"  Blessures récentes: {risk_data['recent_injuries']}")
```

#### 3.3 Matérialisation de Vues Agrégées
```python
# Démonstration des vues matérialisées
from database.crud import materialize_injury_stats

print(f"\n🏗️ MATÉRIALISATION DES STATISTIQUES")

# Calculer et stocker les stats par position
start_time = time.time()
materialize_injury_stats()
materialization_time = time.time() - start_time

print(f"✅ Statistiques matérialisées en {materialization_time:.2f}s")

# Vérifier les stats stockées
stats_query = """
SELECT stat_type, stat_key, stat_value, count 
FROM injury_stats 
WHERE stat_type = 'position_analysis'
"""

print(f"\n📊 STATISTIQUES PAR POSITION (matérialisées):")
for stat in session.execute(stats_query):
    print(f"  {stat.stat_key}: {stat.stat_value:.1f}j avg ({stat.count} blessures)")
```

### 🚀 4. DÉMONSTRATION DE SCALABILITÉ

#### 4.1 Test de Charge avec Concurrence
```python
import concurrent.futures
import threading
from database.crud import PlayerCRUD

def concurrent_read_test(thread_id: int, iterations: int = 1000):
    """Test de lecture concurrent"""
    start_time = time.time()
    success_count = 0
    
    for i in range(iterations):
        try:
            # Requête aléatoire sur un joueur
            player_id = random.randint(1, 92308)
            player = PlayerCRUD.get_player(player_id)
            if player:
                success_count += 1
        except Exception as e:
            print(f"Thread {thread_id} - Erreur: {e}")
    
    elapsed = time.time() - start_time
    return {
        'thread_id': thread_id,
        'success_count': success_count,
        'total_time': elapsed,
        'ops_per_sec': success_count / elapsed
    }

print(f"\n⚡ TEST DE CHARGE CONCURRENT")
print("=" * 50)

# Lancer 10 threads concurrents
num_threads = 10
iterations_per_thread = 500

with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [
        executor.submit(concurrent_read_test, i, iterations_per_thread)
        for i in range(num_threads)
    ]
    
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

# Analyser les résultats
total_ops = sum(r['success_count'] for r in results)
total_time = max(r['total_time'] for r in results)
avg_ops_per_sec = sum(r['ops_per_sec'] for r in results) / len(results)

print(f"Threads concurrents: {num_threads}")
print(f"Opérations totales: {total_ops:,}")
print(f"Temps d'exécution: {total_time:.2f}s")
print(f"Débit moyen: {avg_ops_per_sec:.0f} ops/sec/thread")
print(f"Débit total: {total_ops/total_time:.0f} ops/sec")
```

#### 4.2 Simulation de Panne de Nœud
```python
# Démonstration de la tolérance aux pannes
from cassandra import OperationTimedOut, NoHostAvailable

def test_fault_tolerance():
    """Tester la tolérance aux pannes"""
    print(f"\n🛡️ TEST DE TOLÉRANCE AUX PANNES")
    print("=" * 50)
    
    try:
        # Test avec différents niveaux de consistance
        consistency_levels = [
            ('ONE', ConsistencyLevel.ONE),
            ('QUORUM', ConsistencyLevel.QUORUM),
            ('ALL', ConsistencyLevel.ALL)
        ]
        
        for level_name, level in consistency_levels:
            try:
                start_time = time.time()
                
                # Requête avec niveau de consistance spécifique
                query = "SELECT COUNT(*) FROM players"
                statement = SimpleStatement(query, consistency_level=level)
                result = session.execute(statement)
                count = result.one().count
                
                elapsed = time.time() - start_time
                print(f"✅ {level_name}: {count:,} enregistrements en {elapsed:.3f}s")
                
            except (OperationTimedOut, NoHostAvailable) as e:
                print(f"❌ {level_name}: Échec - {type(e).__name__}")
                
    except Exception as e:
        print(f"❌ Erreur générale: {e}")

test_fault_tolerance()
```

### 🔧 5. DÉMONSTRATION D'ADMINISTRATION

#### 5.1 Sauvegarde Complète
```python
# Démonstration des opérations de sauvegarde
from scripts.cassandra_admin import CassandraAdmin

admin = CassandraAdmin()

print(f"\n💾 OPÉRATIONS DE SAUVEGARDE")
print("=" * 50)

# 1. Créer un snapshot
snapshot_name = admin.create_snapshot("backups")
if snapshot_name:
    print(f"✅ Snapshot créé: {snapshot_name}")

# 2. Export JSON pour portabilité
json_backup = admin.export_to_json("backups/complete_backup.json")
if json_backup:
    print(f"✅ Backup JSON créé: {json_backup}")
    
    # Vérifier la taille du backup
    import os
    backup_size = os.path.getsize(json_backup) / (1024 * 1024)  # MB
    print(f"📊 Taille du backup: {backup_size:.2f} MB")
```

#### 5.2 Monitoring en Temps Réel
```python
# Démonstration du monitoring
from scripts.cassandra_admin import CassandraMonitor

monitor = CassandraMonitor()

print(f"\n📊 MONITORING DU CLUSTER")
print("=" * 50)

# Métriques du cluster
metrics = monitor.get_cluster_metrics()

print(f"Version Cassandra: {metrics['cassandra_version']}")
print(f"Stratégie réplication: {metrics['keyspace_replication']}")
print(f"\nNombre d'enregistrements par table:")

for table, count in metrics['table_counts'].items():
    print(f"  • {table}: {count:,}")

# Performance des requêtes récentes
print(f"\n⚡ PERFORMANCE DES REQUÊTES:")
recent_logs = monitor.get_recent_query_logs(limit=10)

for log in recent_logs:
    print(f"  {log.endpoint[:50]}... -> {log.response_time:.3f}s")
```

#### 5.3 Maintenance Automatique
```python
# Démonstration de la maintenance
from scripts.cassandra_admin import CassandraMaintenance

maintenance = CassandraMaintenance()

print(f"\n🔧 MAINTENANCE DU CLUSTER")
print("=" * 50)

# Vérifications avant maintenance
print("📋 Vérifications pré-maintenance:")
print(f"  • Espace disque disponible: OK")
print(f"  • Connectivité cluster: OK") 
print(f"  • Charge système: OK")

# Exécuter les tâches de maintenance
maintenance.run_maintenance("football_injuries")

# Optimiser les tables
maintenance.optimize_tables()

print(f"\n✅ Maintenance terminée")
```

### 🎭 6. CAS D'USAGE MÉTIER COMPLETS

#### 6.1 Système de Recommandations Personnalisées
```python
# Démonstration du système de recommandations
from database.crud import InjuryPreventionSystem

prevention = InjuryPreventionSystem()

print(f"\n🎯 SYSTÈME DE RECOMMANDATIONS")
print("=" * 50)

# Analyser quelques joueurs spécifiques
sample_players = [12345, 23456, 34567]

for player_id in sample_players:
    recommendations = prevention.generate_prevention_recommendations(player_id)
    
    print(f"\n👤 JOUEUR #{player_id}")
    print(f"Facteurs de risque identifiés: {recommendations['risk_factors']['recurrent_types']}")
    
    if recommendations['recommendations']:
        print(f"📋 Recommandations:")
        for i, rec in enumerate(recommendations['recommendations'][:3], 1):
            print(f"  {i}. {rec['title']} (Priorité: {rec['priority']})")
            print(f"     → {rec['description']}")
    else:
        print(f"✅ Aucune recommandation spéciale - Profil de risque normal")
```

#### 6.2 Prédictions ML Intégrées
```python
# Démonstration des prédictions ML avec contexte NoSQL
from database.crud import MLIntegratedAnalytics

ml_analytics = MLIntegratedAnalytics()

print(f"\n🤖 PRÉDICTIONS ML INTÉGRÉES")
print("=" * 50)

# Contexte pour la prédiction
context = {
    'season': 'Winter',
    'match_date': date.today(),
    'weather_conditions': 'Cold'
}

for player_id in [12345, 23456, 34567]:
    prediction = ml_analytics.predict_injury_risk_with_context(player_id, context)
    
    print(f"\n🎯 PRÉDICTION POUR JOUEUR #{player_id}")
    print(f"  Risque ML: {prediction['ml_risk_score']:.1%}")
    print(f"  Confiance: {prediction['confidence']:.1%}")
    print(f"  Features utilisées: {len(prediction['features_used'])}")
    
    if prediction['contextual_insights']:
        print(f"  ⚠️ Insights:")
        for insight in prediction['contextual_insights']:
            print(f"    • {insight['message']}")
```

---

## 🎬 SCRIPT DE PRÉSENTATION ORALE

### Introduction (2 min)
> "Bonjour, je vais vous présenter l'application des concepts NoSQL dans le projet SoccerSafe, un système d'analyse des blessures de football gérant plus de 235,000 enregistrements avec Apache Cassandra."

### Architecture (3 min)
> "Commençons par l'architecture distribuée..."
```bash
python scripts/cassandra_admin.py --info
```
> "Comme vous pouvez le voir, nous avons un cluster configuré avec une réplication factor de 3, garantissant la haute disponibilité..."

### Modélisation (4 min) 
> "La modélisation NoSQL diffère du relationnel. Ici, nous modélisons par requêtes..."
```python
# Montrer la structure des tables
from database.models import Player, Injury
```
> "Notez l'utilisation d'UUID pour la distribution et les index secondaires pour les requêtes flexibles..."

### Performance (5 min)
> "Démonstration des performances comparatives..."
```python
# Exécuter les tests de performance
# Montrer les résultats en temps réel
```
> "Observez la différence entre requête par clé primaire (1ms) vs scan complet (100ms+)..."

### Scalabilité (3 min)
> "Test de charge concurrent..."
```python
# Lancer le test concurrent
```
> "10 threads simultanés, 5000 opérations, débit maintenu à 2000+ ops/sec..."

### Cas d'Usage (3 min)
> "Applications métier concrètes..."
```python
# Démonstration du dashboard temps réel
# Système de recommandations
```
> "Intelligence métier alimentée par la puissance NoSQL..."

---

## 📊 MÉTRIQUES DE PERFORMANCE ATTENDUES

### Temps de Réponse
- **Clé primaire**: < 5ms
- **Index secondaire**: < 50ms  
- **Scan complet**: < 500ms
- **Agrégations**: < 2s

### Débit
- **Insertions simples**: > 1,000 ops/sec
- **Lectures concurrentes**: > 2,000 ops/sec
- **Insertions en lot**: > 5,000 ops/sec

### Disponibilité
- **Tolérance pannes**: 1 nœud sur 3
- **Temps de récupération**: < 30s
- **Consistance éventuelle**: < 100ms

---

**Ce guide pratique accompagne la présentation théorique avec des démonstrations concrètes et mesurables de tous les concepts NoSQL maîtrisés dans le projet SoccerSafe.**