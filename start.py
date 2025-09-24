"""
Script de démarrage principal pour Football Injury Analytics
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Vérifier que toutes les dépendances sont installées"""
    try:
        import pandas
        import streamlit
        import plotly
        import sklearn
        print("✅ Dépendances Python vérifiées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Installez les dépendances: pip install -r requirements.txt")
        return False

def check_data_files():
    """Vérifier que les fichiers de données sont présents"""
    required_files = [
        "player_injuries.csv",
        "player_profiles.csv"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Fichiers manquants: {', '.join(missing_files)}")
        return False
    
    print("✅ Fichiers de données trouvés")
    return True

def setup_environment():
    """Configurer l'environnement si nécessaire"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        print("🔧 Création du fichier .env...")
        import shutil
        shutil.copy(env_example, env_file)
        print("⚠️  N'oubliez pas de configurer vos clés API dans .env")
    
    # Créer les dossiers nécessaires
    folders = ["logs", "data", "backups", "reports"]
    for folder in folders:
        Path(folder).mkdir(exist_ok=True)
    
    print("✅ Environnement configuré")

def start_streamlit():
    """Démarrer l'application Streamlit"""
    print("🚀 Démarrage de l'application Streamlit...")
    cmd = [sys.executable, "-m", "streamlit", "run", "webapp/app.py"]
    subprocess.run(cmd)

def setup_database():
    """Configurer la base de données"""
    print("🗄️ Configuration de la base de données...")
    cmd = [sys.executable, "scripts/setup_database.py"]
    result = subprocess.run(cmd)
    return result.returncode == 0

def run_tests():
    """Exécuter les tests"""
    print("🧪 Exécution des tests...")
    cmd = [sys.executable, "tests/test_analytics.py"]
    result = subprocess.run(cmd)
    return result.returncode == 0

def collect_data():
    """Collecter des données via les APIs"""
    print("📡 Collecte de données...")
    cmd = [sys.executable, "scripts/automated_collector.py", "--run-once", "daily"]
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description="Football Injury Analytics - Script de démarrage")
    
    parser.add_argument("--setup", action="store_true", 
                       help="Configuration initiale complète")
    parser.add_argument("--start", action="store_true", 
                       help="Démarrer l'application Streamlit")
    parser.add_argument("--test", action="store_true", 
                       help="Exécuter les tests")
    parser.add_argument("--collect", action="store_true", 
                       help="Collecter des données")
    parser.add_argument("--check", action="store_true", 
                       help="Vérifier l'environnement")
    
    args = parser.parse_args()
    
    # Si aucun argument, afficher l'aide
    if not any(vars(args).values()):
        print("🏈 Football Injury Analytics")
        print("=" * 50)
        print("Usage: python start.py [OPTIONS]")
        print("\nOptions:")
        print("  --setup    Configuration initiale complète")
        print("  --start    Démarrer l'application")
        print("  --test     Exécuter les tests")
        print("  --collect  Collecter des données")
        print("  --check    Vérifier l'environnement")
        print("\nExemples:")
        print("  python start.py --setup     # Première installation")
        print("  python start.py --start     # Démarrer l'app")
        print("  python start.py --check     # Vérifier la config")
        return
    
    if args.check or args.setup:
        print("🔍 Vérification de l'environnement...")
        
        if not check_dependencies():
            return
        
        if not check_data_files():
            print("💡 Placez les fichiers CSV dans le répertoire racine")
            return
        
        setup_environment()
        
        if args.setup:
            if not setup_database():
                print("❌ Erreur lors de la configuration de la base de données")
                return
    
    if args.test:
        if not run_tests():
            print("❌ Des tests ont échoué")
            return
    
    if args.collect:
        collect_data()
    
    if args.start:
        if not check_dependencies() or not check_data_files():
            print("❌ Environnement non configuré. Utilisez --setup d'abord")
            return
        
        start_streamlit()

if __name__ == "__main__":
    main()