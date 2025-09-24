"""
Module pour récupérer des données via les APIs externes
Football-API, Weather API, etc.
"""
import requests
import os
from datetime import datetime, date, timedelta
import pandas as pd
from typing import List, Dict, Optional
import time
import json
from dotenv import load_dotenv

load_dotenv()

class FootballAPI:
    """Classe pour interagir avec l'API Football"""
    
    def __init__(self):
        self.api_key = os.getenv('API_FOOTBALL_KEY')
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
        }
    
    def get_leagues(self, country: str = "England"):
        """Récupérer les ligues d'un pays"""
        url = f"{self.base_url}/leagues"
        params = {"country": country}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erreur API Football (leagues): {e}")
            return None
    
    def get_fixtures(self, league_id: int, season: int, date_from: str = None, date_to: str = None):
        """Récupérer les matchs d'une ligue"""
        url = f"{self.base_url}/fixtures"
        params = {
            "league": league_id,
            "season": season
        }
        
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erreur API Football (fixtures): {e}")
            return None
    
    def get_team_players(self, team_id: int, season: int):
        """Récupérer les joueurs d'une équipe"""
        url = f"{self.base_url}/players"
        params = {
            "team": team_id,
            "season": season
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erreur API Football (players): {e}")
            return None
    
    def get_player_statistics(self, player_id: int, season: int):
        """Récupérer les statistiques d'un joueur"""
        url = f"{self.base_url}/players"
        params = {
            "id": player_id,
            "season": season
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erreur API Football (player stats): {e}")
            return None

class WeatherAPI:
    """Classe pour récupérer les données météorologiques"""
    
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def get_weather_by_city_date(self, city: str, date_obj: date):
        """Récupérer la météo pour une ville et une date"""
        # Pour les données historiques, utiliser l'API historique
        timestamp = int(datetime.combine(date_obj, datetime.min.time()).timestamp())
        url = f"{self.base_url}/onecall/timemachine"
        
        # Obtenir les coordonnées de la ville d'abord
        coords = self._get_city_coordinates(city)
        if not coords:
            return None
        
        params = {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "dt": timestamp,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erreur Weather API: {e}")
            return None
    
    def _get_city_coordinates(self, city: str):
        """Obtenir les coordonnées d'une ville"""
        url = f"http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": city,
            "limit": 1,
            "appid": self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if data:
                return {"lat": data[0]["lat"], "lon": data[0]["lon"]}
        except requests.RequestException as e:
            print(f"Erreur geocoding: {e}")
        
        return None

class DataCollector:
    """Collecteur de données automatisé"""
    
    def __init__(self):
        self.football_api = FootballAPI()
        self.weather_api = WeatherAPI()
    
    def collect_recent_matches(self, league_id: int = 39, season: int = 2024):
        """Collecter les matchs récents de Premier League"""
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        fixtures = self.football_api.get_fixtures(
            league_id=league_id,
            season=season,
            date_from=week_ago.strftime("%Y-%m-%d"),
            date_to=today.strftime("%Y-%m-%d")
        )
        
        if not fixtures or "response" not in fixtures:
            return []
        
        matches_data = []
        for fixture in fixtures["response"]:
            match_data = {
                "fixture_id": fixture["fixture"]["id"],
                "date": fixture["fixture"]["date"],
                "home_team": fixture["teams"]["home"]["name"],
                "away_team": fixture["teams"]["away"]["name"],
                "venue": fixture["fixture"]["venue"]["name"],
                "city": fixture["fixture"]["venue"]["city"]
            }
            matches_data.append(match_data)
        
        return matches_data
    
    def collect_weather_for_matches(self, matches_data: List[Dict]):
        """Collecter la météo pour les matchs"""
        weather_data = []
        
        for match in matches_data:
            match_date = datetime.fromisoformat(match["date"].replace("Z", "+00:00")).date()
            city = match["city"]
            
            if city:
                weather = self.weather_api.get_weather_by_city_date(city, match_date)
                if weather and "current" in weather:
                    weather_info = {
                        "match_date": match_date,
                        "city": city,
                        "temperature": weather["current"]["temp"],
                        "humidity": weather["current"]["humidity"],
                        "wind_speed": weather["current"]["wind_speed"],
                        "weather_condition": weather["current"]["weather"][0]["main"]
                    }
                    weather_data.append(weather_info)
                    
                # Respecter les limites de l'API
                time.sleep(1)
        
        return weather_data
    
    def collect_daily_update(self):
        """Collecte quotidienne de données"""
        print(f"🔄 Collecte quotidienne - {datetime.now()}")
        
        # Collecter les matchs récents
        matches = self.collect_recent_matches()
        print(f"📅 {len(matches)} matchs récents collectés")
        
        # Collecter la météo pour ces matchs
        weather = self.collect_weather_for_matches(matches)
        print(f"🌤️  {len(weather)} données météo collectées")
        
        # Sauvegarder dans des fichiers JSON avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarder les matchs
        matches_file = f"data/matches_{timestamp}.json"
        with open(matches_file, 'w') as f:
            json.dump(matches, f, indent=2, default=str)
        
        # Sauvegarder la météo
        weather_file = f"data/weather_{timestamp}.json"
        with open(weather_file, 'w') as f:
            json.dump(weather, f, indent=2, default=str)
        
        return {
            "matches_collected": len(matches),
            "weather_collected": len(weather),
            "matches_file": matches_file,
            "weather_file": weather_file
        }

class KaggleDataDownloader:
    """Téléchargeur de datasets Kaggle complémentaires"""
    
    def __init__(self):
        # Nécessite kaggle API configurée
        pass
    
    def download_player_stats_dataset(self, dataset_name: str = "davidcariboo/player-scores"):
        """Télécharger un dataset de statistiques de joueurs depuis Kaggle"""
        try:
            import kaggle
            
            # Télécharger le dataset
            kaggle.api.dataset_download_files(
                dataset_name,
                path="data/kaggle/",
                unzip=True
            )
            
            print(f"✅ Dataset {dataset_name} téléchargé")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement Kaggle: {e}")
            return False
    
    def list_football_datasets(self):
        """Lister les datasets football disponibles sur Kaggle"""
        try:
            import kaggle
            
            datasets = kaggle.api.dataset_list(search="football", page_size=20)
            
            print("⚽ Datasets Football disponibles sur Kaggle:")
            print("-" * 50)
            
            for dataset in datasets:
                print(f"📊 {dataset.ref}")
                print(f"   Titre: {dataset.title}")
                print(f"   Taille: {dataset.size}")
                print(f"   Dernière MAJ: {dataset.lastUpdated}")
                print()
            
            return datasets
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche Kaggle: {e}")
            return []

if __name__ == "__main__":
    # Test de collecte de données
    collector = DataCollector()
    result = collector.collect_daily_update()
    print("Résultat de la collecte:", result)