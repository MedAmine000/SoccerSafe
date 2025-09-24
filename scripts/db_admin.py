"""
Scripts d'administration de Cassandra
Backup, restauration, optimisation, monitoring
"""
import os
import subprocess
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import json
import sys

# Ajouter le path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_cassandra_session, close_cassandra_connection

load_dotenv()

class CassandraAdmin:
    def __init__(self):
        self.cassandra_config = {
            'hosts': os.getenv('CASSANDRA_HOSTS', 'localhost').split(','),
            'port': int(os.getenv('CASSANDRA_PORT', '9042')),
            'keyspace': os.getenv('CASSANDRA_KEYSPACE', 'football_injuries'),
            'username': os.getenv('CASSANDRA_USERNAME'),
            'password': os.getenv('CASSANDRA_PASSWORD')
        }
    
    def create_dump(self, output_dir="backups"):
        """Créer un dump de la base de données"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dump_file = f"{output_dir}/football_injuries_dump_{timestamp}.sql"
        
        # Commande pg_dump
        cmd = [
            "pg_dump",
            f"--host={self.db_config['host']}",
            f"--port={self.db_config['port']}",
            f"--username={self.db_config['user']}",
            f"--dbname={self.db_config['database']}",
            "--verbose",
            "--clean",
            "--no-owner",
            "--no-privileges",
            f"--file={dump_file}"
        ]
        
        try:
            # Définir le mot de passe via une variable d'environnement
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            subprocess.run(cmd, env=env, check=True)
            print(f"✅ Dump créé avec succès: {dump_file}")
            return dump_file
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de la création du dump: {e}")
            return None
    
    def restore_dump(self, dump_file):
        """Restaurer la base de données depuis un dump"""
        cmd = [
            "psql",
            f"--host={self.db_config['host']}",
            f"--port={self.db_config['port']}",
            f"--username={self.db_config['user']}",
            f"--dbname={self.db_config['database']}",
            f"--file={dump_file}"
        ]
        
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']
            
            subprocess.run(cmd, env=env, check=True)
            print(f"✅ Base de données restaurée depuis: {dump_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de la restauration: {e}")
            return False
    
    def optimize_database(self):
        """Optimiser les performances de la base de données"""
        optimizations = [
            # Créer des index pour améliorer les performances
            "CREATE INDEX IF NOT EXISTS idx_injuries_player_date ON injuries(player_id, from_date);",
            "CREATE INDEX IF NOT EXISTS idx_injuries_type ON injuries(injury_reason);",
            "CREATE INDEX IF NOT EXISTS idx_injuries_season ON injuries(season_name);",
            "CREATE INDEX IF NOT EXISTS idx_players_position ON players(main_position);",
            "CREATE INDEX IF NOT EXISTS idx_players_club ON players(current_club_name);",
            "CREATE INDEX IF NOT EXISTS idx_performances_player_date ON performances(player_id, match_date);",
            "CREATE INDEX IF NOT EXISTS idx_weather_date ON weather_data(match_date);",
            
            # Analyser les tables pour mettre à jour les statistiques
            "ANALYZE players;",
            "ANALYZE injuries;",
            "ANALYZE performances;",
            "ANALYZE weather_data;",
            
            # Nettoyer les données obsolètes
            "VACUUM ANALYZE;"
        ]
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            for query in optimizations:
                print(f"Exécution: {query}")
                cursor.execute(query)
                conn.commit()
            
            cursor.close()
            conn.close()
            print("✅ Optimisation de la base de données terminée")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'optimisation: {e}")
    
    def setup_security(self):
        """Configurer la sécurité de la base de données"""
        security_queries = [
            # Créer un utilisateur en lecture seule pour les rapports
            "CREATE USER IF NOT EXISTS report_user WITH PASSWORD 'report_password123';",
            
            # Accorder les permissions de lecture seulement
            "GRANT CONNECT ON DATABASE football_injuries TO report_user;",
            "GRANT USAGE ON SCHEMA public TO report_user;",
            "GRANT SELECT ON ALL TABLES IN SCHEMA public TO report_user;",
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO report_user;",
            
            # Créer un rôle pour l'application web
            "CREATE ROLE IF NOT EXISTS webapp_role;",
            "GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO webapp_role;",
            "GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO webapp_role;",
        ]
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            for query in security_queries:
                try:
                    cursor.execute(query)
                    conn.commit()
                    print(f"✅ {query}")
                except Exception as e:
                    print(f"⚠️  Avertissement: {e}")
                    continue
            
            cursor.close()
            conn.close()
            print("✅ Configuration de sécurité terminée")
            
        except Exception as e:
            print(f"❌ Erreur lors de la configuration de sécurité: {e}")
    
    def import_large_csv(self, csv_file, table_name, batch_size=10000):
        """Importer un fichier CSV volumineux par lots"""
        print(f"📥 Import de {csv_file} vers {table_name}")
        
        try:
            # Lire le CSV par chunks
            chunk_reader = pd.read_csv(csv_file, chunksize=batch_size)
            total_imported = 0
            
            conn = psycopg2.connect(**self.db_config)
            
            for chunk_num, chunk in enumerate(chunk_reader):
                print(f"Traitement du lot {chunk_num + 1} ({len(chunk)} lignes)")
                
                # Utiliser pd.to_sql pour l'insertion rapide
                from sqlalchemy import create_engine
                engine = create_engine(f"postgresql://{self.db_config['user']}:{self.db_config['password']}@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
                
                chunk.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
                total_imported += len(chunk)
                
                print(f"✅ {total_imported} lignes importées")
            
            conn.close()
            print(f"🎉 Import terminé: {total_imported} lignes au total")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'import: {e}")
    
    def get_database_stats(self):
        """Obtenir des statistiques de la base de données"""
        stats_queries = {
            'Taille de la base': "SELECT pg_size_pretty(pg_database_size('football_injuries'));",
            'Nombre de joueurs': "SELECT COUNT(*) FROM players;",
            'Nombre de blessures': "SELECT COUNT(*) FROM injuries;",
            'Nombre de performances': "SELECT COUNT(*) FROM performances;",
            'Table la plus volumineuse': """
                SELECT schemaname, tablename, 
                       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC 
                LIMIT 1;
            """
        }
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            print("📊 Statistiques de la base de données:")
            print("-" * 50)
            
            for stat_name, query in stats_queries.items():
                cursor.execute(query)
                result = cursor.fetchone()
                print(f"{stat_name}: {result[0] if result else 'N/A'}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des stats: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Administration de la base de données")
    parser.add_argument("--dump", action="store_true", help="Créer un dump")
    parser.add_argument("--restore", type=str, help="Restaurer depuis un dump")
    parser.add_argument("--optimize", action="store_true", help="Optimiser la base")
    parser.add_argument("--security", action="store_true", help="Configurer la sécurité")
    parser.add_argument("--stats", action="store_true", help="Afficher les statistiques")
    parser.add_argument("--import-csv", nargs=2, metavar=('CSV_FILE', 'TABLE_NAME'), 
                       help="Importer un CSV volumineux")
    
    args = parser.parse_args()
    admin = DatabaseAdmin()
    
    if args.dump:
        admin.create_dump()
    elif args.restore:
        admin.restore_dump(args.restore)
    elif args.optimize:
        admin.optimize_database()
    elif args.security:
        admin.setup_security()
    elif args.stats:
        admin.get_database_stats()
    elif args.import_csv:
        admin.import_large_csv(args.import_csv[0], args.import_csv[1])
    else:
        print("Utilisez --help pour voir les options disponibles")