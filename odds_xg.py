import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io
import math
import numpy as np
import random
import time
#from scipy.stats import norm, poisson, skellam
#from scipy.optimize import minimize

#Set page title and icon
st.set_page_config(page_title="BetWise", page_icon=":soccer:")

# Custom CSS for styling
st.markdown("""\
    <style>
        body {
            background-color: #f4f4f9;
            font-family: 'Arial', sans-serif;
        }
        .header {
            font-size: 32px;
            color: #3b5998;
            font-weight: bold;
            text-align: center;
        }
        .section-header {
            font-size: 20px;
            font-weight: 600;
            color: #007BFF;
        }
        .subsection-header {
            font-size: 18px;
            font-weight: 500;
            color: #5a5a5a;
        }
        .rating-table th {
            background-color: #007BFF;
            color: white;
            text-align: center;
        }
        .rating-table td {
            text-align: center;
        }
        .win-probability {
            color: #28a745;
            font-size: 18px;
            font-weight: 600;
        }
        .odds {
            color: #dc3545;
            font-size: 18px;
            font-weight: 600;
        }
        .slider {
            margin-top: 20px;
            padding: 10px;
            border-radius: 10px;
            background-color: #007BFF;
            color: white;
        }
        .button {
            background-color: #28a745;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-size: 16px;
        }
        .button:hover {
            background-color: #218838;
        }
        .card {
            background-color: #f8f9fa;
            border: 1px solid #007BFF;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 10px;
            transition: transform 0.2s;
        }
        .card:hover {
            transform: scale(1.05);
        }
        .card-title {
            color: #007BFF;
            font-weight: bold;
            font-size: 18px;
        }
        .card-odds {
            font-size: 24px;
            font-weight: bold;
            color: red;
        }
    </style>
""", unsafe_allow_html=True)

# Streamlit header
st.markdown('<div class="header">⚽ BetWise- Elo Odds Calculator</div>', unsafe_allow_html=True)

# Explanation tooltip
if "data_fetched" not in st.session_state:
    st.info("Use the sidebar to select a country and league. Click 'Get Ratings' to fetch the latest data.")

# Sidebar: How to use
with st.sidebar.expander("How to Use This App", expanded=True):
    st.write("1. Select Country and League.")
    st.write("2. Click 'Get Ratings' to fetch the latest data.")
    st.write("3. Select Home and Away Teams from the dropdowns.")
    st.write("4. View calculated odds and expected goals.")


# Sidebar: Select Match Details
st.sidebar.header("⚽ Select Match Details")
selected_country = st.sidebar.selectbox("Select Country:", list(leagues_dict.keys()), index=0)
selected_league = st.sidebar.selectbox("Select League:", leagues_dict[selected_country], index=0)

# Create two tabs
tab1, tab2 = st.tabs(["Elo Ratings Odds Calculator", "League Table"])

with tab1:
    try:
        # Create a progress bar
        progress_bar = st.progress(0)
    
        # Fetch data if not available or league has changed
        if "home_table" not in st.session_state or "away_table" not in st.session_state or st.session_state.get("selected_league") != selected_league:
            if st.sidebar.button("Get Ratings", key="fetch_button", help="Fetch ratings and tables for selected country and league"):
                with st.spinner(random.choice(spinner_messages)):
                    for i in range(100):  # Simulate progress
                        time.sleep(0.05)
                        progress_bar.progress(i + 1)
                    home_table, home_league_table = fetch_table(selected_country, selected_league, "home")
                    away_table, away_league_table = fetch_table(selected_country, selected_league, "away")
                    progress_bar.empty()
                    if isinstance(home_table, pd.DataFrame) and isinstance(away_table, pd.DataFrame):
                        home_table = home_table.drop(home_table.columns[[0, 2, 3]], axis=1)
                        away_table = away_table.drop(away_table.columns[[0, 2, 3]], axis=1)
                        st.session_state["home_table"] = home_table
                        st.session_state["away_table"] = away_table
                        st.session_state["league_table"] = home_league_table  # Store the league table
                        st.session_state["selected_league"] = selected_league
                        st.success("Data fetched successfully!")
                    else:
                        st.error("Error fetching one or both tables. Please try again.")
    
        # Display team selection and ratings if data is available
        if "home_table" in st.session_state and "away_table" in st.session_state:
            st.markdown('<div class="section-header">⚽ Match Details</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                home_team = st.selectbox("Select Home Team:", st.session_state["home_table"].iloc[:, 0])
            with col2:
                away_team = st.selectbox("Select Away Team:", st.session_state["away_table"].iloc[:, 0])
    
            # Fetch team ratings
            home_team_data = st.session_state["home_table"][st.session_state["home_table"].iloc[:, 0] == home_team]
            away_team_data = st.session_state["away_table"][st.session_state["away_table"].iloc[:, 0] == away_team]
            home_rating = home_team_data.iloc[0, 1]
            away_rating = away_team_data.iloc[0, 1]
            home = 10**(home_rating / 400)
            away = 10**(away_rating / 400)
            home_win_prob_raw = home / (home + away)
            away_win_prob_raw = away / (home + away)
    
            # Normalize win probabilities to exclude draw for DNB calculation
            total_win_prob = home_win_prob_raw + away_win_prob_raw
            home_win_prob_dnb = home_win_prob_raw / total_win_prob if total_win_prob > 0 else 0.5 # Normalize for DNB
            away_win_prob_dnb = away_win_prob_raw / total_win_prob if total_win_prob > 0 else 0.5 # Normalize for DNB
    
    
            # Display Ratings and Win Probabilities
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"{home_team} Home Rating: {home_rating}")
            with col2:
                st.write(f"{away_team} Away Rating: {away_rating}")
            st.markdown('<div class="section-header">Win Probability</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**{home_team} Win Probability:** {home_win_prob_raw:.2f}")
            with col2:
                st.write(f"**{away_team} Win Probability:** {away_win_prob_raw:.2f}")
    
            # Draw No Bet Odds Calculation
            home_draw_no_bet_odds = 1 / home_win_prob_dnb if home_win_prob_dnb > 0 else float('inf')
            away_draw_no_bet_odds = 1 / away_win_prob_dnb if away_win_prob_dnb > 0 else float('inf')
            st.markdown('<div class="section-header">Draw No Bet Odds</div>', unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            with col3:
                st.write(f"**{home_team} Draw No Bet Odds:** {home_draw_no_bet_odds:.2f}")
            with col4:
                st.write(f"**{away_team} Draw No Bet Odds:** {away_draw_no_bet_odds:.2f}")
    
            # Initialize variables for goals statistics
            home_goals_for_per_game = None
            home_goals_against_per_game = None
            away_goals_for_per_game = None
            away_goals_against_per_game = None
    
            # Helper function to extract goals (format "GF:GA")
            def extract_goals_parts(value):
                try:
                    parts = value.split(":")
                    if len(parts) >= 2:
                        goals_for = float(parts[0].strip())
                        goals_against = float(parts[1].strip())
                        return goals_for, goals_against
                    else:
                        return None, None
                except Exception as e:
                    return None, None
    
            # Calculate goals statistics from league table if available
            if "league_table" in st.session_state and st.session_state["league_table"] is not None:
                league_table = st.session_state["league_table"]
                # Home team stats
                home_team_row = league_table[league_table.iloc[:, 1] == home_team]
                if not home_team_row.empty:
                    home_raw = home_team_row.iloc[0]["Home.4"]
                    home_goals_for, home_goals_against = extract_goals_parts(home_raw)
                    try:
                        home_games = float(home_team_row.iloc[0]["Home"])
                        if home_games and home_games != 0:
                            if home_goals_for is not None:
                                home_goals_for_per_game = home_goals_for / home_games
                            if home_goals_against is not None:
                                home_goals_against_per_game = home_goals_against / home_games
                    except Exception as e:
                        pass
                # Away team stats
                away_team_row = league_table[league_table.iloc[:, 1] == away_team]
                if not away_team_row.empty:
                    away_raw = away_team_row.iloc[0]["Away.4"]
                    away_goals_for, away_goals_against = extract_goals_parts(away_raw)
                    try:
                        away_games = float(away_team_row.iloc[0]["Away"])
                        if away_games and away_games != 0:
                            if away_goals_for is not None:
                                away_goals_for_per_game = away_goals_for / away_games
                            if away_goals_against is not None:
                                away_goals_against_per_game = away_goals_against / away_games
                    except Exception as e:
                        pass
            # Calculate average league goals per match using 'Goals' (format "GF:GA") and 'M' (matches)
            avg_goals_per_match = None
            if "league_table" in st.session_state and st.session_state["league_table"] is not None:
                league_table = st.session_state["league_table"]
                if "Goals" in league_table.columns and "M" in league_table.columns:
                    league_table["GF"] = league_table["Goals"].apply(lambda x: float(x.split(":")[0].strip()) if isinstance(x, str) and ":" in x else None)
                    league_table["GA"] = league_table["Goals"].apply(lambda x: float(x.split(":")[1].strip()) if isinstance(x, str) and ":" in x else None)
                    avg_GF = league_table["GF"].mean()
                    avg_GA = league_table["GA"].mean()
                    avg_total = (league_table["GF"] + league_table["GA"]).mean()
                    avg_matches = league_table["M"].mean()
                    if avg_matches and avg_matches != 0:
                        avg_goals_per_match = avg_total / avg_matches
                    st.markdown('<div class="section-header">League Average Goals</div>', unsafe_allow_html=True)
                    if avg_goals_per_match is not None:
                        st.write(f"**Average Goals per Match:** {avg_goals_per_match:.2f}")
                    else:
                        st.write("**Average Goals per Match:** N/A")
                else:
                    st.write("The required columns ('Goals' and/or 'M') were not found in the league table.")
    
            # Calculate Expected Goals using per game statistics
            home_xg_base = None
            away_xg_base = None
            total_expected_goals = None
            if home_goals_for_per_game is not None and away_goals_against_per_game is not None:
                home_xg_base = (home_goals_for_per_game + away_goals_against_per_game) / 2
            if away_goals_for_per_game is not None and home_goals_against_per_game is not None:
                away_xg_base = (away_goals_for_per_game + home_goals_against_per_game) / 2
            if home_xg_base is not None and away_xg_base is not None and avg_goals_per_match is not None:
                total_expected_goals = ((home_xg_base + away_xg_base) + avg_goals_per_match) / 2
    
            # Calculate xG from DNB probs and total xG
            home_xg = None
            away_xg = None
            if total_expected_goals is not None and total_expected_goals > 0:
                try:
                    home_xg, away_xg = calculate_xg_from_dnb_probs(home_win_prob_dnb, away_win_prob_dnb, total_expected_goals)
                except ValueError as e:
                    st.error(f"Error calculating xG from DNB probabilities: {e}")
    
    
            # Display 1X2 odds and xG
            if home_xg is not None and away_xg is not None and total_expected_goals is not None and total_expected_goals > 0:
                try:
                    p_home_win, p_draw, p_away_win = calculate_1x2_and_xg(home_xg, away_xg)
                    home_odds_poisson = 1 / p_home_win if p_home_win > 0 else float('inf')
                    draw_odds_poisson = 1 / p_draw if p_draw > 0 else float('inf')
                    away_odds_poisson = 1 / p_away_win if p_away_win > 0 else float('inf')
                   
                    p_under_25 = poisson.cdf(2, total_expected_goals)
                    p_over_25 = 1 - p_under_25
                    over_odds_poisson = 1 / p_over_25 if p_over_25 > 0 else float('inf')
                    under_odds_poisson = 1 / p_under_25 if p_under_25 > 0 else float('inf')
    
                except ValueError as e:
                    st.error(f"Error calculating 1X2 odds: {e}")
            st.markdown('<div class="section-header">1X2 Betting Odds</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div style='color:black' class='card'><b>{home_team}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card'><div class='card-title'></div><div class='card-odds'>{home_odds_poisson:.2f}</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='color:black' class='card'><b>Draw</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card'><div class='card-title'></div><div class='card-odds'>{draw_odds_poisson:.2f}</div></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div style='color:black' class='card'><b>{away_team}</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='card'><div class='card-title'></div><div class='card-odds'>{away_odds_poisson:.2f}</div></div>", unsafe_allow_html=True)
    
            #Display home xG, away xG and total xG
            st.markdown('<div class="section-header">Expected Goals</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='card'><div class='card-title'>{home_team} xG</div><div class='card-odds'>{home_xg:.2f}</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='card'><div class='card-title'>{away_team} xG</div><div class='card-odds'>{away_xg:.2f}</div></div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='card'><div class='card-title'>Total xG</div><div class='card-odds'>{total_expected_goals:.2f}</div></div>", unsafe_allow_html=True)
    
            #Display O/U 2.5 Odds
            st.markdown('<div class="section-header">Over/Under 2.5 Goals</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div class='card'><div class='card-title'>Over 2.5</div><div class='card-odds'>{over_odds_poisson:.2f}</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='card'><div class='card-title'>Under 2.5</div><div class='card-odds'>{under_odds_poisson:.2f}</div></div>", unsafe_allow_html=True)
    except:
        pass
with tab2:
    try:
        # Display the league table as a simple text list
        if "league_table" in st.session_state and st.session_state["league_table"] is not None:
            league_table = st.session_state["league_table"]
            league_table.rename(columns={'Unnamed: 0': 'Position'}, inplace=True)
            for index, row in league_table.iterrows():
                team_name = row[league_table.columns[1]]
                points = row["P."]  # Points from the last column
                if pd.notna(team_name):
                    st.write(f"{row['Position']:.0f}. {team_name} - Points: {points}")
    except:
        pass
