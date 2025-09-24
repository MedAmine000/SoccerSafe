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
    
    def create_snapshot(self, output_dir="backups"):
        """Créer un snapshot de Cassandra"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"football_injuries_snapshot_{timestamp}"
        
        try:
            # Utiliser nodetool pour créer un snapshot
            cmd = [
                "nodetool",
                "snapshot",
                "-t", snapshot_name,
                self.cassandra_config['keyspace']
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Snapshot créé avec succès: {snapshot_name}")
                
                # Exporter aussi en JSON pour faciliter la restauration
                self.export_to_json(f"{output_dir}/{snapshot_name}.json")
                return snapshot_name
            else:
                print(f"❌ Erreur lors de la création du snapshot: {result.stderr}")
                return None
                
        except FileNotFoundError:
            print("❌ nodetool non trouvé. Utilisation de l'export JSON...")
            json_file = self.export_to_json(f"{output_dir}/backup_{timestamp}.json")
            return json_file
        except Exception as e:
            print(f"❌ Erreur lors de la création du snapshot: {e}")
            return None
    
    def export_to_json(self, output_file):
        """Exporter toutes les données en JSON"""
        session = get_cassandra_session()
        backup_data = {}
        
        # Tables à sauvegarder
        tables = ['players', 'injuries', 'performances', 'weather_data', 'api_logs', 'injury_stats']
        
        try:
            for table in tables:
                print(f"📊 Export de la table {table}...")
                
                # Récupérer toutes les données de la table
                query = f"SELECT * FROM {table}"
                result = session.execute(query)
                
                # Convertir en liste de dictionnaires
                table_data = []
                for row in result:
                    row_dict = {}
                    for column, value in row._asdict().items():
                        # Convertir les types spéciaux en chaînes
                        if isinstance(value, (datetime, )):
                            row_dict[column] = value.isoformat()
                        elif hasattr(value, '__str__'):
                            row_dict[column] = str(value)
                        else:
                            row_dict[column] = value
                    table_data.append(row_dict)
                
                backup_data[table] = table_data
                print(f"  ✅ {len(table_data)} enregistrements exportés")
            
            # Sauvegarder en JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Backup JSON créé: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Erreur lors de l'export JSON: {e}")
            return None
        finally:
            close_cassandra_connection()
    
    def restore_from_json(self, backup_file):
        """Restaurer depuis un fichier JSON"""
        if not os.path.exists(backup_file):
            print(f"❌ Fichier de backup non trouvé: {backup_file}")
            return False
        
        session = get_cassandra_session()
        
        try:
            # Charger les données
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            print(f"📥 Restauration depuis {backup_file}...")
            
            # Restaurer chaque table
            for table_name, table_data in backup_data.items():
                print(f"📊 Restauration de {table_name}...")
                
                # Préparer les statements d'insertion selon la table
                if table_name == 'players':
                    insert_query = """
                    INSERT INTO players (player_id, player_name, date_of_birth, place_of_birth,
                                       country_of_birth, height, position, main_position, foot,
                                       current_club_name, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                elif table_name == 'injuries':
                    insert_query = """
                    INSERT INTO injuries (injury_id, player_id, season_name, injury_reason,
                                        from_date, end_date, days_missed, games_missed,
                                        severity_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                # Ajouter d'autres tables au besoin...
                
                # Insérer les données
                for row in table_data:
                    try:
                        if table_name == 'players':
                            values = (
                                int(row.get('player_id')),
                                row.get('player_name'),
                                datetime.fromisoformat(row.get('date_of_birth')) if row.get('date_of_birth') else None,
                                row.get('place_of_birth'),
                                row.get('country_of_birth'),
                                float(row.get('height')) if row.get('height') else None,
                                row.get('position'),
                                row.get('main_position'),
                                row.get('foot'),
                                row.get('current_club_name'),
                                datetime.fromisoformat(row.get('created_at')) if row.get('created_at') else datetime.now(),
                                datetime.fromisoformat(row.get('updated_at')) if row.get('updated_at') else datetime.now()
                            )
                            session.execute(insert_query, values)
                    except Exception as e:
                        print(f"⚠️  Erreur insertion {table_name}: {e}")
                        continue
                
                print(f"  ✅ {len(table_data)} enregistrements restaurés")
            
            print("✅ Restauration terminée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la restauration: {e}")
            return False
        finally:
            close_cassandra_connection()
    
    def optimize_keyspace(self):
        """Optimiser le keyspace Cassandra"""
        print("🔧 Optimisation du keyspace Cassandra...")
        
        try:
            # Utiliser nodetool pour la maintenance
            maintenance_commands = [
                ["nodetool", "repair", self.cassandra_config['keyspace']],
                ["nodetool", "compact", self.cassandra_config['keyspace']],
                ["nodetool", "cleanup", self.cassandra_config['keyspace']]
            ]
            
            for cmd in maintenance_commands:
                print(f"🔧 Exécution: {' '.join(cmd)}")
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                    if result.returncode == 0:
                        print(f"  ✅ {cmd[1]} terminé")
                    else:
                        print(f"  ⚠️  {cmd[1]} - avertissement: {result.stderr}")
                except subprocess.TimeoutExpired:
                    print(f"  ⏰ {cmd[1]} - timeout (mais peut continuer en arrière-plan)")
                except FileNotFoundError:
                    print(f"  ❌ nodetool non disponible pour {cmd[1]}")
            
            print("✅ Optimisation terminée")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'optimisation: {e}")
    
    def get_cluster_info(self):
        """Obtenir des informations sur le cluster"""
        session = get_cassandra_session()
        
        try:
            print("📊 Informations du cluster Cassandra:")
            print("-" * 50)
            
            # Version Cassandra
            result = session.execute("SELECT release_version FROM system.local")
            version = result.one().release_version
            print(f"Version Cassandra: {version}")
            
            # Informations sur le cluster
            cluster_result = session.execute("SELECT cluster_name FROM system.local")
            cluster_name = cluster_result.one().cluster_name
            print(f"Nom du cluster: {cluster_name}")
            
            # Keyspace info
            keyspace_query = """
            SELECT keyspace_name, replication 
            FROM system_schema.keyspaces 
            WHERE keyspace_name = ?
            """
            keyspace_result = session.execute(keyspace_query, (self.cassandra_config['keyspace'],))
            keyspace_info = keyspace_result.one()
            
            if keyspace_info:
                print(f"Keyspace: {keyspace_info.keyspace_name}")
                print(f"Réplication: {keyspace_info.replication}")
            
            # Tables et statistiques
            tables_query = """
            SELECT table_name 
            FROM system_schema.tables 
            WHERE keyspace_name = ?
            """
            tables_result = session.execute(tables_query, (self.cassandra_config['keyspace'],))
            tables = [row.table_name for row in tables_result]
            
            print(f"\nTables ({len(tables)}):")
            for table in tables:
                try:
                    count_query = f"SELECT COUNT(*) FROM {table}"
                    count_result = session.execute(count_query)
                    count = count_result.one().count
                    print(f"  - {table}: {count:,} enregistrements")
                except Exception as e:
                    print(f"  - {table}: Erreur de comptage")
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération d'infos: {e}")
        finally:
            close_cassandra_connection()
    
    def import_large_csv(self, csv_file, table_name, batch_size=1000):
        """Importer un fichier CSV volumineux par lots"""
        print(f"📥 Import de {csv_file} vers {table_name}")
        
        try:
            # Utiliser pandas pour lire par chunks
            chunk_reader = pd.read_csv(csv_file, chunksize=batch_size)
            total_imported = 0
            
            session = get_cassandra_session()
            
            for chunk_num, chunk in enumerate(chunk_reader):
                print(f"Traitement du lot {chunk_num + 1} ({len(chunk)} lignes)")
                
                # Insérer chaque ligne (à adapter selon la table)
                for _, row in chunk.iterrows():
                    try:
                        # Exemple pour la table players (à adapter)
                        if table_name == 'players':
                            insert_query = """
                            INSERT INTO players (player_id, player_name, date_of_birth, 
                                               place_of_birth, country_of_birth, height, 
                                               position, main_position, foot, current_club_name,
                                               created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """
                            
                            values = (
                                int(row.get('player_id')),
                                row.get('player_name', ''),
                                pd.to_datetime(row.get('date_of_birth')).date() if pd.notna(row.get('date_of_birth')) else None,
                                row.get('place_of_birth', ''),
                                row.get('country_of_birth', ''),
                                float(row.get('height')) if pd.notna(row.get('height')) and row.get('height') != 0.0 else None,
                                row.get('position', ''),
                                row.get('main_position', ''),
                                row.get('foot', ''),
                                row.get('current_club_name', ''),
                                datetime.now(),
                                datetime.now()
                            )
                            
                            session.execute(insert_query, values)
                            total_imported += 1
                    
                    except Exception as e:
                        print(f"Erreur ligne: {e}")
                        continue
                
                print(f"✅ {total_imported} lignes importées")
            
            print(f"🎉 Import terminé: {total_imported} lignes au total")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'import: {e}")
        finally:
            close_cassandra_connection()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Administration de Cassandra")
    parser.add_argument("--snapshot", action="store_true", help="Créer un snapshot")
    parser.add_argument("--export-json", type=str, help="Exporter en JSON vers fichier")
    parser.add_argument("--restore-json", type=str, help="Restaurer depuis JSON")
    parser.add_argument("--optimize", action="store_true", help="Optimiser le keyspace")
    parser.add_argument("--info", action="store_true", help="Afficher les informations")
    parser.add_argument("--import-csv", nargs=2, metavar=('CSV_FILE', 'TABLE_NAME'), 
                       help="Importer un CSV volumineux")
    
    args = parser.parse_args()
    admin = CassandraAdmin()
    
    if args.snapshot:
        admin.create_snapshot()
    elif args.export_json:
        admin.export_to_json(args.export_json)
    elif args.restore_json:
        admin.restore_from_json(args.restore_json)
    elif args.optimize:
        admin.optimize_keyspace()
    elif args.info:
        admin.get_cluster_info()
    elif args.import_csv:
        admin.import_large_csv(args.import_csv[0], args.import_csv[1])
    else:
        print("Utilisez --help pour voir les options disponibles")
        print("\nExemples d'utilisation:")
        print("  python db_admin.py --snapshot")
        print("  python db_admin.py --export-json backup.json")
        print("  python db_admin.py --info")