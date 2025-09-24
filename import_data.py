#!/usr/bin/env python3
"""
Script d'import des données CSV vers Cassandra
Import des données existantes de joueurs et blessures
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Ajouter le path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_cassandra_session, create_all_tables
from database.crud import DataImporter

def main():
    """Point d'entrée principal"""
    print("🚀 Import des données CSV vers Cassandra")
    print("=" * 50)
    
    # Vérifier que les fichiers CSV existent
    player_file = "player_profiles.csv"
    injury_file = "player_injuries.csv"
    
    if not os.path.exists(player_file):
        print(f"❌ Fichier non trouvé: {player_file}")
        return
        
    if not os.path.exists(injury_file):
        print(f"❌ Fichier non trouvé: {injury_file}")
        return
    
    # Vérifier la connexion Cassandra
    try:
        session = get_cassandra_session()
        print("✅ Connexion Cassandra établie")
    except Exception as e:
        print(f"❌ Erreur de connexion Cassandra: {e}")
        print("Assurez-vous que Cassandra est démarré et configuré")
        return
    
    # Créer les tables si nécessaire
    print("\n📋 Création des tables...")
    try:
        create_all_tables()
        print("✅ Tables créées/vérifiées")
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        return
    
    # Afficher les informations sur les fichiers
    print(f"\n📊 Analyse des fichiers...")
    
    try:
        players_df = pd.read_csv(player_file)
        injuries_df = pd.read_csv(injury_file)
        
        print(f"  Joueurs: {len(players_df):,} entrées")
        print(f"  Blessures: {len(injuries_df):,} entrées")
        
    except Exception as e:
        print(f"❌ Erreur lors de la lecture des CSV: {e}")
        return
    
    # Demander confirmation
    response = input(f"\n⚠️  Voulez-vous importer ces données dans Cassandra? (y/N): ")
    if response.lower() != 'y':
        print("Import annulé")
        return
    
    # Import des données
    print(f"\n🔄 Import en cours...")
    start_time = datetime.now()
    
    try:
        # Import des joueurs
        print("\n1️⃣ Import des joueurs...")
        players_count = DataImporter.import_players_from_csv(player_file)
        
        # Import des blessures
        print("\n2️⃣ Import des blessures...")
        injuries_count = DataImporter.import_injuries_from_csv(injury_file)
        
        # Calcul du temps total
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Résumé final
        print(f"\n🎉 Import terminé avec succès!")
        print("=" * 40)
        print(f"✅ Joueurs importés: {players_count:,}")
        print(f"✅ Blessures importées: {injuries_count:,}")
        print(f"⏱️  Durée totale: {duration}")
        print(f"📊 Total: {players_count + injuries_count:,} entrées")
        
        # Vérification rapide
        print(f"\n🔍 Vérification des données...")
        
        # Test de quelques requêtes
        from database.crud import PlayerCRUD, InjuryCRUD
        
        sample_players = PlayerCRUD.get_all_players(limit=5)
        sample_injuries = InjuryCRUD.get_all_injuries(limit=5)
        
        print(f"✅ Échantillon joueurs: {len(sample_players)} trouvés")
        print(f"✅ Échantillon blessures: {len(sample_injuries)} trouvés")
        
        print(f"\n🚀 Prochaines étapes:")
        print("1. Démarrer l'application web: streamlit run webapp/app.py")
        print("2. Vérifier les données: python scripts/cassandra_admin.py --info")
        print("3. Créer des sauvegardes: python scripts/cassandra_admin.py --backup")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'import: {e}")
        print("Vérifiez les logs pour plus de détails")
        return
    
    finally:
        # Fermer la session
        try:
            session.shutdown()
        except:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Import interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)