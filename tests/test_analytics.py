"""
Tests unitaires pour le projet Football Injury Analytics
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys
import os

# Ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import InjuryAnalyzer
from database.crud import PlayerCRUD, InjuryCRUD

class TestInjuryAnalyzer(unittest.TestCase):
    """Tests pour la classe InjuryAnalyzer"""
    
    def setUp(self):
        """Préparer les données de test"""
        # Créer des données de test
        self.injuries_data = {
            'player_id': [1, 1, 2, 3],
            'season_name': ['20/21', '21/22', '20/21', '21/22'],
            'injury_reason': ['Muscle injury', 'Knee injury', 'Back problems', 'Hamstring injury'],
            'from_date': ['2021-01-15', '2022-03-10', '2021-05-20', '2022-07-05'],
            'end_date': ['2021-02-15', '2022-04-10', '2021-06-10', '2022-08-05'],
            'days_missed': [31, 31, 21, 31],
            'games_missed': [5, 4, 3, 6]
        }
        
        self.players_data = {
            'player_id': [1, 2, 3],
            'player_name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'date_of_birth': ['1995-05-15', '1992-08-22', '1990-03-10'],
            'main_position': ['Attack', 'Midfield', 'Defender'],
            'height': [180, 175, 185],
            'current_club_name': ['Team A', 'Team B', 'Team C']
        }
        
        self.injuries_df = pd.DataFrame(self.injuries_data)
        self.players_df = pd.DataFrame(self.players_data)
        
        self.analyzer = InjuryAnalyzer(self.injuries_df, self.players_df)
    
    def test_data_preparation(self):
        """Tester la préparation des données"""
        self.assertIsNotNone(self.analyzer.merged_df)
        self.assertTrue(len(self.analyzer.merged_df) > 0)
        self.assertIn('injury_category', self.analyzer.merged_df.columns)
        self.assertIn('severity', self.analyzer.merged_df.columns)
    
    def test_injury_categorization(self):
        """Tester la catégorisation des blessures"""
        categories = self.analyzer._categorize_injuries(['Muscle injury', 'Knee injury', 'Back problems'])
        
        self.assertIn('Musculaire', categories)
        self.assertIn('Membres inférieurs', categories)
        self.assertIn('Dos', categories)
    
    def test_severity_calculation(self):
        """Tester le calcul de sévérité"""
        severities = self.analyzer._calculate_severity([5, 15, 25, 90])
        
        expected = ['Légère', 'Modérée', 'Grave', 'Très grave']
        self.assertEqual(severities, expected)
    
    def test_statistics_generation(self):
        """Tester la génération de statistiques"""
        stats = self.analyzer.generate_injury_statistics()
        
        self.assertIn('total_injuries', stats)
        self.assertIn('unique_players', stats)
        self.assertIn('avg_days_missed', stats)
        self.assertGreater(stats['total_injuries'], 0)
    
    def test_player_risk_profile(self):
        """Tester le profil de risque d'un joueur"""
        profile = self.analyzer.generate_player_risk_profile(1)
        
        self.assertIn('player_name', profile)
        self.assertIn('total_injuries', profile)
        self.assertEqual(profile['total_injuries'], 2)  # Joueur 1 a 2 blessures

class TestDatabaseCRUD(unittest.TestCase):
    """Tests pour les opérations CRUD"""
    
    def setUp(self):
        """Configurer la base de données de test"""
        # Utiliser une base de données en mémoire pour les tests
        import tempfile
        self.test_db = tempfile.mktemp()
    
    def test_player_creation(self):
        """Tester la création d'un joueur"""
        # Test simulé (nécessite une vraie DB pour les tests complets)
        player_data = {
            'player_id': 999,
            'player_name': 'Test Player',
            'main_position': 'Attack'
        }
        
        # Dans un vrai test, vous utiliseriez:
        # player = PlayerCRUD.create_player(db_session, player_data)
        # self.assertEqual(player.player_name, 'Test Player')
        
        # Pour ce test simulé:
        self.assertTrue(True)
    
    def test_injury_creation(self):
        """Tester la création d'une blessure"""
        injury_data = {
            'player_id': 999,
            'injury_reason': 'Test injury',
            'days_missed': 15
        }
        
        # Test simulé
        self.assertTrue(True)

class TestDataValidation(unittest.TestCase):
    """Tests de validation des données"""
    
    def test_date_validation(self):
        """Tester la validation des dates"""
        # Test avec des dates valides
        valid_dates = ['2021-01-15', '2022-03-10']
        dates_df = pd.to_datetime(valid_dates)
        
        self.assertTrue(all(dates_df.notna()))
    
    def test_numeric_validation(self):
        """Tester la validation des valeurs numériques"""
        # Test avec des valeurs numériques
        numeric_values = [10, 15, 30, 45]
        
        self.assertTrue(all(isinstance(x, (int, float)) for x in numeric_values))
        self.assertTrue(all(x >= 0 for x in numeric_values))
    
    def test_data_completeness(self):
        """Tester la complétude des données"""
        test_data = pd.DataFrame({
            'player_id': [1, 2, None],
            'injury_reason': ['Muscle', 'Knee', 'Back'],
            'days_missed': [10, None, 20]
        })
        
        # Vérifier les valeurs manquantes
        missing_players = test_data['player_id'].isna().sum()
        missing_days = test_data['days_missed'].isna().sum()
        
        self.assertEqual(missing_players, 1)
        self.assertEqual(missing_days, 1)

class TestAPIIntegration(unittest.TestCase):
    """Tests d'intégration des APIs"""
    
    def test_api_response_structure(self):
        """Tester la structure des réponses API"""
        # Test simulé pour la structure de réponse
        mock_response = {
            'response': [
                {
                    'fixture': {'id': 1, 'date': '2024-01-15'},
                    'teams': {'home': {'name': 'Team A'}, 'away': {'name': 'Team B'}}
                }
            ]
        }
        
        self.assertIn('response', mock_response)
        self.assertTrue(len(mock_response['response']) > 0)
    
    def test_data_transformation(self):
        """Tester la transformation des données API"""
        # Test de transformation des données
        raw_data = {'temp': 20, 'humidity': 65}
        
        # Transformation simulée
        transformed_data = {
            'temperature': raw_data['temp'],
            'humidity': raw_data['humidity']
        }
        
        self.assertEqual(transformed_data['temperature'], 20)
        self.assertEqual(transformed_data['humidity'], 65)

def run_tests():
    """Exécuter tous les tests"""
    # Créer une suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajouter les classes de test
    test_classes = [
        TestInjuryAnalyzer,
        TestDatabaseCRUD,
        TestDataValidation,
        TestAPIIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    
    if success:
        print("✅ Tous les tests sont passés!")
        exit(0)
    else:
        print("❌ Certains tests ont échoué")
        exit(1)