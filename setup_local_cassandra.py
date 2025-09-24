#!/usr/bin/env python3
"""
Script de configuration locale pour Cassandra
Configuration et installation de Cassandra pour le développement local
"""

import os
import sys
import subprocess
import platform
import requests
import zipfile
import tempfile
from pathlib import Path

class CassandraLocalSetup:
    def __init__(self):
        self.system = platform.system().lower()
        self.cassandra_version = "4.1.10"
        self.cassandra_dir = Path.home() / "cassandra"
        
    def print_banner(self):
        print("🚀 Configuration locale de Cassandra")
        print("=" * 50)
        print(f"Système: {self.system}")
        print(f"Version Cassandra: {self.cassandra_version}")
        print(f"Répertoire: {self.cassandra_dir}")
        print()
        
    def check_java(self):
        """Vérifier si Java est installé"""
        print("☕ Vérification de Java...")
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Java est installé")
                return True
            else:
                print("❌ Java n'est pas installé")
                return False
        except FileNotFoundError:
            print("❌ Java n'est pas installé")
            return False
            
    def install_java_instructions(self):
        """Instructions d'installation de Java"""
        print("\n📋 Instructions d'installation de Java:")
        print("=" * 40)
        
        if self.system == "windows":
            print("1. Téléchargez OpenJDK 11 ou 17:")
            print("   https://adoptium.net/temurin/releases/")
            print("2. Installez et ajoutez JAVA_HOME aux variables d'environnement")
            print("3. Ajoutez %JAVA_HOME%\\bin au PATH")
        elif self.system == "darwin":  # macOS
            print("1. Installez avec Homebrew:")
            print("   brew install openjdk@11")
            print("2. Ou téléchargez depuis: https://adoptium.net/")
        else:  # Linux
            print("1. Ubuntu/Debian:")
            print("   sudo apt update && sudo apt install openjdk-11-jdk")
            print("2. CentOS/RHEL:")
            print("   sudo yum install java-11-openjdk-devel")
            
    def download_cassandra(self):
        """Télécharger Cassandra"""
        print(f"\n📥 Téléchargement de Cassandra {self.cassandra_version}...")
        
        url = f"https://downloads.apache.org/cassandra/{self.cassandra_version}/apache-cassandra-{self.cassandra_version}-bin.tar.gz"
        
        # Créer le répertoire parent
        self.cassandra_dir.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            print(f"URL: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Télécharger dans un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name
                
            print("✅ Téléchargement terminé")
            return tmp_path
            
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement: {e}")
            return None
            
    def extract_cassandra(self, archive_path):
        """Extraire Cassandra"""
        print("\n📂 Extraction de Cassandra...")
        
        try:
            import tarfile
            
            with tarfile.open(archive_path, 'r:gz') as tar:
                # Extraire dans le répertoire parent
                extract_dir = self.cassandra_dir.parent
                tar.extractall(path=extract_dir)
                
            # Renommer le répertoire extrait
            extracted_dir = extract_dir / f"apache-cassandra-{self.cassandra_version}"
            if extracted_dir.exists():
                if self.cassandra_dir.exists():
                    import shutil
                    shutil.rmtree(self.cassandra_dir)
                extracted_dir.rename(self.cassandra_dir)
                
            print("✅ Extraction terminée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'extraction: {e}")
            return False
            
    def configure_cassandra(self):
        """Configurer Cassandra pour le développement local"""
        print("\n⚙️ Configuration de Cassandra...")
        
        try:
            config_file = self.cassandra_dir / "conf" / "cassandra.yaml"
            
            if not config_file.exists():
                print(f"❌ Fichier de configuration non trouvé: {config_file}")
                return False
                
            # Lire la configuration actuelle
            with open(config_file, 'r') as f:
                config = f.read()
                
            # Remplacements pour le développement local
            replacements = {
                'cluster_name: \'Test Cluster\'': 'cluster_name: \'Football Analytics\'',
                'listen_address: localhost': 'listen_address: 127.0.0.1',
                'rpc_address: localhost': 'rpc_address: 127.0.0.1',
                'start_native_transport: true': 'start_native_transport: true',
                'native_transport_port: 9042': 'native_transport_port: 9042',
            }
            
            for old, new in replacements.items():
                config = config.replace(old, new)
                
            # Sauvegarder la configuration modifiée
            with open(config_file, 'w') as f:
                f.write(config)
                
            print("✅ Configuration terminée")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la configuration: {e}")
            return False
            
    def create_start_script(self):
        """Créer un script de démarrage"""
        print("\n📜 Création du script de démarrage...")
        
        if self.system == "windows":
            script_name = "start_cassandra.bat"
            script_content = f"""@echo off
echo Starting Cassandra...
cd /d "{self.cassandra_dir}"
bin\\cassandra.bat
"""
        else:
            script_name = "start_cassandra.sh"
            script_content = f"""#!/bin/bash
echo "Starting Cassandra..."
cd "{self.cassandra_dir}"
./bin/cassandra -f
"""
            
        script_path = Path(script_name)
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        if self.system != "windows":
            os.chmod(script_path, 0o755)
            
        print(f"✅ Script créé: {script_path.absolute()}")
        
    def create_env_file(self):
        """Créer un fichier .env pour le développement local"""
        print("\n📄 Création du fichier .env local...")
        
        env_content = f"""# Configuration Cassandra locale
CASSANDRA_HOSTS=127.0.0.1
CASSANDRA_PORT=9042
CASSANDRA_KEYSPACE=football_injuries
CASSANDRA_USERNAME=
CASSANDRA_PASSWORD=
CASSANDRA_DATACENTER=datacenter1

# APIs (à configurer)
API_FOOTBALL_KEY=your_api_key_here
WEATHER_API_KEY=your_weather_api_key

# Configuration app
DEBUG=True
LOG_LEVEL=INFO
"""
        
        with open('.env.local', 'w') as f:
            f.write(env_content)
            
        print("✅ Fichier .env.local créé")
        
    def show_next_steps(self):
        """Afficher les prochaines étapes"""
        print("\n🎉 Installation terminée!")
        print("=" * 30)
        print("\n📋 Prochaines étapes:")
        print("1. Démarrer Cassandra:")
        
        if self.system == "windows":
            print("   .\\start_cassandra.bat")
        else:
            print("   ./start_cassandra.sh")
            
        print("\n2. Dans un autre terminal, configurer la base de données:")
        print("   python scripts/setup_database.py")
        
        print("\n3. Importer les données:")
        print("   python scripts/import_data.py")
        
        print("\n4. Démarrer l'application:")
        print("   streamlit run webapp/app.py")
        
        print("\n🔧 Outils utiles:")
        print(f"   cqlsh (dans {self.cassandra_dir}/bin/)")
        print("   python scripts/cassandra_admin.py --info")
        
        print("\n📁 Répertoires importants:")
        print(f"   Cassandra: {self.cassandra_dir}")
        print(f"   Logs: {self.cassandra_dir}/logs/")
        print(f"   Données: {self.cassandra_dir}/data/")
        
    def run(self):
        """Exécuter l'installation complète"""
        self.print_banner()
        
        # Vérifier Java
        if not self.check_java():
            self.install_java_instructions()
            print("\n❌ Installez Java avant de continuer")
            return False
            
        # Vérifier si Cassandra est déjà installé
        if self.cassandra_dir.exists():
            response = input(f"\n⚠️  Cassandra semble déjà installé dans {self.cassandra_dir}\n"
                           "Voulez-vous le réinstaller? (y/N): ")
            if response.lower() != 'y':
                print("Installation annulée")
                return False
                
        # Télécharger et installer
        archive_path = self.download_cassandra()
        if not archive_path:
            return False
            
        if not self.extract_cassandra(archive_path):
            return False
            
        # Nettoyer le fichier temporaire
        os.unlink(archive_path)
        
        # Configurer
        if not self.configure_cassandra():
            return False
            
        # Créer les scripts
        self.create_start_script()
        self.create_env_file()
        
        # Instructions finales
        self.show_next_steps()
        
        return True

def main():
    """Point d'entrée principal"""
    setup = CassandraLocalSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Usage: python setup_local_cassandra.py")
        print("Installe et configure Cassandra pour le développement local")
        return
        
    try:
        setup.run()
    except KeyboardInterrupt:
        print("\n\n❌ Installation interrompue")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()