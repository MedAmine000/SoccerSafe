#!/usr/bin/env python3
"""
🚀 SoccerSafe - Script de Démarrage Principal
Gère l'installation, la configuration et le lancement de l'application
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

class SoccerSafeSetup:
    """Classe pour gérer le setup et lancement de SoccerSafe"""
    
    def __init__(self):
        self.project_name = "⚽ SoccerSafe - Football Injury Analytics"
        self.required_files = [
            "data/player_injuries.csv",
            "data/player_profiles.csv"
        ]
        self.required_packages = [
            ("pandas", "pandas"),
            ("sklearn", "scikit-learn"),
            ("streamlit", "streamlit"),
            ("numpy", "numpy"),
            ("plotly", "plotly")
        ]
    
    def print_header(self):
        """Afficher l'en-tête du projet"""
        print("=" * 70)
        print(self.project_name)
        print("🎓 Projet M1 IPSSI - Base de Données NoSQL")
        print("=" * 70)
    
    def check_python_version(self):
        """Vérifier la version Python"""
        if sys.version_info < (3, 9):
            print(f"❌ Python 3.9+ requis. Version actuelle: {sys.version}")
            return False
        
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} détecté")
        return True

    def check_dependencies(self):
        """Vérifier les dépendances principales"""
        missing = []
        
        for import_name, package_name in self.required_packages:
            try:
                __import__(import_name)
                print(f"✅ {package_name} disponible")
            except ImportError:
                print(f"❌ {package_name} manquant")
                missing.append(package_name)
        
        return len(missing) == 0, missing
    
    def install_dependencies(self):
        """Installer les dépendances"""
        print("\n📦 Installation des dépendances...")
        try:
            cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dépendances installées avec succès")
                return True
            else:
                print(f"❌ Erreur d'installation: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Erreur lors de l'installation: {e}")
            return False

    def check_data_files(self):
        """Vérifier la présence des fichiers de données"""
        print("\n📊 Vérification des fichiers de données...")
        missing = []
        
        for file_path in self.required_files:
            if os.path.exists(file_path):
                # Obtenir la taille du fichier
                size = os.path.getsize(file_path)
                size_mb = size / (1024 * 1024)
                print(f"✅ {file_path} trouvé ({size_mb:.1f} MB)")
            else:
                print(f"❌ {file_path} manquant")
                missing.append(file_path)
        
        if missing:
            print("\n💡 Fichiers manquants:")
            for file in missing:
                print(f"   - {file}")
            print("   Assurez-vous que les fichiers CSV sont dans le dossier data/")
            return False
        
        return True
    
    def setup_environment(self):
        """Configuration de l'environnement"""
        print("\n⚙️ Configuration de l'environnement...")
        
        # Créer .env si nécessaire
        if not os.path.exists(".env"):
            if os.path.exists(".env.example"):
                import shutil
                shutil.copy(".env.example", ".env")
                print("✅ Fichier .env créé depuis .env.example")
            else:
                print("⚠️ Aucun fichier .env.example trouvé")
        else:
            print("✅ Fichier .env existe déjà")
        
        # Créer le dossier models s'il n'existe pas
        models_dir = Path("models")
        if not models_dir.exists():
            models_dir.mkdir()
            print("✅ Dossier models/ créé")
        else:
            print("✅ Dossier models/ existe")
    
    def test_ml_system(self):
        """Tester le système ML"""
        print("\n🧪 Test du système de Machine Learning...")
        try:
            result = subprocess.run(
                [sys.executable, "tests/test_simple.py"], 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minutes max
            )
            
            if result.returncode == 0:
                print("✅ Système ML testé avec succès")
                # Afficher les dernières lignes importantes
                lines = result.stdout.split('\n')
                for line in lines[-10:]:
                    if 'TESTS RÉUSSIS' in line or 'Précision' in line:
                        print(f"   📊 {line.strip()}")
                return True
            else:
                print(f"❌ Erreur dans les tests ML: {result.stderr}")
                return False
        
        except subprocess.TimeoutExpired:
            print("❌ Timeout lors des tests ML (>5min)")
            return False
        except Exception as e:
            print(f"❌ Erreur lors du test: {e}")
            return False
    
    def launch_app(self, app_type="simple"):
        """Lancer l'application Streamlit"""
        app_files = {
            "simple": "webapp/app_simple.py",
            "full": "webapp/app.py"
        }
        
        app_file = app_files.get(app_type, app_files["simple"])
        
        print(f"\n🚀 Lancement de l'application {app_type.upper()}...")
        print(f"📂 Fichier: {app_file}")
        print("🌐 L'application s'ouvrira dans votre navigateur...")
        print("⏹️  Appuyez sur Ctrl+C pour arrêter\n")
        
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", app_file])
        except KeyboardInterrupt:
            print("\n👋 Application arrêtée par l'utilisateur")
        except Exception as e:
            print(f"\n❌ Erreur lors du lancement: {e}")
    
    def full_setup(self):
        """Setup complet du projet"""
        self.print_header()
        
        # Vérifications préalables
        if not self.check_python_version():
            return False
        
        # Installation des dépendances
        deps_ok, missing = self.check_dependencies()
        if not deps_ok:
            print(f"\n📦 Installation des packages manquants: {', '.join(missing)}")
            if not self.install_dependencies():
                return False
        
        # Configuration environnement
        self.setup_environment()
        
        # Vérification données
        if not self.check_data_files():
            return False
        
        # Test ML
        if not self.test_ml_system():
            print("⚠️ Les tests ML ont échoué, mais vous pouvez continuer")
        
        print("\n" + "=" * 70)
        print("🎉 SETUP TERMINÉ AVEC SUCCÈS!")
        print("💡 Vous pouvez maintenant lancer l'application avec:")
        print("   python start.py --start")
        print("=" * 70)
        
        return True

def main():
    """Fonction principale avec arguments en ligne de commande"""
    parser = argparse.ArgumentParser(
        description="SoccerSafe - Système d'analyse des blessures de football",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python start.py --setup          # Configuration complète
  python start.py --start          # Lancer l'app simple
  python start.py --start full     # Lancer l'app complète
  python start.py --test           # Tester uniquement le ML
        """
    )
    
    parser.add_argument("--setup", action="store_true", 
                       help="Configuration complète du projet")
    parser.add_argument("--install", action="store_true", 
                       help="Installer uniquement les dépendances")
    parser.add_argument("--test", action="store_true", 
                       help="Tester uniquement le système ML")
    parser.add_argument("--start", choices=["simple", "full"], nargs='?', const="simple",
                       help="Démarrer l'application (simple par défaut)")
    
    args = parser.parse_args()
    
    setup = SoccerSafeSetup()
    
    # Si aucun argument, faire le setup par défaut
    if not any(vars(args).values()):
        args.setup = True
        args.start = "simple"
    
    # Exécuter les actions demandées
    try:
        if args.setup:
            if setup.full_setup() and args.start:
                setup.launch_app(args.start)
        
        elif args.install:
            setup.print_header()
            setup.install_dependencies()
        
        elif args.test:
            setup.print_header()
            setup.test_ml_system()
        
        elif args.start:
            setup.print_header()
            # Vérifications rapides avant lancement
            if not setup.check_python_version():
                sys.exit(1)
            
            deps_ok, _ = setup.check_dependencies()
            if not deps_ok:
                print("❌ Dépendances manquantes. Lancez avec --install ou --setup")
                sys.exit(1)
            
            if not setup.check_data_files():
                print("❌ Fichiers de données manquants")
                sys.exit(1)
            
            setup.launch_app(args.start)
    
    except KeyboardInterrupt:
        print("\n👋 Opération annulée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()