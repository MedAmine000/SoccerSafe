"""
Module de prédiction ML spécialisé pour les blessures de football
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import warnings
warnings.filterwarnings('ignore')

class InjuryPredictor:
    """Prédicteur de blessures basé sur Random Forest"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, injuries_df, players_df):
        """Préparer les features pour l'entraînement"""
        try:
            # Fusion des données
            merged_df = injuries_df.merge(
                players_df[['player_id', 'player_name', 'main_position', 'date_of_birth', 'height']],
                on='player_id',
                how='left'
            )
            
            # Calculer l'âge
            merged_df['from_date'] = pd.to_datetime(merged_df['from_date'])
            merged_df['date_of_birth'] = pd.to_datetime(merged_df['date_of_birth'])
            merged_df['age_at_injury'] = (merged_df['from_date'] - merged_df['date_of_birth']).dt.days / 365.25
            
            # Extraire des features temporelles
            merged_df['injury_month'] = merged_df['from_date'].dt.month
            merged_df['injury_day_of_year'] = merged_df['from_date'].dt.dayofyear
            
            # Nettoyer les données
            clean_df = merged_df.dropna(subset=['age_at_injury', 'main_position', 'days_missed']).copy()
            
            print(f"📊 Données après nettoyage: {len(clean_df)} blessures")
            
            if len(clean_df) < 50:
                raise ValueError("Données insuffisantes pour l'entraînement ML (minimum: 50)")
            
            # Encoder les variables catégorielles
            position_encoder = LabelEncoder()
            clean_df['position_encoded'] = position_encoder.fit_transform(clean_df['main_position'])
            self.label_encoders['position'] = position_encoder
            
            # Encoder les types de blessures pour features additionnelles
            injury_encoder = LabelEncoder()
            clean_df['injury_type_encoded'] = injury_encoder.fit_transform(clean_df['injury_reason'])
            self.label_encoders['injury_type'] = injury_encoder
            
            # Créer des features dérivées
            clean_df['height_normalized'] = clean_df['height'].fillna(clean_df['height'].mean())
            clean_df['is_young'] = (clean_df['age_at_injury'] < 25).astype(int)
            clean_df['is_old'] = (clean_df['age_at_injury'] > 30).astype(int)
            clean_df['winter_season'] = clean_df['injury_month'].isin([12, 1, 2]).astype(int)
            
            # Features finales
            self.feature_names = [
                'age_at_injury', 'height_normalized', 'position_encoded', 
                'injury_month', 'is_young', 'is_old', 'winter_season'
            ]
            
            X = clean_df[self.feature_names]
            
            # Variable cible: blessure grave (>21 jours)
            y = (clean_df['days_missed'] > 21).astype(int)
            
            print(f"🎯 Features: {self.feature_names}")
            print(f"📈 Distribution cible: {y.value_counts().to_dict()}")
            
            return X, y, clean_df
            
        except Exception as e:
            print(f"❌ Erreur préparation features: {e}")
            raise
    
    def train(self, injuries_df, players_df, test_size=0.3):
        """Entraîner le modèle prédictif"""
        try:
            # Préparer les données
            X, y, data_info = self.prepare_features(injuries_df, players_df)
            
            # Division train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # Normalisation des features numériques
            numeric_features = ['age_at_injury', 'height_normalized', 'injury_month']
            X_train_scaled = X_train.copy()
            X_test_scaled = X_test.copy()
            
            X_train_scaled[numeric_features] = self.scaler.fit_transform(X_train[numeric_features])
            X_test_scaled[numeric_features] = self.scaler.transform(X_test[numeric_features])
            
            # Entraînement du modèle
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Évaluation
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
            
            # Métriques
            accuracy = self.model.score(X_test_scaled, y_test)
            
            try:
                auc_score = roc_auc_score(y_test, y_pred_proba)
            except:
                auc_score = 0.5
            
            # Validation croisée
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Rapport détaillé
            report = classification_report(y_test, y_pred, output_dict=True)
            
            self.is_trained = True
            
            results = {
                'accuracy': accuracy,
                'auc_score': auc_score,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'feature_importance': feature_importance,
                'classification_report': report,
                'confusion_matrix': confusion_matrix(y_test, y_pred),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'model': self.model,
                'label_encoders': self.label_encoders
            }
            
            print(f"✅ Modèle entraîné - Précision: {accuracy:.3f}, AUC: {auc_score:.3f}")
            print(f"📊 Validation croisée: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
            
            return results
            
        except Exception as e:
            print(f"❌ Erreur entraînement: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def predict_risk(self, age, position, month, height=None, is_young=None, is_old=None):
        """Prédire le risque de blessure grave pour un joueur"""
        if not self.is_trained:
            raise ValueError("Le modèle n'est pas encore entraîné")
        
        try:
            # Préparer les features
            features = {}
            features['age_at_injury'] = age
            features['height_normalized'] = height if height else 180  # Valeur moyenne
            features['injury_month'] = month
            features['is_young'] = 1 if age < 25 else 0
            features['is_old'] = 1 if age > 30 else 0
            features['winter_season'] = 1 if month in [12, 1, 2] else 0
            
            # Encoder la position
            try:
                features['position_encoded'] = self.label_encoders['position'].transform([position])[0]
            except:
                # Position inconnue, utiliser la plus fréquente
                features['position_encoded'] = 0
            
            # Créer le vecteur de features
            feature_vector = np.array([[features[name] for name in self.feature_names]])
            
            # Normaliser les features numériques
            numeric_features = ['age_at_injury', 'height_normalized', 'injury_month']
            feature_vector_scaled = feature_vector.copy()
            
            numeric_indices = [i for i, name in enumerate(self.feature_names) if name in numeric_features]
            feature_vector_scaled[:, numeric_indices] = self.scaler.transform(
                feature_vector[:, numeric_indices]
            )
            
            # Prédiction
            risk_proba = self.model.predict_proba(feature_vector_scaled)[0]
            risk_class = self.model.predict(feature_vector_scaled)[0]
            
            return {
                'risk_probability': risk_proba[1] * 100,  # Probabilité de blessure grave
                'safe_probability': risk_proba[0] * 100,  # Probabilité de blessure légère
                'prediction': 'Grave' if risk_class == 1 else 'Légère',
                'confidence': max(risk_proba) * 100
            }
            
        except Exception as e:
            print(f"❌ Erreur prédiction: {e}")
            return {'error': str(e)}
    
    def save_model(self, filepath):
        """Sauvegarder le modèle entraîné"""
        if not self.is_trained:
            raise ValueError("Aucun modèle entraîné à sauvegarder")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        print(f"💾 Modèle sauvegardé: {filepath}")
    
    def load_model(self, filepath):
        """Charger un modèle pré-entraîné"""
        try:
            model_data = joblib.load(filepath)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.feature_names = model_data['feature_names']
            self.is_trained = model_data['is_trained']
            
            print(f"📂 Modèle chargé: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur chargement modèle: {e}")
            return False
    
    def get_model_info(self):
        """Informations sur le modèle"""
        if not self.is_trained:
            return {"status": "Non entraîné"}
        
        return {
            "status": "Entraîné",
            "features": self.feature_names,
            "positions_available": list(self.label_encoders['position'].classes_),
            "model_type": "Random Forest",
            "n_estimators": self.model.n_estimators
        }

def test_predictor():
    """Test rapide du prédicteur"""
    # Créer des données de test
    injuries_test = pd.DataFrame({
        'player_id': [1, 1, 2, 2, 3],
        'injury_reason': ['Muscle', 'Knee', 'Back', 'Ankle', 'Hamstring'],
        'from_date': ['2021-01-15', '2021-06-10', '2021-03-20', '2021-09-15', '2022-01-05'],
        'days_missed': [15, 35, 8, 45, 25],
        'games_missed': [2, 6, 1, 8, 4]
    })
    
    players_test = pd.DataFrame({
        'player_id': [1, 2, 3],
        'player_name': ['Test Player 1', 'Test Player 2', 'Test Player 3'],
        'main_position': ['Attack', 'Midfield', 'Defense'],
        'date_of_birth': ['1995-05-15', '1990-08-22', '1988-03-10'],
        'height': [180, 175, 185]
    })
    
    # Tester le prédicteur
    predictor = InjuryPredictor()
    results = predictor.train(injuries_test, players_test)
    
    if 'error' not in results:
        # Test de prédiction
        risk_result = predictor.predict_risk(
            age=25,
            position='Attack',
            month=12,
            height=180
        )
        
        print(f"🧪 Test prédiction: {risk_result}")
        return True
    else:
        print(f"❌ Erreur test: {results['error']}")
        return False

if __name__ == "__main__":
    print("🔬 Test du module prédicteur ML...")
    success = test_predictor()
    
    if success:
        print("✅ Module prédicteur fonctionnel!")
    else:
        print("❌ Problèmes détectés dans le module")