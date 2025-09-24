"""
Module d'analyse des données de blessures et génération de rapports
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class InjuryAnalyzer:
    """Analyseur de blessures de joueurs"""
    
    def __init__(self, injuries_df: pd.DataFrame, players_df: pd.DataFrame):
        self.injuries_df = injuries_df.copy()
        self.players_df = players_df.copy()
        self.merged_df = None
        self._prepare_data()
    
    def _prepare_data(self):
        """Préparer et nettoyer les données"""
        # Conversion des dates
        self.injuries_df['from_date'] = pd.to_datetime(self.injuries_df['from_date'])
        self.injuries_df['end_date'] = pd.to_datetime(self.injuries_df['end_date'])
        self.players_df['date_of_birth'] = pd.to_datetime(self.players_df['date_of_birth'])
        
        # Calculer l'âge des joueurs
        current_date = pd.Timestamp.now()
        self.players_df['age'] = (current_date - self.players_df['date_of_birth']).dt.days / 365.25
        
        # Fusionner les données
        self.merged_df = self.injuries_df.merge(
            self.players_df[['player_id', 'player_name', 'main_position', 'age', 'height', 'current_club_name']],
            on='player_id',
            how='left'
        )
        
        # Catégoriser les blessures
        self.merged_df['injury_category'] = self._categorize_injuries(self.merged_df['injury_reason'])
        
        # Calculer la sévérité
        self.merged_df['severity'] = self._calculate_severity(self.merged_df['days_missed'])
        
        # Extraire l'année et le mois
        self.merged_df['injury_year'] = self.merged_df['from_date'].dt.year
        self.merged_df['injury_month'] = self.merged_df['from_date'].dt.month
        
        print(f"✅ Données préparées: {len(self.merged_df)} blessures analysées")
    
    def _categorize_injuries(self, injury_reasons):
        """Catégoriser les types de blessures"""
        categories = []
        for reason in injury_reasons:
            reason_lower = str(reason).lower()
            if any(word in reason_lower for word in ['muscle', 'muscular', 'hamstring', 'thigh', 'calf']):
                categories.append('Musculaire')
            elif any(word in reason_lower for word in ['knee', 'ankle', 'foot', 'leg']):
                categories.append('Membres inférieurs')
            elif any(word in reason_lower for word in ['back', 'spine', 'lumbago']):
                categories.append('Dos')
            elif any(word in reason_lower for word in ['head', 'concussion', 'brain']):
                categories.append('Tête')
            elif any(word in reason_lower for word in ['shoulder', 'arm', 'hand', 'wrist']):
                categories.append('Membres supérieurs')
            else:
                categories.append('Autre')
        return categories
    
    def _calculate_severity(self, days_missed):
        """Calculer la sévérité des blessures"""
        severity = []
        for days in days_missed:
            if pd.isna(days) or days <= 0:
                severity.append('Inconnue')
            elif days <= 7:
                severity.append('Légère')
            elif days <= 21:
                severity.append('Modérée')
            elif days <= 60:
                severity.append('Grave')
            else:
                severity.append('Très grave')
        return severity
    
    def generate_injury_statistics(self):
        """Générer des statistiques générales sur les blessures"""
        stats = {
            'total_injuries': len(self.merged_df),
            'unique_players': self.merged_df['player_id'].nunique(),
            'avg_days_missed': self.merged_df['days_missed'].mean(),
            'most_common_injury': self.merged_df['injury_category'].mode().iloc[0],
            'most_affected_position': self.merged_df['main_position'].mode().iloc[0],
            'injuries_by_category': self.merged_df['injury_category'].value_counts().to_dict(),
            'injuries_by_severity': self.merged_df['severity'].value_counts().to_dict(),
            'injuries_by_position': self.merged_df['main_position'].value_counts().head(10).to_dict()
        }
        return stats
    
    def plot_injury_trends(self):
        """Graphique des tendances de blessures dans le temps"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Blessures par année', 'Blessures par mois', 
                          'Répartition par catégorie', 'Sévérité des blessures'),
            specs=[[{'type': 'scatter'}, {'type': 'bar'}],
                   [{'type': 'pie'}, {'type': 'bar'}]]
        )
        
        # Tendance annuelle
        yearly_trend = self.merged_df.groupby('injury_year').size()
        fig.add_trace(
            go.Scatter(x=yearly_trend.index, y=yearly_trend.values, 
                      mode='lines+markers', name='Blessures/an'),
            row=1, col=1
        )
        
        # Tendance mensuelle
        monthly_trend = self.merged_df.groupby('injury_month').size()
        fig.add_trace(
            go.Bar(x=monthly_trend.index, y=monthly_trend.values, name='Blessures/mois'),
            row=1, col=2
        )
        
        # Répartition par catégorie
        category_counts = self.merged_df['injury_category'].value_counts()
        fig.add_trace(
            go.Pie(labels=category_counts.index, values=category_counts.values, name='Catégories'),
            row=2, col=1
        )
        
        # Sévérité
        severity_counts = self.merged_df['severity'].value_counts()
        fig.add_trace(
            go.Bar(x=severity_counts.index, y=severity_counts.values, name='Sévérité'),
            row=2, col=2
        )
        
        fig.update_layout(height=800, title_text="Analyse des Tendances de Blessures")
        return fig
    
    def plot_position_analysis(self):
        """Analyse des blessures par position"""
        position_stats = self.merged_df.groupby('main_position').agg({
            'player_id': 'count',
            'days_missed': 'mean',
            'games_missed': 'mean'
        }).round(2)
        
        position_stats.columns = ['Nombre_blessures', 'Jours_moyens_manqués', 'Matchs_moyens_manqués']
        position_stats = position_stats.sort_values('Nombre_blessures', ascending=False).head(10)
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Nombre de blessures', 'Jours moyens manqués', 'Matchs moyens manqués')
        )
        
        # Nombre de blessures
        fig.add_trace(
            go.Bar(x=position_stats.index, y=position_stats['Nombre_blessures'], 
                   name='Blessures', marker_color='lightcoral'),
            row=1, col=1
        )
        
        # Jours manqués
        fig.add_trace(
            go.Bar(x=position_stats.index, y=position_stats['Jours_moyens_manqués'], 
                   name='Jours', marker_color='lightblue'),
            row=1, col=2
        )
        
        # Matchs manqués
        fig.add_trace(
            go.Bar(x=position_stats.index, y=position_stats['Matchs_moyens_manqués'], 
                   name='Matchs', marker_color='lightgreen'),
            row=1, col=3
        )
        
        fig.update_layout(height=500, title_text="Analyse des Blessures par Position")
        fig.update_xaxes(tickangle=45)
        return fig
    
    def plot_age_injury_correlation(self):
        """Corrélation entre âge et blessures"""
        # Filtrer les données avec âge valide
        valid_age_df = self.merged_df.dropna(subset=['age'])
        
        fig = px.scatter(
            valid_age_df, 
            x='age', 
            y='days_missed',
            color='injury_category',
            size='games_missed',
            hover_data=['player_name', 'main_position'],
            title='Corrélation Âge vs Gravité des Blessures',
            labels={'age': 'Âge du joueur', 'days_missed': 'Jours manqués'}
        )
        
        # Ajouter une ligne de tendance
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            valid_age_df['age'].dropna(), 
            valid_age_df['days_missed'].dropna()
        )
        
        line_x = np.linspace(valid_age_df['age'].min(), valid_age_df['age'].max(), 100)
        line_y = slope * line_x + intercept
        
        fig.add_trace(go.Scatter(
            x=line_x, 
            y=line_y,
            mode='lines',
            name=f'Tendance (R²={r_value**2:.3f})',
            line=dict(color='red', dash='dash')
        ))
        
        return fig
    
    def predict_injury_risk(self):
        """Modèle de prédiction du risque de blessure"""
        # Préparer les données pour le ML
        ml_df = self.merged_df.dropna(subset=['age', 'height', 'main_position']).copy()
        
        # Encoder les variables catégorielles
        le_position = LabelEncoder()
        ml_df['position_encoded'] = le_position.fit_transform(ml_df['main_position'])
        
        le_category = LabelEncoder()
        ml_df['category_encoded'] = le_category.fit_transform(ml_df['injury_category'])
        
        # Variables prédictives
        features = ['age', 'height', 'position_encoded', 'injury_month']
        X = ml_df[features]
        
        # Variable cible (blessure grave ou non)
        y = (ml_df['days_missed'] > 21).astype(int)  # 1 si blessure grave (>21 jours)
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Entraînement du modèle
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Prédictions
        y_pred = model.predict(X_test)
        
        # Importance des features
        feature_importance = pd.DataFrame({
            'feature': features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Rapport de classification
        report = classification_report(y_test, y_pred, output_dict=True)
        
        return {
            'model': model,
            'feature_importance': feature_importance,
            'classification_report': report,
            'accuracy': model.score(X_test, y_test),
            'label_encoders': {'position': le_position, 'category': le_category}
        }
    
    def generate_player_risk_profile(self, player_id: int):
        """Générer un profil de risque pour un joueur spécifique"""
        player_injuries = self.merged_df[self.merged_df['player_id'] == player_id]
        
        if player_injuries.empty:
            return {"error": "Aucune blessure trouvée pour ce joueur"}
        
        player_info = player_injuries.iloc[0]
        
        profile = {
            'player_name': player_info['player_name'],
            'position': player_info['main_position'],
            'age': player_info['age'],
            'total_injuries': len(player_injuries),
            'total_days_missed': player_injuries['days_missed'].sum(),
            'avg_days_per_injury': player_injuries['days_missed'].mean(),
            'most_common_injury': player_injuries['injury_category'].mode().iloc[0] if not player_injuries['injury_category'].mode().empty else 'N/A',
            'injury_frequency': len(player_injuries) / max(1, player_injuries['injury_year'].nunique()),
            'recent_injury': player_injuries['from_date'].max(),
            'injury_timeline': player_injuries[['from_date', 'injury_reason', 'days_missed']].to_dict('records')
        }
        
        return profile
    
    def export_analysis_report(self, output_path: str = "analysis_report.html"):
        """Exporter un rapport d'analyse complet en HTML"""
        stats = self.generate_injury_statistics()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rapport d'Analyse des Blessures</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #2E8B57; color: white; padding: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #2E8B57; }}
                .stat {{ display: inline-block; margin: 10px; padding: 10px; background-color: #f0f0f0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 Rapport d'Analyse des Blessures de Joueurs</h1>
                <p>Généré le {pd.Timestamp.now().strftime('%d/%m/%Y à %H:%M')}</p>
            </div>
            
            <div class="section">
                <h2>📊 Statistiques Générales</h2>
                <div class="stat"><strong>Total blessures:</strong> {stats['total_injuries']}</div>
                <div class="stat"><strong>Joueurs concernés:</strong> {stats['unique_players']}</div>
                <div class="stat"><strong>Durée moyenne:</strong> {stats['avg_days_missed']:.1f} jours</div>
                <div class="stat"><strong>Blessure la plus courante:</strong> {stats['most_common_injury']}</div>
                <div class="stat"><strong>Position la plus touchée:</strong> {stats['most_affected_position']}</div>
            </div>
            
            <div class="section">
                <h2>🎯 Recommandations</h2>
                <ul>
                    <li><strong>Prévention ciblée:</strong> Focus sur les blessures {stats['most_common_injury'].lower()}</li>
                    <li><strong>Surveillance renforcée:</strong> Joueurs en position {stats['most_affected_position']}</li>
                    <li><strong>Programme de récupération:</strong> Optimiser la durée moyenne de récupération</li>
                    <li><strong>Analyse prédictive:</strong> Utiliser le modèle ML pour identifier les joueurs à risque</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>📈 Indicateurs Clés de Performance (KPI)</h2>
                <ul>
                    <li>Taux de blessure grave: {(self.merged_df['severity'] == 'Grave').sum() / len(self.merged_df) * 100:.1f}%</li>
                    <li>Efficacité de récupération: {(self.merged_df['days_missed'] <= 14).sum() / len(self.merged_df) * 100:.1f}% de récupération rapide</li>
                    <li>Impact sur les matchs: {self.merged_df['games_missed'].sum()} matchs manqués au total</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Rapport exporté: {output_path}")
        return output_path

if __name__ == "__main__":
    # Test avec des données d'exemple
    print("🔬 Module d'analyse des blessures prêt")
    print("Utilisez la classe InjuryAnalyzer avec vos DataFrames pour commencer l'analyse")