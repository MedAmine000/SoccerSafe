"""
Script de collecte automatisée de données
Peut être exécuté via cron job ou task scheduler
"""
import schedule
import time
import logging
from datetime import datetime
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collector import DataCollector
from database.models import get_cassandra_session
from database.crud import WeatherCRUD, APILogCRUD
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_collection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AutomatedDataCollector:
    """Collecteur de données automatisé"""
    
    def __init__(self):
        self.collector = DataCollector()
        self.session = get_cassandra_session()
        self.api_log_crud = APILogCRUD(self.session)
    
    def daily_collection(self):
        """Collecte quotidienne de données"""
        logger.info("🚀 Début de la collecte quotidienne")
        
        try:
            # Collecter les données
            result = self.collector.collect_daily_update()
            
            # Enregistrer les résultats
            self._log_collection_result(result)
            
            # Envoyer un rapport par email (optionnel)
            if result['matches_collected'] > 0 or result['weather_collected'] > 0:
                self._send_daily_report(result)
            
            logger.info(f"✅ Collecte terminée: {result['matches_collected']} matchs, {result['weather_collected']} météo")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la collecte quotidienne: {e}")
            self._send_error_alert(str(e))
    
    def weekly_analysis(self):
        """Analyse hebdomadaire des tendances"""
        logger.info("📊 Début de l'analyse hebdomadaire")
        
        try:
            # Importer l'analyseur
            from src.analyzer import InjuryAnalyzer
            import pandas as pd
            
            # Charger les données
            injuries_df = pd.read_csv("player_injuries.csv")
            players_df = pd.read_csv("player_profiles.csv")
            
            # Créer l'analyseur
            analyzer = InjuryAnalyzer(injuries_df, players_df)
            
            # Générer le rapport
            report_path = analyzer.export_analysis_report(
                f"reports/weekly_report_{datetime.now().strftime('%Y%m%d')}.html"
            )
            
            logger.info(f"📈 Rapport hebdomadaire généré: {report_path}")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse hebdomadaire: {e}")
    
    def database_maintenance(self):
        """Maintenance de la base de données"""
        logger.info("🔧 Début de la maintenance de la base de données")
        
        try:
            from scripts.db_admin import DatabaseAdmin
            
            admin = DatabaseAdmin()
            
            # Optimiser la base
            admin.optimize_database()
            
            # Créer un backup
            backup_file = admin.create_dump()
            
            # Nettoyer les anciens logs API (>30 jours)
            self._cleanup_old_logs()
            
            logger.info("✅ Maintenance de la base de données terminée")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la maintenance: {e}")
    
    def _log_collection_result(self, result):
        """Enregistrer le résultat de la collecte"""
        try:
            # Log pour l'API Football
            if result['matches_collected'] > 0:
                api_log_data = {
                    'api_name': 'Football API',
                    'endpoint': '/fixtures',
                    'status_code': 200,
                    'response_time': 1.5  # Simulé
                }
                self.api_log_crud.create(api_log_data)
            
            # Log pour l'API Météo
            if result['weather_collected'] > 0:
                api_log_data = {
                    'api_name': 'Weather API',
                    'endpoint': '/weather',
                    'status_code': 200,
                    'response_time': 0.8  # Simulé
                }
                self.api_log_crud.create(api_log_data)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des logs: {e}")
    
    def _cleanup_old_logs(self):
        """Nettoyer les anciens logs API"""
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.now() - timedelta(days=30)
            
            # Utiliser la méthode Cassandra pour nettoyer les anciens logs
            deleted_count = self.api_log_crud.delete_old_logs(cutoff_date)
            
            logger.info(f"🗑️ {deleted_count} anciens logs supprimés")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")
    
    def _send_daily_report(self, result):
        """Envoyer un rapport quotidien par email"""
        try:
            # Configuration email (à personnaliser)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = os.getenv('SENDER_EMAIL')
            sender_password = os.getenv('SENDER_PASSWORD')
            recipient_email = os.getenv('RECIPIENT_EMAIL')
            
            if not all([sender_email, sender_password, recipient_email]):
                logger.warning("Configuration email manquante")
                return
            
            # Créer le message
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = f"Rapport quotidien - {datetime.now().strftime('%d/%m/%Y')}"
            
            body = f"""
            Bonjour,
            
            Voici le rapport de collecte quotidienne:
            
            📅 Matchs collectés: {result['matches_collected']}
            🌤️ Données météo: {result['weather_collected']}
            📁 Fichiers générés:
               - {result.get('matches_file', 'N/A')}
               - {result.get('weather_file', 'N/A')}
            
            Cordialement,
            Le système de collecte automatisée
            """
            
            message.attach(MIMEText(body, "plain"))
            
            # Envoyer l'email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(message)
            
            logger.info("📧 Rapport quotidien envoyé par email")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi d'email: {e}")
    
    def _send_error_alert(self, error_message):
        """Envoyer une alerte en cas d'erreur"""
        logger.error(f"🚨 Alerte d'erreur: {error_message}")
        # Ici vous pourriez implémenter l'envoi d'alertes par email, Slack, etc.

def setup_scheduler():
    """Configurer le planificateur de tâches"""
    collector = AutomatedDataCollector()
    
    # Collecte quotidienne à 6h00
    schedule.every().day.at("06:00").do(collector.daily_collection)
    
    # Analyse hebdomadaire le dimanche à 8h00
    schedule.every().sunday.at("08:00").do(collector.weekly_analysis)
    
    # Maintenance mensuelle le 1er du mois à 2h00
    schedule.every().month.do(collector.database_maintenance)
    
    logger.info("⏰ Planificateur configuré:")
    logger.info("  - Collecte quotidienne: 6h00")
    logger.info("  - Analyse hebdomadaire: Dimanche 8h00")
    logger.info("  - Maintenance: 1er du mois 2h00")

def run_scheduler():
    """Exécuter le planificateur en continu"""
    setup_scheduler()
    
    logger.info("🔄 Démarrage du planificateur...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Vérifier toutes les minutes

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collecteur automatisé de données")
    parser.add_argument("--run-once", choices=['daily', 'weekly', 'maintenance'], 
                       help="Exécuter une tâche une seule fois")
    parser.add_argument("--daemon", action="store_true", 
                       help="Exécuter en mode daemon (planification continue)")
    
    args = parser.parse_args()
    
    collector = AutomatedDataCollector()
    
    if args.run_once:
        if args.run_once == 'daily':
            collector.daily_collection()
        elif args.run_once == 'weekly':
            collector.weekly_analysis()
        elif args.run_once == 'maintenance':
            collector.database_maintenance()
    elif args.daemon:
        run_scheduler()
    else:
        print("Utilisez --help pour voir les options disponibles")
        print("\nExemples d'utilisation:")
        print("  python automated_collector.py --run-once daily")
        print("  python automated_collector.py --daemon")