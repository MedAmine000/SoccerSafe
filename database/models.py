"""
Configuration de base de données Cassandra et modèles
"""
import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy
from dotenv import load_dotenv
from datetime import datetime, date
import uuid
from typing import Optional, List

load_dotenv()

# Configuration Cassandra
class CassandraConfig:
    def __init__(self):
        self.hosts = os.getenv('CASSANDRA_HOSTS', 'localhost').split(',')
        self.port = int(os.getenv('CASSANDRA_PORT', '9042'))
        self.keyspace = os.getenv('CASSANDRA_KEYSPACE', 'football_injuries')
        self.username = os.getenv('CASSANDRA_USERNAME')
        self.password = os.getenv('CASSANDRA_PASSWORD')
        self.datacenter = os.getenv('CASSANDRA_DATACENTER', 'datacenter1')
        
        # Configuration de l'authentification
        self.auth_provider = None
        if self.username and self.password:
            self.auth_provider = PlainTextAuthProvider(
                username=self.username, 
                password=self.password
            )
        
        # Configuration de la politique de charge
        self.load_balancing_policy = DCAwareRoundRobinPolicy(
            local_dc=self.datacenter
        )

# Instance globale de configuration
cassandra_config = CassandraConfig()

# Cluster et session Cassandra
cluster = None
session = None

def get_cassandra_session():
    """Obtenir une session Cassandra"""
    global cluster, session
    
    if session is None:
        cluster = Cluster(
            cassandra_config.hosts,
            port=cassandra_config.port,
            auth_provider=cassandra_config.auth_provider,
            load_balancing_policy=cassandra_config.load_balancing_policy
        )
        session = cluster.connect()
        
        # Créer le keyspace s'il n'existe pas
        create_keyspace_if_not_exists()
        
        # Utiliser le keyspace
        session.set_keyspace(cassandra_config.keyspace)
    
    return session

def create_keyspace_if_not_exists():
    """Créer le keyspace s'il n'existe pas"""
    global session
    
    keyspace_query = f"""
    CREATE KEYSPACE IF NOT EXISTS {cassandra_config.keyspace}
    WITH REPLICATION = {{
        'class': 'SimpleStrategy',
        'replication_factor': 3
    }}
    """
    
    session.execute(keyspace_query)
    print(f"✅ Keyspace '{cassandra_config.keyspace}' créé/vérifié")

def close_cassandra_connection():
    """Fermer la connexion Cassandra"""
    global cluster, session
    if session:
        session.shutdown()
    if cluster:
        cluster.shutdown()

# Modèles de données pour Cassandra
class CassandraTable:
    """Classe de base pour les tables Cassandra"""
    
    @classmethod
    def create_table(cls):
        """Créer la table dans Cassandra"""
        session = get_cassandra_session()
        session.execute(cls.create_statement())
        print(f"✅ Table {cls.table_name} créée/vérifiée")
    
    @classmethod
    def create_statement(cls):
        """Statement de création de table - à override"""
        raise NotImplementedError

class Player(CassandraTable):
    table_name = "players"
    
    @classmethod
    def create_statement(cls):
        return """
        CREATE TABLE IF NOT EXISTS players (
            player_id int PRIMARY KEY,
            player_name text,
            date_of_birth date,
            place_of_birth text,
            country_of_birth text,
            height float,
            position text,
            main_position text,
            foot text,
            current_club_name text,
            created_at timestamp,
            updated_at timestamp
        )
        """
    
    def __init__(self, player_id=None, player_name=None, date_of_birth=None, 
                 place_of_birth=None, country_of_birth=None, height=None,
                 position=None, main_position=None, foot=None, 
                 current_club_name=None, created_at=None, updated_at=None):
        self.player_id = player_id
        self.player_name = player_name
        self.date_of_birth = date_of_birth
        self.place_of_birth = place_of_birth
        self.country_of_birth = country_of_birth
        self.height = height
        self.position = position
        self.main_position = main_position
        self.foot = foot
        self.current_club_name = current_club_name
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

class Injury(CassandraTable):
    table_name = "injuries"
    
    @classmethod
    def create_statement(cls):
        return """
        CREATE TABLE IF NOT EXISTS injuries (
            injury_id uuid PRIMARY KEY,
            player_id int,
            season_name text,
            injury_reason text,
            from_date date,
            end_date date,
            days_missed float,
            games_missed int,
            severity_score float,
            created_at timestamp
        )
        """
    
    @classmethod
    def create_indexes(cls):
        """Créer les index secondaires"""
        session = get_cassandra_session()
        indexes = [
            "CREATE INDEX IF NOT EXISTS ON injuries (player_id)",
            "CREATE INDEX IF NOT EXISTS ON injuries (season_name)",
            "CREATE INDEX IF NOT EXISTS ON injuries (injury_reason)"
        ]
        for index in indexes:
            try:
                session.execute(index)
            except Exception as e:
                print(f"Index déjà existant: {e}")
    
    def __init__(self, injury_id=None, player_id=None, season_name=None,
                 injury_reason=None, from_date=None, end_date=None,
                 days_missed=None, games_missed=None, severity_score=None,
                 created_at=None):
        self.injury_id = injury_id or uuid.uuid4()
        self.player_id = player_id
        self.season_name = season_name
        self.injury_reason = injury_reason
        self.from_date = from_date
        self.end_date = end_date
        self.days_missed = days_missed
        self.games_missed = games_missed
        self.severity_score = severity_score
        self.created_at = created_at or datetime.now()

class Performance(CassandraTable):
    table_name = "performances"
    
    @classmethod
    def create_statement(cls):
        return """
        CREATE TABLE IF NOT EXISTS performances (
            performance_id uuid PRIMARY KEY,
            player_id int,
            match_date date,
            minutes_played int,
            goals int,
            assists int,
            yellow_cards int,
            red_cards int,
            rating float,
            created_at timestamp
        )
        """
    
    @classmethod
    def create_indexes(cls):
        """Créer les index secondaires"""
        session = get_cassandra_session()
        indexes = [
            "CREATE INDEX IF NOT EXISTS ON performances (player_id)",
            "CREATE INDEX IF NOT EXISTS ON performances (match_date)"
        ]
        for index in indexes:
            try:
                session.execute(index)
            except Exception as e:
                print(f"Index déjà existant: {e}")
    
    def __init__(self, performance_id=None, player_id=None, match_date=None,
                 minutes_played=None, goals=0, assists=0, yellow_cards=0,
                 red_cards=0, rating=None, created_at=None):
        self.performance_id = performance_id or uuid.uuid4()
        self.player_id = player_id
        self.match_date = match_date
        self.minutes_played = minutes_played
        self.goals = goals
        self.assists = assists
        self.yellow_cards = yellow_cards
        self.red_cards = red_cards
        self.rating = rating
        self.created_at = created_at or datetime.now()

class WeatherData(CassandraTable):
    table_name = "weather_data"
    
    @classmethod
    def create_statement(cls):
        return """
        CREATE TABLE IF NOT EXISTS weather_data (
            weather_id uuid PRIMARY KEY,
            match_date date,
            city text,
            temperature float,
            humidity float,
            wind_speed float,
            weather_condition text,
            created_at timestamp
        )
        """
    
    @classmethod
    def create_indexes(cls):
        """Créer les index secondaires"""
        session = get_cassandra_session()
        indexes = [
            "CREATE INDEX IF NOT EXISTS ON weather_data (match_date)",
            "CREATE INDEX IF NOT EXISTS ON weather_data (city)"
        ]
        for index in indexes:
            try:
                session.execute(index)
            except Exception as e:
                print(f"Index déjà existant: {e}")
    
    def __init__(self, weather_id=None, match_date=None, city=None,
                 temperature=None, humidity=None, wind_speed=None,
                 weather_condition=None, created_at=None):
        self.weather_id = weather_id or uuid.uuid4()
        self.match_date = match_date
        self.city = city
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.weather_condition = weather_condition
        self.created_at = created_at or datetime.now()

class APILog(CassandraTable):
    table_name = "api_logs"
    
    @classmethod
    def create_statement(cls):
        return """
        CREATE TABLE IF NOT EXISTS api_logs (
            log_id uuid PRIMARY KEY,
            api_name text,
            endpoint text,
            status_code int,
            response_time float,
            created_at timestamp
        )
        """
    
    @classmethod
    def create_indexes(cls):
        """Créer les index secondaires"""
        session = get_cassandra_session()
        indexes = [
            "CREATE INDEX IF NOT EXISTS ON api_logs (api_name)",
            "CREATE INDEX IF NOT EXISTS ON api_logs (created_at)"
        ]
        for index in indexes:
            try:
                session.execute(index)
            except Exception as e:
                print(f"Index déjà existant: {e}")
    
    def __init__(self, log_id=None, api_name=None, endpoint=None,
                 status_code=None, response_time=None, created_at=None):
        self.log_id = log_id or uuid.uuid4()
        self.api_name = api_name
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_time = response_time
        self.created_at = created_at or datetime.now()

# Modèle pour les analyses agrégées (dénormalisation Cassandra)
class InjuryStats(CassandraTable):
    table_name = "injury_stats"
    
    @classmethod
    def create_statement(cls):
        return """
        CREATE TABLE IF NOT EXISTS injury_stats (
            stat_id uuid PRIMARY KEY,
            stat_type text,
            stat_key text,
            stat_value float,
            count int,
            period_start date,
            period_end date,
            created_at timestamp
        )
        """
    
    @classmethod
    def create_indexes(cls):
        """Créer les index secondaires"""
        session = get_cassandra_session()
        indexes = [
            "CREATE INDEX IF NOT EXISTS ON injury_stats (stat_type)",
            "CREATE INDEX IF NOT EXISTS ON injury_stats (stat_key)"
        ]
        for index in indexes:
            try:
                session.execute(index)
            except Exception as e:
                print(f"Index déjà existant: {e}")

def create_all_tables():
    """Créer toutes les tables Cassandra"""
    print("🗄️ Création des tables Cassandra...")
    
    tables = [Player, Injury, Performance, WeatherData, APILog, InjuryStats]
    
    for table_class in tables:
        table_class.create_table()
        if hasattr(table_class, 'create_indexes'):
            table_class.create_indexes()
    
    print("✅ Toutes les tables Cassandra créées/vérifiées")

if __name__ == "__main__":
    create_all_tables()
    print("Configuration Cassandra terminée!")