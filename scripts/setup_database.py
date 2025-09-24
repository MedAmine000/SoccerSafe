"""
Script de configuration initiale de Cassandra
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import create_all_tables, get_cassandra_session, close_cassandra_connection
from database.crud import DataImporter
import argparse

def setup_database():
    """Configuration initiale de Cassandra"""
    print("🚀 Configuration de Cassandra...")
    
    try:
        # Créer les tables et indexes
        create_all_tables()
        print("✅ Tables Cassandra créées avec succès")
        
        # Importer les données CSV existantes
        print("📊 Import des données CSV...")
        
        # Importer les joueurs
        players_imported = DataImporter.import_players_from_csv("data/player_profiles.csv")
        print(f"✅ {players_imported} joueurs importés")
        
        # Importer les blessures  
        injuries_imported = DataImporter.import_injuries_from_csv("data/player_injuries.csv")
        print(f"✅ {injuries_imported} blessures importées")
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        close_cassandra_connection()
    
    print("🎉 Configuration Cassandra terminée!")

def reset_database():
    """Réinitialiser complètement la base de données Cassandra"""
    session = get_cassandra_session()
    
    print("⚠️  Suppression de toutes les données...")
    
    # Supprimer toutes les tables
    tables = ['players', 'injuries', 'performances', 'weather_data', 'api_logs', 'injury_stats']
    
    for table in tables:
        try:
            session.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"  ❌ Table {table} supprimée")
        except Exception as e:
            print(f"  ⚠️  Erreur suppression {table}: {e}")
    
    print("✅ Base de données réinitialisée")
    close_cassandra_connection()
    
    # Reconfigurer
    setup_database()

def check_cassandra_connection():
    """Vérifier la connexion à Cassandra"""
    print("🔍 Vérification de la connexion Cassandra...")
    
    try:
        session = get_cassandra_session()
        
        # Test simple
        result = session.execute("SELECT release_version FROM system.local")
        version = result.one().release_version
        print(f"✅ Connexion réussie - Cassandra {version}")
        
        # Vérifier le keyspace
        keyspace_query = "SELECT keyspace_name FROM system_schema.keyspaces WHERE keyspace_name = 'football_injuries'"
        keyspace_result = session.execute(keyspace_query)
        
        if keyspace_result.one():
            print("✅ Keyspace 'football_injuries' trouvé")
        else:
            print("⚠️  Keyspace 'football_injuries' non trouvé")
        
        close_cassandra_connection()
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion Cassandra: {e}")
        print("💡 Vérifiez que Cassandra est démarré et configuré correctement")
        return False

def show_database_info():
    """Afficher les informations de la base de données"""
    try:
        session = get_cassandra_session()
        
        print("📊 Informations Cassandra:")
        print("-" * 50)
        
        # Version Cassandra
        result = session.execute("SELECT release_version FROM system.local")
        version = result.one().release_version
        print(f"Version: {version}")
        
        # Keyspace info
        keyspace_query = """
        SELECT keyspace_name, replication 
        FROM system_schema.keyspaces 
        WHERE keyspace_name = 'football_injuries'
        """
        keyspace_result = session.execute(keyspace_query)
        keyspace_info = keyspace_result.one()
        
        if keyspace_info:
            print(f"Keyspace: {keyspace_info.keyspace_name}")
            print(f"Réplication: {keyspace_info.replication}")
        
        # Tables
        tables_query = """
        SELECT table_name 
        FROM system_schema.tables 
        WHERE keyspace_name = 'football_injuries'
        """
        tables_result = session.execute(tables_query)
        tables = [row.table_name for row in tables_result]
        
        print(f"Tables: {', '.join(tables)}")
        
        # Compter les données
        for table in tables:
            try:
                count_query = f"SELECT COUNT(*) FROM {table}"
                count_result = session.execute(count_query)
                count = count_result.one().count
                print(f"  - {table}: {count:,} enregistrements")
            except Exception as e:
                print(f"  - {table}: Erreur de comptage ({e})")
        
        close_cassandra_connection()
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération d'infos: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration de Cassandra")
    parser.add_argument("--reset", action="store_true", help="Réinitialiser la base de données")
    parser.add_argument("--check", action="store_true", help="Vérifier la connexion")
    parser.add_argument("--info", action="store_true", help="Afficher les informations")
    
    args = parser.parse_args()
    
    if args.check:
        check_cassandra_connection()
    elif args.info:
        show_database_info()
    elif args.reset:
        reset_database()
    else:
        setup_database()