"""
Opérations CRUD pour Cassandra
"""
from database.models import (
    get_cassandra_session, Player, Injury, Performance, 
    WeatherData, APILog, InjuryStats
)
from datetime import datetime, date
from typing import List, Optional, Dict, Any
import pandas as pd
import uuid
from cassandra.query import SimpleStatement

class PlayerCRUD:
    @staticmethod
    def create_player(player_data: dict):
        """Créer un nouveau joueur"""
        session = get_cassandra_session()
        
        # Préparer les données
        player_data['created_at'] = datetime.now()
        player_data['updated_at'] = datetime.now()
        
        # Statement d'insertion
        insert_query = """
        INSERT INTO players (player_id, player_name, date_of_birth, place_of_birth,
                           country_of_birth, height, position, main_position, foot,
                           current_club_name, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            player_data.get('player_id'),
            player_data.get('player_name'),
            player_data.get('date_of_birth'),
            player_data.get('place_of_birth'),
            player_data.get('country_of_birth'),
            player_data.get('height'),
            player_data.get('position'),
            player_data.get('main_position'),
            player_data.get('foot'),
            player_data.get('current_club_name'),
            player_data['created_at'],
            player_data['updated_at']
        )
        
        session.execute(insert_query, values)
        return player_data
    
    @staticmethod
    def get_player(player_id: int):
        """Récupérer un joueur par ID"""
        session = get_cassandra_session()
        query = "SELECT * FROM players WHERE player_id = ?"
        result = session.execute(query, (player_id,))
        return result.one() if result else None
    
    @staticmethod
    def get_players(limit: int = 100):
        """Récupérer une liste de joueurs"""
        session = get_cassandra_session()
        query = f"SELECT * FROM players LIMIT {limit}"
        result = session.execute(query)
        return list(result)
    
    @staticmethod
    def update_player(player_id: int, player_data: dict):
        """Mettre à jour un joueur"""
        session = get_cassandra_session()
        
        # Ajouter timestamp de mise à jour
        player_data['updated_at'] = datetime.now()
        
        # Construire la requête de mise à jour dynamiquement
        set_clauses = []
        values = []
        
        for key, value in player_data.items():
            if key != 'player_id':  # Ne pas mettre à jour la clé primaire
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        values.append(player_id)  # Pour la clause WHERE
        
        update_query = f"""
        UPDATE players SET {', '.join(set_clauses)}
        WHERE player_id = ?
        """
        
        session.execute(update_query, values)
        return player_data
    
    @staticmethod
    def delete_player(player_id: int):
        """Supprimer un joueur"""
        session = get_cassandra_session()
        delete_query = "DELETE FROM players WHERE player_id = ?"
        session.execute(delete_query, (player_id,))
        return True
    
    @staticmethod
    def search_players_by_position(position: str):
        """Rechercher des joueurs par position"""
        session = get_cassandra_session()
        # Note: Cassandra nécessite ALLOW FILTERING pour les requêtes non-indexées
        query = "SELECT * FROM players WHERE main_position = ? ALLOW FILTERING"
        result = session.execute(query, (position,))
        return list(result)
    
    @staticmethod
    def get_players_by_club(club_name: str):
        """Récupérer les joueurs par club"""
        session = get_cassandra_session()
        query = "SELECT * FROM players WHERE current_club_name = ? ALLOW FILTERING"
        result = session.execute(query, (club_name,))
        return list(result)

class InjuryCRUD:
    @staticmethod
    def create_injury(injury_data: dict):
        """Créer une nouvelle blessure"""
        session = get_cassandra_session()
        
        # Calculer le score de sévérité
        if injury_data.get('days_missed'):
            severity_score = min(injury_data['days_missed'] / 30, 10)  # Score de 0 à 10
            injury_data['severity_score'] = severity_score
        
        # Générer un UUID pour l'injury_id
        injury_id = uuid.uuid4()
        injury_data['injury_id'] = injury_id
        injury_data['created_at'] = datetime.now()
        
        # Statement d'insertion
        insert_query = """
        INSERT INTO injuries (injury_id, player_id, season_name, injury_reason,
                            from_date, end_date, days_missed, games_missed,
                            severity_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            injury_data['injury_id'],
            injury_data.get('player_id'),
            injury_data.get('season_name'),
            injury_data.get('injury_reason'),
            injury_data.get('from_date'),
            injury_data.get('end_date'),
            injury_data.get('days_missed'),
            injury_data.get('games_missed'),
            injury_data.get('severity_score'),
            injury_data['created_at']
        )
        
        session.execute(insert_query, values)
        return injury_data
    
    @staticmethod
    def get_player_injuries(player_id: int):
        """Récupérer toutes les blessures d'un joueur"""
        session = get_cassandra_session()
        query = "SELECT * FROM injuries WHERE player_id = ?"
        result = session.execute(query, (player_id,))
        return list(result)
    
    @staticmethod
    def get_injuries_by_type(injury_type: str):
        """Récupérer les blessures par type"""
        session = get_cassandra_session()
        query = "SELECT * FROM injuries WHERE injury_reason = ?"
        result = session.execute(query, (injury_type,))
        return list(result)
    
    @staticmethod
    def get_injuries_by_season(season: str):
        """Récupérer les blessures par saison"""
        session = get_cassandra_session()
        query = "SELECT * FROM injuries WHERE season_name = ?"
        result = session.execute(query, (season,))
        return list(result)
    
    @staticmethod
    def update_injury(injury_id: uuid.UUID, injury_data: dict):
        """Mettre à jour une blessure"""
        session = get_cassandra_session()
        
        # Construire la requête de mise à jour dynamiquement
        set_clauses = []
        values = []
        
        for key, value in injury_data.items():
            if key != 'injury_id':  # Ne pas mettre à jour la clé primaire
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        values.append(injury_id)  # Pour la clause WHERE
        
        update_query = f"""
        UPDATE injuries SET {', '.join(set_clauses)}
        WHERE injury_id = ?
        """
        
        session.execute(update_query, values)
        return injury_data
    
    @staticmethod
    def delete_injury(injury_id: uuid.UUID):
        """Supprimer une blessure"""
        session = get_cassandra_session()
        delete_query = "DELETE FROM injuries WHERE injury_id = ?"
        session.execute(delete_query, (injury_id,))
        return True
    
    @staticmethod
    def get_injury_statistics():
        """Obtenir des statistiques sur les blessures"""
        session = get_cassandra_session()
        
        # Compter le total des blessures
        count_query = "SELECT COUNT(*) FROM injuries"
        total_result = session.execute(count_query)
        total_injuries = total_result.one().count
        
        # Calculer la moyenne des jours manqués (nécessite de récupérer toutes les données)
        all_injuries_query = "SELECT days_missed FROM injuries"
        all_injuries = session.execute(all_injuries_query)
        
        days_missed_list = [row.days_missed for row in all_injuries if row.days_missed is not None]
        avg_days_missed = sum(days_missed_list) / len(days_missed_list) if days_missed_list else 0
        
        return {
            "total_injuries": total_injuries,
            "average_days_missed": round(avg_days_missed, 2)
        }

class PerformanceCRUD:
    @staticmethod
    def create_performance(performance_data: dict):
        """Créer une nouvelle performance"""
        session = get_cassandra_session()
        
        # Générer un UUID pour performance_id
        performance_id = uuid.uuid4()
        performance_data['performance_id'] = performance_id
        performance_data['created_at'] = datetime.now()
        
        # Statement d'insertion
        insert_query = """
        INSERT INTO performances (performance_id, player_id, match_date, minutes_played,
                                goals, assists, yellow_cards, red_cards, rating, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            performance_data['performance_id'],
            performance_data.get('player_id'),
            performance_data.get('match_date'),
            performance_data.get('minutes_played'),
            performance_data.get('goals', 0),
            performance_data.get('assists', 0),
            performance_data.get('yellow_cards', 0),
            performance_data.get('red_cards', 0),
            performance_data.get('rating'),
            performance_data['created_at']
        )
        
        session.execute(insert_query, values)
        return performance_data
    
    @staticmethod
    def get_player_performances(player_id: int, limit: int = 50):
        """Récupérer les performances d'un joueur"""
        session = get_cassandra_session()
        query = f"SELECT * FROM performances WHERE player_id = ? LIMIT {limit}"
        result = session.execute(query, (player_id,))
        return list(result)
    
    @staticmethod
    def bulk_create_performances(performances_data: List[dict]):
        """Créer plusieurs performances en une fois"""
        session = get_cassandra_session()
        
        # Préparer le statement d'insertion
        insert_query = """
        INSERT INTO performances (performance_id, player_id, match_date, minutes_played,
                                goals, assists, yellow_cards, red_cards, rating, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Préparer toutes les données
        for performance_data in performances_data:
            performance_data['performance_id'] = uuid.uuid4()
            performance_data['created_at'] = datetime.now()
            
            values = (
                performance_data['performance_id'],
                performance_data.get('player_id'),
                performance_data.get('match_date'),
                performance_data.get('minutes_played'),
                performance_data.get('goals', 0),
                performance_data.get('assists', 0),
                performance_data.get('yellow_cards', 0),
                performance_data.get('red_cards', 0),
                performance_data.get('rating'),
                performance_data['created_at']
            )
            
            session.execute(insert_query, values)
        
        return performances_data

class WeatherCRUD:
    @staticmethod
    def create_weather_data(weather_data: dict):
        """Créer des données météo"""
        session = get_cassandra_session()
        
        # Générer un UUID pour weather_id
        weather_id = uuid.uuid4()
        weather_data['weather_id'] = weather_id
        weather_data['created_at'] = datetime.now()
        
        # Statement d'insertion
        insert_query = """
        INSERT INTO weather_data (weather_id, match_date, city, temperature,
                                humidity, wind_speed, weather_condition, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            weather_data['weather_id'],
            weather_data.get('match_date'),
            weather_data.get('city'),
            weather_data.get('temperature'),
            weather_data.get('humidity'),
            weather_data.get('wind_speed'),
            weather_data.get('weather_condition'),
            weather_data['created_at']
        )
        
        session.execute(insert_query, values)
        return weather_data
    
    @staticmethod
    def get_weather_by_date(match_date: date):
        """Récupérer les données météo par date"""
        session = get_cassandra_session()
        query = "SELECT * FROM weather_data WHERE match_date = ?"
        result = session.execute(query, (match_date,))
        return result.one() if result else None

class DataImporter:
    @staticmethod
    def import_players_from_csv(csv_path: str):
        """Importer les joueurs depuis un fichier CSV"""
        df = pd.read_csv(csv_path)
        imported_count = 0
        
        print(f"📊 Import de {len(df)} joueurs depuis {csv_path}")
        
        for _, row in df.iterrows():
            try:
                # Vérifier si le joueur existe déjà
                existing_player = PlayerCRUD.get_player(row['player_id'])
                if not existing_player:
                    player_data = {
                        'player_id': int(row['player_id']),
                        'player_name': row.get('player_name', ''),
                        'date_of_birth': pd.to_datetime(row['date_of_birth']).date() if pd.notna(row.get('date_of_birth')) else None,
                        'place_of_birth': row.get('place_of_birth', ''),
                        'country_of_birth': row.get('country_of_birth', ''),
                        'height': float(row['height']) if pd.notna(row.get('height')) and row.get('height') != 0.0 else None,
                        'position': row.get('position', ''),
                        'main_position': row.get('main_position', ''),
                        'foot': row.get('foot', ''),
                        'current_club_name': row.get('current_club_name', '')
                    }
                    PlayerCRUD.create_player(player_data)
                    imported_count += 1
                    
                    # Afficher le progrès
                    if imported_count % 1000 == 0:
                        print(f"  ✅ {imported_count} joueurs importés...")
                        
            except Exception as e:
                print(f"❌ Erreur lors de l'import du joueur {row.get('player_id', 'N/A')}: {e}")
                continue
        
        print(f"🎉 Import terminé: {imported_count} joueurs importés")
        return imported_count
    
    @staticmethod
    def import_injuries_from_csv(csv_path: str):
        """Importer les blessures depuis un fichier CSV"""
        df = pd.read_csv(csv_path)
        imported_count = 0
        
        print(f"🏥 Import de {len(df)} blessures depuis {csv_path}")
        
        for _, row in df.iterrows():
            try:
                injury_data = {
                    'player_id': int(row['player_id']),
                    'season_name': row['season_name'],
                    'injury_reason': row['injury_reason'],
                    'from_date': pd.to_datetime(row['from_date']).date() if pd.notna(row['from_date']) else None,
                    'end_date': pd.to_datetime(row['end_date']).date() if pd.notna(row['end_date']) else None,
                    'days_missed': float(row['days_missed']) if pd.notna(row['days_missed']) else None,
                    'games_missed': int(row['games_missed']) if pd.notna(row['games_missed']) else None
                }
                InjuryCRUD.create_injury(injury_data)
                imported_count += 1
                
                # Afficher le progrès
                if imported_count % 5000 == 0:
                    print(f"  ✅ {imported_count} blessures importées...")
                    
            except Exception as e:
                print(f"❌ Erreur lors de l'import de la blessure: {e}")
                continue
        
        print(f"🎉 Import terminé: {imported_count} blessures importées")
        return imported_count
    
    @staticmethod
    def import_all_data():
        """Importer toutes les données CSV"""
        print("🚀 Import complet des données...")
        
        # Importer les joueurs
        players_count = DataImporter.import_players_from_csv("data/player_profiles.csv")
        
        # Importer les blessures
        injuries_count = DataImporter.import_injuries_from_csv("data/player_injuries.csv")
        
        print(f"✅ Import terminé: {players_count} joueurs, {injuries_count} blessures")
        return players_count + injuries_count


class APILogCRUD:
    """CRUD operations pour les logs d'API"""
    
    def __init__(self, session):
        self.session = session
        
    def create(self, log_data: dict):
        """Créer un nouveau log d'API"""
        log_data['log_id'] = uuid.uuid4()
        log_data['created_at'] = datetime.now()
        
        insert_query = """
        INSERT INTO api_logs (log_id, api_name, endpoint, status_code, response_time, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        values = (
            log_data['log_id'],
            log_data.get('api_name'),
            log_data.get('endpoint'),
            log_data.get('status_code'),
            log_data.get('response_time'),
            log_data['created_at']
        )
        
        self.session.execute(insert_query, values)
        return log_data
    
    def get_recent_logs(self, limit: int = 100):
        """Récupérer les logs récents"""
        query = f"SELECT * FROM api_logs LIMIT {limit}"
        result = self.session.execute(query)
        return list(result)
    
    def delete_old_logs(self, cutoff_date: datetime):
        """Supprimer les anciens logs (simulation pour Cassandra)"""
        # Note: Cassandra ne supporte pas DELETE avec WHERE sur les dates non-clé
        # Dans une vraie implémentation, on utiliserait TTL ou une partition par date
        
        # Pour cette démo, nous simulons la suppression
        query = "SELECT COUNT(*) FROM api_logs"
        result = self.session.execute(query)
        count_before = list(result)[0].count if result else 0
        
        # Ici, on pourrait implémenter une vraie suppression avec une stratégie
        # adaptée à Cassandra (par ex. TTL ou partitioning par date)
        
        return 0  # Simulé pour éviter les erreurs


class WeatherCRUD:
    """CRUD operations pour les données météo"""
    
    def __init__(self, session):
        self.session = session
        
    def create_weather_data(self, weather_data: dict):
        """Créer une nouvelle donnée météo"""
        weather_data['weather_id'] = uuid.uuid4()
        weather_data['created_at'] = datetime.now()
        
        insert_query = """
        INSERT INTO weather_data (weather_id, location, temperature, humidity, 
                                wind_speed, conditions, date, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            weather_data['weather_id'],
            weather_data.get('location'),
            weather_data.get('temperature'),
            weather_data.get('humidity'),
            weather_data.get('wind_speed'),
            weather_data.get('conditions'),
            weather_data.get('date'),
            weather_data['created_at']
        )
        
        self.session.execute(insert_query, values)
        return weather_data
    
    def get_weather_by_location_date(self, location: str, date: str):
        """Récupérer les données météo par localisation et date"""
        query = "SELECT * FROM weather_data WHERE location = ? AND date = ?"
        result = self.session.execute(query, (location, date))
        return list(result)