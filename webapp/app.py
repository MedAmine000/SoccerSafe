"""
Application Web Streamlit pour l'analyse des blessures de joueurs
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import InjuryAnalyzer
from src.ml_predictor import InjuryPredictor
from src.data_collector import DataCollector
from database.models import get_cassandra_session
from database.crud import PlayerCRUD, InjuryCRUD

# Configuration de la page
st.set_page_config(
    page_title="⚽ Football Injury Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E8B57, #3CB371);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2E8B57;
    }
    
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Charger les données avec mise en cache"""
    try:
        # Charger les CSV existants
        injuries_df = pd.read_csv("player_injuries.csv")
        players_df = pd.read_csv("player_profiles.csv")
        
        return injuries_df, players_df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame(), pd.DataFrame()

def main():
    """Fonction principale de l'application"""
    
    # En-tête principal
    st.markdown("""
    <div class="main-header">
        <h1>⚽ Football Injury Analytics Dashboard</h1>
        <p>Analyse prédictive des blessures et optimisation de la performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar pour la navigation
    st.sidebar.title("🎛️ Navigation")
    page = st.sidebar.selectbox(
        "Choisir une page",
        ["📊 Vue d'ensemble", "🔍 Analyse détaillée", "🤖 Prédictions ML", "👤 Profil joueur", "📈 Données temps réel"]
    )
    
    # Chargement des données
    with st.spinner("Chargement des données..."):
        injuries_df, players_df = load_data()
    
    if injuries_df.empty or players_df.empty:
        st.error("❌ Impossible de charger les données. Vérifiez que les fichiers CSV sont présents.")
        return
    
    # Initialiser l'analyseur
    analyzer = InjuryAnalyzer(injuries_df, players_df)
    
    # Navigation entre les pages
    if page == "📊 Vue d'ensemble":
        show_overview(analyzer)
    elif page == "🔍 Analyse détaillée":
        show_detailed_analysis(analyzer)
    elif page == "🤖 Prédictions ML":
        show_ml_predictions(analyzer)
    elif page == "👤 Profil joueur":
        show_player_profile(analyzer)
    elif page == "📈 Données temps réel":
        show_realtime_data()

def show_overview(analyzer):
    """Afficher la vue d'ensemble"""
    st.header("📊 Vue d'ensemble des blessures")
    
    # Statistiques générales
    stats = analyzer.generate_injury_statistics()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏥 Total blessures",
            value=f"{stats['total_injuries']:,}",
            delta="Depuis le début des enregistrements"
        )
    
    with col2:
        st.metric(
            label="👤 Joueurs concernés",
            value=f"{stats['unique_players']:,}",
            delta=f"{(stats['unique_players']/stats['total_injuries']*100):.1f}% du total"
        )
    
    with col3:
        st.metric(
            label="⏱️ Durée moyenne",
            value=f"{stats['avg_days_missed']:.1f} jours",
            delta="Par blessure"
        )
    
    with col4:
        st.metric(
            label="🎯 Blessure courante",
            value=stats['most_common_injury'],
            delta="Type le plus fréquent"
        )
    
    # Graphiques de tendances
    st.subheader("📈 Tendances et répartitions")
    
    # Graphique des tendances
    trends_fig = analyzer.plot_injury_trends()
    st.plotly_chart(trends_fig, use_container_width=True)
    
    # Analyse par position
    st.subheader("⚽ Analyse par position")
    position_fig = analyzer.plot_position_analysis()
    st.plotly_chart(position_fig, use_container_width=True)
    
    # Répartition des blessures
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔥 Top 10 - Types de blessures")
        category_counts = pd.Series(stats['injuries_by_category']).head(10)
        fig_category = px.bar(
            x=category_counts.values,
            y=category_counts.index,
            orientation='h',
            title="Répartition par catégorie",
            color=category_counts.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Niveau de sévérité")
        severity_counts = pd.Series(stats['injuries_by_severity'])
        fig_severity = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title="Répartition par sévérité",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_severity, use_container_width=True)

def show_detailed_analysis(analyzer):
    """Afficher l'analyse détaillée"""
    st.header("🔍 Analyse détaillée")
    
    # Filtres
    st.sidebar.subheader("🎛️ Filtres")
    
    # Sélection de la période
    years = analyzer.merged_df['injury_year'].dropna().unique()
    selected_years = st.sidebar.multiselect(
        "Années",
        options=sorted(years),
        default=sorted(years)[-3:] if len(years) >= 3 else sorted(years)
    )
    
    # Sélection des positions
    positions = analyzer.merged_df['main_position'].dropna().unique()
    selected_positions = st.sidebar.multiselect(
        "Positions",
        options=sorted(positions),
        default=[]
    )
    
    # Filtrer les données
    filtered_df = analyzer.merged_df.copy()
    if selected_years:
        filtered_df = filtered_df[filtered_df['injury_year'].isin(selected_years)]
    if selected_positions:
        filtered_df = filtered_df[filtered_df['main_position'].isin(selected_positions)]
    
    st.info(f"📊 {len(filtered_df)} blessures sélectionnées avec les filtres actuels")
    
    # Corrélation âge-blessures
    st.subheader("👴 Corrélation âge vs gravité des blessures")
    age_fig = analyzer.plot_age_injury_correlation()
    st.plotly_chart(age_fig, use_container_width=True)
    
    # Analyse saisonnière
    st.subheader("🗓️ Analyse saisonnière")
    monthly_data = filtered_df.groupby('injury_month').agg({
        'player_id': 'count',
        'days_missed': 'mean'
    }).round(2)
    
    fig_seasonal = go.Figure()
    fig_seasonal.add_trace(go.Bar(
        x=monthly_data.index,
        y=monthly_data['player_id'],
        name='Nombre de blessures',
        marker_color='lightblue'
    ))
    
    fig_seasonal.add_trace(go.Scatter(
        x=monthly_data.index,
        y=monthly_data['days_missed'],
        mode='lines+markers',
        name='Durée moyenne (jours)',
        yaxis='y2',
        line=dict(color='red', width=3)
    ))
    
    fig_seasonal.update_layout(
        title='Évolution mensuelle des blessures',
        xaxis_title='Mois',
        yaxis_title='Nombre de blessures',
        yaxis2=dict(
            title='Durée moyenne (jours)',
            overlaying='y',
            side='right'
        )
    )
    
    st.plotly_chart(fig_seasonal, use_container_width=True)
    
    # Heatmap des blessures par position et mois
    st.subheader("🔥 Heatmap: Blessures par position et mois")
    
    heatmap_data = filtered_df.pivot_table(
        values='player_id',
        index='main_position',
        columns='injury_month',
        aggfunc='count',
        fill_value=0
    )
    
    fig_heatmap = px.imshow(
        heatmap_data,
        title="Intensité des blessures par position et mois",
        color_continuous_scale='Reds',
        aspect='auto'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Tableau détaillé
    st.subheader("📋 Données détaillées")
    if st.checkbox("Afficher les données brutes"):
        st.dataframe(
            filtered_df[['player_name', 'main_position', 'injury_reason', 'from_date', 'days_missed', 'severity']],
            use_container_width=True
        )

def show_ml_predictions(analyzer):
    """Afficher les prédictions ML"""
    st.header("🤖 Prédictions et Machine Learning")
    
    with st.spinner("Entraînement du modèle de prédiction..."):
        ml_results = analyzer.predict_injury_risk()
    
    # Vérifier s'il y a une erreur
    if 'error' in ml_results:
        st.error(f"❌ Erreur ML: {ml_results['error']}")
        st.info("💡 Vérifiez que les données contiennent suffisamment d'informations pour l'entraînement")
        
        if 'available_data' in ml_results:
            st.warning(f"Données disponibles: {ml_results['available_data']} échantillons (minimum: 10)")
        
        return
    
    # Métriques du modèle
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🎯 Précision du modèle",
            value=f"{ml_results['accuracy']:.3f}",
            delta="Score de précision"
        )
    
    with col2:
        f1_score = ml_results['classification_report'].get('weighted avg', {}).get('f1-score', 0.0)
        st.metric(
            label="📊 F1-Score",
            value=f"{f1_score:.3f}",
            delta="Score pondéré"
        )
    
    with col3:
        recall_score = ml_results['classification_report'].get('weighted avg', {}).get('recall', 0.0)
        st.metric(
            label="🔍 Rappel",
            value=f"{recall_score:.3f}",
            delta="Score de rappel"
        )
    
    # Informations sur les données d'entraînement
    st.info(f"📊 Modèle entraîné sur {ml_results.get('training_data_size', 0)} échantillons, "
            f"testé sur {ml_results.get('test_data_size', 0)} échantillons")
    
    # Importance des features
    st.subheader("📊 Importance des facteurs prédictifs")
    
    feature_importance = ml_results['feature_importance']
    if not feature_importance.empty:
        fig_importance = px.bar(
            feature_importance,
            x='importance',
            y='feature',
            orientation='h',
            title="Facteurs les plus importants pour prédire les blessures graves",
            color='importance',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_importance, use_container_width=True)
    else:
        st.warning("Aucune donnée d'importance des features disponible")
    
    # Simulateur de risque
    st.subheader("🎮 Simulateur de risque de blessure")
    
    # Vérifier si le modèle existe et fonctionne
    if ml_results.get('model') is None:
        st.error("❌ Modèle non disponible pour les prédictions")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        age_input = st.slider("Âge du joueur", 16, 40, 25)
        # Adapter selon les features disponibles
        if 'height_normalized' in ml_results.get('features_used', []):
            height_input = st.slider("Taille (cm)", 150, 210, 180)
        else:
            height_input = None
    
    with col2:
        position_options = analyzer.merged_df['main_position'].dropna().unique()
        position_input = st.selectbox("Position", position_options)
        month_input = st.selectbox("Mois", list(range(1, 13)), index=0)
    
    if st.button("🔮 Prédire le risque"):
        try:
            # Encoder la position
            position_encoded = ml_results['label_encoders']['position'].transform([position_input])[0]
            
            # Préparer les features selon le modèle
            features_used = ml_results.get('features_used', [])
            feature_values = []
            
            # Construire le vecteur de features dans l'ordre correct
            for feature in features_used:
                if feature == 'age':
                    feature_values.append(age_input)
                elif feature == 'position_encoded':
                    feature_values.append(position_encoded)
                elif feature == 'injury_month':
                    feature_values.append(month_input)
                elif feature == 'height_normalized' and height_input:
                    feature_values.append(height_input)
                else:
                    feature_values.append(0)  # Valeur par défaut
            
            # Faire la prédiction
            prediction_input = [feature_values]
            risk_proba = ml_results['model'].predict_proba(prediction_input)[0]
            
            # Afficher le résultat
            if len(risk_proba) > 1:
                risk_percentage = risk_proba[1] * 100
                
                if risk_percentage > 70:
                    st.error(f"🚨 Risque élevé: {risk_percentage:.1f}% de chance de blessure grave")
                elif risk_percentage > 40:
                    st.warning(f"⚠️ Risque modéré: {risk_percentage:.1f}% de chance de blessure grave")
                else:
                    st.success(f"✅ Risque faible: {risk_percentage:.1f}% de chance de blessure grave")
                
                # Afficher les détails
                st.info(f"🔍 Détails: Probabilité sûr={risk_proba[0]*100:.1f}%, "
                       f"Probabilité blessure grave={risk_proba[1]*100:.1f}%")
            else:
                st.warning("⚠️ Prédiction non disponible - modèle mal entraîné")
                
        except Exception as e:
            st.error(f"❌ Erreur lors de la prédiction: {e}")
            st.info("💡 Vérifiez que le modèle est correctement entraîné et que les données sont valides")

def show_player_profile(analyzer):
    """Afficher le profil d'un joueur"""
    st.header("👤 Profil individuel de joueur")
    
    # Sélection du joueur
    players_list = analyzer.merged_df[['player_id', 'player_name']].drop_duplicates()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_player_name = st.selectbox(
            "Rechercher un joueur",
            options=players_list['player_name'].sort_values().unique()
        )
    
    # Obtenir l'ID du joueur sélectionné
    selected_player_id = players_list[players_list['player_name'] == selected_player_name]['player_id'].iloc[0]
    
    with col2:
        st.info(f"ID du joueur: {selected_player_id}")
    
    # Générer le profil
    if st.button("📋 Générer le profil"):
        profile = analyzer.generate_player_risk_profile(selected_player_id)
        
        if "error" in profile:
            st.error(profile["error"])
            return
        
        # Informations générales
        st.subheader(f"🏃‍♂️ {profile['player_name']}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Position", profile['position'])
        
        with col2:
            st.metric("Âge", f"{profile['age']:.1f} ans")
        
        with col3:
            st.metric("Total blessures", profile['total_injuries'])
        
        with col4:
            st.metric("Jours perdus", f"{profile['total_days_missed']:.0f}")
        
        # Métriques de risque
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Durée moyenne/blessure",
                f"{profile['avg_days_per_injury']:.1f} jours"
            )
        
        with col2:
            st.metric(
                "Fréquence annuelle",
                f"{profile['injury_frequency']:.1f} blessures/an"
            )
        
        with col3:
            st.metric(
                "Type dominant",
                profile['most_common_injury']
            )
        
        # Timeline des blessures
        st.subheader("📅 Historique des blessures")
        
        timeline_df = pd.DataFrame(profile['injury_timeline'])
        timeline_df['from_date'] = pd.to_datetime(timeline_df['from_date'])
        
        fig_timeline = px.scatter(
            timeline_df,
            x='from_date',
            y='days_missed',
            hover_data=['injury_reason'],
            title=f"Timeline des blessures - {profile['player_name']}",
            labels={'from_date': 'Date de blessure', 'days_missed': 'Jours manqués'}
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Recommandations personnalisées
        st.subheader("💡 Recommandations personnalisées")
        
        recommendations = []
        
        if profile['injury_frequency'] > 3:
            recommendations.append("🚨 Fréquence élevée - Surveillance médicale renforcée recommandée")
        
        if profile['avg_days_per_injury'] > 30:
            recommendations.append("⏰ Temps de récupération long - Révision du protocole de soin")
        
        if profile['most_common_injury'] == 'Musculaire':
            recommendations.append("💪 Focus sur la préparation physique et l'échauffement")
        
        if not recommendations:
            recommendations.append("✅ Profil de risque dans la normale")
        
        for rec in recommendations:
            st.info(rec)

def show_realtime_data():
    """Afficher les données temps réel"""
    st.header("📈 Données en temps réel")
    
    st.info("🔄 Cette section simule la collecte de données temps réel via les APIs")
    
    # Simuler la collecte de données
    collector = DataCollector()
    
    if st.button("🔄 Actualiser les données"):
        with st.spinner("Collecte des données en cours..."):
            try:
                # Simuler la collecte (remplacez par de vraies données API)
                st.success("✅ Données actualisées avec succès!")
                
                # Afficher des métriques en temps réel (simulées)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Matchs cette semaine",
                        "12",
                        delta="3"
                    )
                
                with col2:
                    st.metric(
                        "Nouvelles blessures",
                        "2",
                        delta="-1"
                    )
                
                with col3:
                    st.metric(
                        "Retours de blessure",
                        "5",
                        delta="2"
                    )
                
                # Graphique temps réel simulé
                dates = pd.date_range(
                    start=datetime.now() - timedelta(days=7),
                    end=datetime.now(),
                    freq='D'
                )
                
                simulated_data = pd.DataFrame({
                    'date': dates,
                    'new_injuries': np.random.poisson(2, len(dates)),
                    'recoveries': np.random.poisson(3, len(dates))
                })
                
                fig_realtime = go.Figure()
                fig_realtime.add_trace(go.Scatter(
                    x=simulated_data['date'],
                    y=simulated_data['new_injuries'],
                    mode='lines+markers',
                    name='Nouvelles blessures',
                    line=dict(color='red')
                ))
                
                fig_realtime.add_trace(go.Scatter(
                    x=simulated_data['date'],
                    y=simulated_data['recoveries'],
                    mode='lines+markers',
                    name='Retours de blessure',
                    line=dict(color='green')
                ))
                
                fig_realtime.update_layout(
                    title='Évolution des 7 derniers jours',
                    xaxis_title='Date',
                    yaxis_title='Nombre'
                )
                
                st.plotly_chart(fig_realtime, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la collecte: {e}")
    
    # Configuration des alertes
    st.subheader("🚨 Configuration des alertes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Alerte blessure grave (>30 jours)", value=True)
        st.checkbox("Alerte fréquence élevée", value=True)
    
    with col2:
        st.checkbox("Alerte retour de blessure", value=False)
        st.checkbox("Alerte tendance mensuelle", value=True)
    
    # Planification des mises à jour
    st.subheader("⏰ Planification automatique")
    
    update_frequency = st.selectbox(
        "Fréquence de mise à jour",
        ["Temps réel", "Toutes les heures", "Quotidien", "Hebdomadaire"]
    )
    
    if st.button("💾 Sauvegarder la configuration"):
        st.success("Configuration sauvegardée!")

if __name__ == "__main__":
    main()