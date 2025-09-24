"""
Application Web Streamlit pour l'analyse des blessures de joueurs
Version simplifiée fonctionnant avec les CSV locaux
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

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
        # Charger les CSV existants depuis le dossier data
        injuries_df = pd.read_csv("data/player_injuries.csv")
        players_df = pd.read_csv("data/player_profiles.csv")
        
        return injuries_df, players_df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame(), pd.DataFrame()

def show_overview(injuries_df, players_df):
    """Afficher la vue d'ensemble"""
    st.header("📊 Vue d'ensemble des données")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total joueurs", f"{len(players_df):,}")
    
    with col2:
        st.metric("Total blessures", f"{len(injuries_df):,}")
    
    with col3:
        active_players = len(players_df[players_df['current_club'] != 'Retired'])
        st.metric("Joueurs actifs", f"{active_players:,}")
    
    with col4:
        if not injuries_df.empty and 'days_missed' in injuries_df.columns:
            avg_days = injuries_df['days_missed'].mean()
            st.metric("Moy. jours blessure", f"{avg_days:.1f}")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        if not players_df.empty and 'position' in players_df.columns:
            st.subheader("Distribution par position")
            position_counts = players_df['position'].value_counts().head(10)
            fig = px.bar(x=position_counts.values, y=position_counts.index, orientation='h')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not injuries_df.empty and 'injury_reason' in injuries_df.columns:
            st.subheader("Types de blessures les plus fréquents")
            injury_counts = injuries_df['injury_reason'].value_counts().head(10)
            fig = px.pie(values=injury_counts.values, names=injury_counts.index)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def show_detailed_analysis(injuries_df, players_df):
    """Afficher l'analyse détaillée"""
    st.header("🔍 Analyse détaillée")
    
    # Filtres
    col1, col2 = st.columns(2)
    
    with col1:
        if not players_df.empty and 'position' in players_df.columns:
            positions = ['Tous'] + list(players_df['position'].dropna().unique())
            selected_position = st.selectbox("Position", positions)
    
    with col2:
        if not injuries_df.empty and 'season_name' in injuries_df.columns:
            seasons = ['Toutes'] + list(injuries_df['season_name'].dropna().unique())
            selected_season = st.selectbox("Saison", seasons)
    
    # Filtrer les données
    filtered_injuries = injuries_df.copy()
    filtered_players = players_df.copy()
    
    if selected_position != 'Tous':
        player_ids = players_df[players_df['position'] == selected_position]['player_id'].values
        filtered_injuries = injuries_df[injuries_df['player_id'].isin(player_ids)]
    
    if selected_season != 'Toutes':
        filtered_injuries = filtered_injuries[filtered_injuries['season_name'] == selected_season]
    
    # Afficher les statistiques filtrées
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Blessures filtrées", f"{len(filtered_injuries):,}")
    
    with col2:
        if not filtered_injuries.empty and 'days_missed' in filtered_injuries.columns:
            avg_days = filtered_injuries['days_missed'].mean()
            st.metric("Moy. jours perdus", f"{avg_days:.1f}")
    
    with col3:
        if not filtered_injuries.empty and 'games_missed' in filtered_injuries.columns:
            avg_games = filtered_injuries['games_missed'].mean()
            st.metric("Moy. matchs ratés", f"{avg_games:.1f}")
    
    # Graphique temporel des blessures
    if not filtered_injuries.empty and 'from_date' in filtered_injuries.columns:
        st.subheader("Évolution temporelle des blessures")
        
        # Convertir les dates
        filtered_injuries['from_date'] = pd.to_datetime(filtered_injuries['from_date'], errors='coerce')
        injuries_by_month = filtered_injuries.groupby(filtered_injuries['from_date'].dt.to_period('M')).size()
        
        if not injuries_by_month.empty:
            fig = px.line(x=injuries_by_month.index.astype(str), y=injuries_by_month.values)
            fig.update_layout(xaxis_title="Mois", yaxis_title="Nombre de blessures")
            st.plotly_chart(fig, use_container_width=True)

def show_player_profile():
    """Afficher le profil d'un joueur"""
    st.header("👤 Profil joueur")
    
    # Chargement des données
    injuries_df, players_df = load_data()
    
    if players_df.empty:
        st.warning("Aucune donnée de joueur disponible")
        return
    
    # Trouver la colonne nom
    name_col = None
    for col in ['name', 'full_name', 'player_name', 'surname', 'nom']:
        if col in players_df.columns:
            name_col = col
            break
    
    if not name_col:
        st.warning("Aucune colonne nom trouvée dans les données")
        return
    
    # Sélection du joueur
    player_names = players_df[name_col].dropna().unique()
    selected_player = st.selectbox("Choisir un joueur", player_names)
    
    if selected_player:
        player_info = players_df[players_df[name_col] == selected_player].iloc[0]
        player_id = player_info['player_id']
        
        # Afficher info de base
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Nom:** {player_info[name_col]}")
            st.write(f"**Position:** {player_info.get('position', 'N/A')}")
        
        with col2:
            st.write(f"**Âge:** {player_info.get('age', 'N/A')}")
            st.write(f"**Club:** {player_info.get('current_club', 'N/A')}")
        
        with col3:
            # Chercher la colonne nationalité
            nationality_display = 'N/A'
            for col in ['nationality', 'country', 'nation', 'citizenship']:
                if col in player_info.index:
                    nationality_display = player_info.get(col, 'N/A')
                    break
            
            st.write(f"**Nationalité:** {nationality_display}")
            st.write(f"**Taille:** {player_info.get('height_cm', 'N/A')} cm")
        
        # Historique des blessures
        player_injuries = injuries_df[injuries_df['player_id'] == player_id]
        
        if not player_injuries.empty:
            st.subheader("Historique des blessures")
            st.dataframe(player_injuries[['season_name', 'injury_reason', 'from_date', 'end_date', 'days_missed', 'games_missed']])
            
            # Graphique des blessures
            if len(player_injuries) > 1:
                fig = px.bar(player_injuries, x='season_name', y='days_missed', 
                            title="Jours perdus par saison")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune blessure enregistrée pour ce joueur")

def show_advanced_search():
    """Afficher la page de recherche avancée"""
    st.header("🔎 Recherche avancée")
    
    # Chargement des données
    injuries_df, players_df = load_data()
    
    if injuries_df.empty or players_df.empty:
        st.warning("Aucune donnée disponible pour la recherche")
        return
    
    # Debug: Afficher les colonnes disponibles (temporaire)
    with st.expander("🔍 Colonnes disponibles (debug)", expanded=False):
        st.write("**Colonnes joueurs:**", list(players_df.columns))
        st.write("**Colonnes blessures:**", list(injuries_df.columns))
    
    # Interface de filtrage
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎛️ Filtres de recherche")
    
    # === FILTRES JOUEURS ===
    st.sidebar.markdown("### 👤 Filtres Joueurs")
    
    # Déterminer la colonne nom
    name_col = None
    for col in ['name', 'full_name', 'player_name', 'surname', 'nom']:
        if col in players_df.columns:
            name_col = col
            break
    
    # Filtre par nom de joueur
    player_name_search = st.sidebar.text_input("🔍 Nom du joueur", placeholder="Tapez un nom...")
    
    # Filtre par position
    positions = ['Tous'] + sorted(players_df['position'].dropna().unique().tolist())
    selected_positions = st.sidebar.multiselect("⚽ Position", positions, default=['Tous'])
    
    # Filtre par âge
    if 'age' in players_df.columns:
        age_range = st.sidebar.slider(
            "🎂 Tranche d'âge", 
            int(players_df['age'].min()), 
            int(players_df['age'].max()), 
            (int(players_df['age'].min()), int(players_df['age'].max()))
        )
    
    # Filtre par nationalité (vérifier si la colonne existe)
    nationality_col = None
    for col in ['nationality', 'country', 'nation', 'citizenship']:
        if col in players_df.columns:
            nationality_col = col
            break
    
    if nationality_col:
        nationalities = ['Toutes'] + sorted(players_df[nationality_col].dropna().unique().tolist()[:20])  # Top 20
        selected_nationality = st.sidebar.selectbox("🌍 Nationalité", nationalities)
    else:
        selected_nationality = 'Toutes'
    
    # Filtre par club
    if 'current_club' in players_df.columns:
        clubs = ['Tous'] + sorted(players_df['current_club'].dropna().unique().tolist()[:30])  # Top 30
        selected_club = st.sidebar.selectbox("🏟️ Club actuel", clubs)
    
    # === FILTRES BLESSURES ===
    st.sidebar.markdown("### 🚑 Filtres Blessures")
    
    # Filtre par type de blessure
    injury_types = ['Tous'] + sorted(injuries_df['injury_reason'].dropna().unique().tolist())
    selected_injury_types = st.sidebar.multiselect("🤕 Type de blessure", injury_types[:20], default=['Tous'])
    
    # Filtre par saison
    seasons = ['Toutes'] + sorted(injuries_df['season_name'].dropna().unique().tolist(), reverse=True)
    selected_seasons = st.sidebar.multiselect("📅 Saisons", seasons[:10], default=['Toutes'])
    
    # Filtre par durée de blessure
    if 'days_missed' in injuries_df.columns:
        days_range = st.sidebar.slider(
            "⏰ Jours d'absence (min-max)", 
            0, 
            int(injuries_df['days_missed'].max()), 
            (0, int(injuries_df['days_missed'].max()))
        )
    
    # Filtre par matchs ratés
    if 'games_missed' in injuries_df.columns:
        games_range = st.sidebar.slider(
            "🎮 Matchs ratés (min-max)", 
            0, 
            int(injuries_df['games_missed'].max()), 
            (0, int(injuries_df['games_missed'].max()))
        )
    
    # === FILTRES TEMPORELS ===
    st.sidebar.markdown("### 📆 Filtres Temporels")
    
    # Convertir les dates
    injuries_df['from_date'] = pd.to_datetime(injuries_df['from_date'], errors='coerce')
    injuries_df['end_date'] = pd.to_datetime(injuries_df['end_date'], errors='coerce')
    
    # Filtre par période
    if not injuries_df['from_date'].isna().all():
        min_date = injuries_df['from_date'].min().date()
        max_date = injuries_df['from_date'].max().date()
        
        date_range = st.sidebar.date_input(
            "📅 Période de blessure",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # === APPLICATION DES FILTRES ===
    
    # Filtrer les joueurs
    filtered_players = players_df.copy()
    
    # Filtre par nom
    if player_name_search and name_col:
        filtered_players = filtered_players[
            filtered_players[name_col].str.contains(player_name_search, case=False, na=False)
        ]
    
    # Filtre par position
    if 'Tous' not in selected_positions and selected_positions:
        filtered_players = filtered_players[filtered_players['position'].isin(selected_positions)]
    
    # Filtre par âge
    if 'age' in players_df.columns:
        filtered_players = filtered_players[
            (filtered_players['age'] >= age_range[0]) & 
            (filtered_players['age'] <= age_range[1])
        ]
    
    # Filtre par nationalité
    if nationality_col and selected_nationality != 'Toutes':
        filtered_players = filtered_players[filtered_players[nationality_col] == selected_nationality]
    
    # Filtre par club
    if 'current_club' in players_df.columns and selected_club != 'Tous':
        filtered_players = filtered_players[filtered_players['current_club'] == selected_club]
    
    # Obtenir les IDs des joueurs filtrés
    filtered_player_ids = filtered_players['player_id'].tolist()
    
    # Filtrer les blessures
    filtered_injuries = injuries_df[injuries_df['player_id'].isin(filtered_player_ids)].copy()
    
    # Filtre par type de blessure
    if 'Tous' not in selected_injury_types and selected_injury_types:
        filtered_injuries = filtered_injuries[filtered_injuries['injury_reason'].isin(selected_injury_types)]
    
    # Filtre par saison
    if 'Toutes' not in selected_seasons and selected_seasons:
        filtered_injuries = filtered_injuries[filtered_injuries['season_name'].isin(selected_seasons)]
    
    # Filtre par durée
    if 'days_missed' in injuries_df.columns:
        filtered_injuries = filtered_injuries[
            (filtered_injuries['days_missed'] >= days_range[0]) & 
            (filtered_injuries['days_missed'] <= days_range[1])
        ]
    
    # Filtre par matchs ratés
    if 'games_missed' in injuries_df.columns:
        filtered_injuries = filtered_injuries[
            (filtered_injuries['games_missed'] >= games_range[0]) & 
            (filtered_injuries['games_missed'] <= games_range[1])
        ]
    
    # Filtre par date
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_injuries = filtered_injuries[
            (filtered_injuries['from_date'].dt.date >= start_date) &
            (filtered_injuries['from_date'].dt.date <= end_date)
        ]
    
    # === AFFICHAGE DES RÉSULTATS ===
    
    # Statistiques des résultats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Joueurs trouvés", f"{len(filtered_players):,}")
    
    with col2:
        st.metric("🚑 Blessures trouvées", f"{len(filtered_injuries):,}")
    
    with col3:
        if not filtered_injuries.empty and 'days_missed' in filtered_injuries.columns:
            avg_days = filtered_injuries['days_missed'].mean()
            st.metric("📊 Moy. jours perdus", f"{avg_days:.1f}")
    
    with col4:
        if not filtered_injuries.empty and 'games_missed' in filtered_injuries.columns:
            avg_games = filtered_injuries['games_missed'].mean()
            st.metric("🎮 Moy. matchs ratés", f"{avg_games:.1f}")
    
    # Onglets pour les différentes vues
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Résultats", "📊 Analyses", "📈 Tendances", "📥 Export"])
    
    with tab1:
        st.subheader("📋 Résultats de la recherche")
        
        # Sélecteur de vue
        view_type = st.radio("Vue", ["Joueurs", "Blessures", "Combinée"], horizontal=True)
        
        if view_type == "Joueurs":
            if not filtered_players.empty:
                # Colonnes à afficher (avec vérification)
                base_cols = ['position', 'age', 'current_club', 'height_cm']
                display_cols = base_cols.copy()
                
                # Ajouter la colonne nom si elle existe
                if name_col:
                    display_cols.insert(0, name_col)
                
                # Ajouter la colonne nationalité si elle existe
                if nationality_col:
                    display_cols.insert(-2, nationality_col)
                
                available_cols = [col for col in display_cols if col in filtered_players.columns]
                
                st.dataframe(
                    filtered_players[available_cols].head(100),
                    use_container_width=True,
                    height=400
                )
                
                if len(filtered_players) > 100:
                    st.info(f"Affichage des 100 premiers résultats sur {len(filtered_players)} trouvés")
            else:
                st.warning("Aucun joueur ne correspond aux critères de recherche")
        
        elif view_type == "Blessures":
            if not filtered_injuries.empty:
                # Trouver la colonne nom du joueur
                name_col = None
                for col in ['name', 'full_name', 'player_name', 'surname', 'nom']:
                    if col in filtered_players.columns:
                        name_col = col
                        break
                
                if name_col:
                    # Jointure avec les noms des joueurs
                    injury_display = filtered_injuries.merge(
                        filtered_players[['player_id', name_col]], 
                        on='player_id', 
                        how='left'
                    )
                    injury_display = injury_display.rename(columns={name_col: 'name'})
                else:
                    injury_display = filtered_injuries.copy()
                    injury_display['name'] = 'Joueur ' + injury_display['player_id'].astype(str)
                
                # Colonnes à afficher
                display_cols = ['name', 'season_name', 'injury_reason', 'from_date', 'end_date', 'days_missed', 'games_missed']
                available_cols = [col for col in display_cols if col in injury_display.columns]
                
                st.dataframe(
                    injury_display[available_cols].head(100),
                    use_container_width=True,
                    height=400
                )
                
                if len(filtered_injuries) > 100:
                    st.info(f"Affichage des 100 premières blessures sur {len(filtered_injuries)} trouvées")
            else:
                st.warning("Aucune blessure ne correspond aux critères de recherche")
        
        else:  # Vue combinée
            if not filtered_players.empty and not filtered_injuries.empty:
                # Statistiques par joueur
                player_stats = filtered_injuries.groupby('player_id').agg({
                    'injury_reason': 'count',
                    'days_missed': ['sum', 'mean'],
                    'games_missed': ['sum', 'mean']
                }).round(1)
                
                player_stats.columns = ['Nb_blessures', 'Total_jours', 'Moy_jours', 'Total_matchs', 'Moy_matchs']
                player_stats = player_stats.reset_index()
                
                # Colonnes pour la jointure
                join_cols = ['player_id', 'position', 'age', 'current_club']
                if name_col:
                    join_cols.insert(1, name_col)
                available_join_cols = [col for col in join_cols if col in filtered_players.columns]
                
                # Jointure avec les infos joueurs
                combined_data = player_stats.merge(
                    filtered_players[available_join_cols], 
                    on='player_id', 
                    how='left'
                )
                
                # Colonnes d'affichage pour la vue combinée
                combined_display_cols = ['position', 'age', 'current_club', 'Nb_blessures', 'Total_jours', 'Moy_jours']
                if name_col and name_col in combined_data.columns:
                    combined_display_cols.insert(0, name_col)
                
                # Filtrer les colonnes existantes
                final_cols = [col for col in combined_display_cols if col in combined_data.columns]
                
                st.dataframe(
                    combined_data[final_cols].head(50),
                    use_container_width=True,
                    height=400
                )
    
    with tab2:
        st.subheader("📊 Analyses des résultats")
        
        if not filtered_injuries.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Top des types de blessures
                st.subheader("🤕 Types de blessures")
                injury_counts = filtered_injuries['injury_reason'].value_counts().head(10)
                fig = px.bar(x=injury_counts.values, y=injury_counts.index, orientation='h')
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Distribution des durées
                st.subheader("⏰ Distribution des durées")
                if 'days_missed' in filtered_injuries.columns:
                    fig = px.histogram(filtered_injuries, x='days_missed', nbins=20)
                    fig.update_layout(height=400, showlegend=False, xaxis_title="Jours perdus", yaxis_title="Nombre de blessures")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Analyse par position
            if not filtered_players.empty:
                st.subheader("⚽ Analyse par position")
                
                # Jointure pour avoir les positions
                injury_position = filtered_injuries.merge(
                    filtered_players[['player_id', 'position']], 
                    on='player_id', 
                    how='left'
                )
                
                position_stats = injury_position.groupby('position').agg({
                    'injury_reason': 'count',
                    'days_missed': 'mean',
                    'games_missed': 'mean'
                }).round(1)
                
                position_stats.columns = ['Nb_blessures', 'Moy_jours', 'Moy_matchs']
                position_stats = position_stats.reset_index().sort_values('Nb_blessures', ascending=False)
                
                fig = px.bar(position_stats.head(10), x='position', y=['Nb_blessures'], 
                            title="Nombre de blessures par position")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📈 Tendances temporelles")
        
        if not filtered_injuries.empty and 'from_date' in filtered_injuries.columns:
            # Évolution mensuelle
            filtered_injuries['month_year'] = filtered_injuries['from_date'].dt.to_period('M')
            monthly_trend = filtered_injuries.groupby('month_year').size().reset_index()
            monthly_trend['month_year_str'] = monthly_trend['month_year'].astype(str)
            
            fig = px.line(monthly_trend, x='month_year_str', y=0, 
                         title="Évolution mensuelle des blessures")
            fig.update_layout(xaxis_title="Mois", yaxis_title="Nombre de blessures")
            st.plotly_chart(fig, use_container_width=True)
            
            # Saisonnalité (mois de l'année)
            if len(filtered_injuries) > 12:
                filtered_injuries['month'] = filtered_injuries['from_date'].dt.month
                monthly_pattern = filtered_injuries.groupby('month').size().reset_index()
                month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                              'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
                monthly_pattern['month_name'] = monthly_pattern['month'].apply(lambda x: month_names[x-1])
                
                fig = px.bar(monthly_pattern, x='month_name', y=0, 
                            title="Répartition saisonnière des blessures")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("📥 Export des données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Joueurs filtrés**")
            if not filtered_players.empty:
                csv_players = filtered_players.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger joueurs (CSV)",
                    data=csv_players,
                    file_name=f"joueurs_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.write(f"📊 {len(filtered_players)} joueurs")
        
        with col2:
            st.write("**Blessures filtrées**")
            if not filtered_injuries.empty:
                # Ajouter les noms des joueurs si possible
                if name_col:
                    export_injuries = filtered_injuries.merge(
                        filtered_players[['player_id', name_col]], 
                        on='player_id', 
                        how='left'
                    )
                else:
                    export_injuries = filtered_injuries.copy()
                
                csv_injuries = export_injuries.to_csv(index=False)
                st.download_button(
                    label="📥 Télécharger blessures (CSV)",
                    data=csv_injuries,
                    file_name=f"blessures_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                st.write(f"🚑 {len(filtered_injuries)} blessures")
        
        # Résumé de la recherche
        st.subheader("📋 Résumé de la recherche")
        search_summary = {
            "Filtres appliqués": {
                "Nom joueur": player_name_search if player_name_search else "Aucun",
                "Positions": ", ".join(selected_positions) if selected_positions else "Toutes",
                "Nationalité": selected_nationality,
                "Types blessures": ", ".join(selected_injury_types) if selected_injury_types else "Tous",
                "Saisons": ", ".join(selected_seasons) if selected_seasons else "Toutes"
            },
            "Résultats": {
                "Joueurs trouvés": len(filtered_players),
                "Blessures trouvées": len(filtered_injuries),
                "Taux de correspondance joueurs": f"{len(filtered_players)/len(players_df)*100:.1f}%",
                "Taux de correspondance blessures": f"{len(filtered_injuries)/len(injuries_df)*100:.1f}%"
            }
        }
        
        st.json(search_summary)

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
        ["📊 Vue d'ensemble", "🔍 Analyse détaillée", "� Recherche avancée", "�👤 Profil joueur", "ℹ️ À propos"]
    )
    
    # Chargement des données
    with st.spinner("Chargement des données..."):
        injuries_df, players_df = load_data()
    
    if injuries_df.empty or players_df.empty:
        st.error("❌ Impossible de charger les données. Vérifiez que les fichiers CSV sont présents.")
        st.info("Fichiers requis: player_injuries.csv et player_profiles.csv")
        return
    
    # Navigation entre les pages
    if page == "📊 Vue d'ensemble":
        show_overview(injuries_df, players_df)
    elif page == "🔍 Analyse détaillée":
        show_detailed_analysis(injuries_df, players_df)
    elif page == "� Recherche avancée":
        show_advanced_search()
    elif page == "�👤 Profil joueur":
        show_player_profile()
    elif page == "ℹ️ À propos":
        st.header("ℹ️ À propos")
        st.write("""
        ### Football Injury Analytics
        
        Cette application analyse les données de blessures de joueurs de football
        pour fournir des insights sur les patterns et tendances.
        
        **Données:**
        - 🏃‍♂️ Profils de joueurs
        - 🚑 Historique des blessures
        - 📊 Analyses statistiques
        
        **Fonctionnalités:**
        - Vue d'ensemble des statistiques
        - Analyse détaillée avec filtres
        - Profils individuels des joueurs
        
        **Note:** Version simplifiée utilisant les fichiers CSV locaux.
        Pour la version complète avec Cassandra, configurez d'abord la base de données.
        """)

if __name__ == "__main__":
    main()