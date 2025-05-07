import streamlit as st
import requests
import time

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Fire Bet AI – Arbitrage Finder")

API_KEY = "c67ba6d52da5d8ec46c08a9f5037cc6c"
REGIONS = "uk,us,eu,au"
MARKETS = "h2h"  # Match winner
ODDS_API_URL = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions={REGIONS}&markets={MARKETS}&apiKey={API_KEY}"

@st.cache_data(ttl=300)
def fetch_odds():
    response = requests.get(ODDS_API_URL)
    if response.status_code != 200:
        st.error(f"Failed to fetch odds: {response.status_code}")
        return []
    return response.json()

def calculate_arbitrage(outcomes):
    """Returns arbitrage opportunity if exists."""
    best_odds = {}
    for outcome in outcomes:
        team = outcome['name']
        odds = float(outcome['price'])
        if team not in best_odds or best_odds[team] < odds:
            best_odds[team] = odds

    inv_sum = sum(1 / odd for odd in best_odds.values())
    if inv_sum < 1:
        return (1 - inv_sum) * 100, best_odds
    return None, None

data = fetch_odds()

# Arbitrage Finder
for event in data:
    bookmakers = event.get("bookmakers", [])
    best_odds = {}

    for bookie in bookmakers:
        for market in bookie["markets"]:
            arb_margin, top_odds = calculate_arbitrage(market["outcomes"])
            if arb_margin:
                st.markdown(f"""
                    <div class="arb-card">
                        <div class="arb-header">
                            {event['home_team']} vs {event['away_team']} — Profit: {arb_margin:.2f}%
                        </div>
                        <div class="arb-body">
                """, unsafe_allow_html=True)

                for outcome in market["outcomes"]:
                    team = outcome["name"]
                    odds = top_odds[team]
                    bookie_name = bookie["title"].lower().replace(" ", "")
                    st.markdown(f"""
                        <div class="bookie-column">
                            <img src="app/static/{bookie_name}.png" class="bookie-logo" />
                            <div class="team-name">{team}</div>
                            <div class="team-odds">@ {odds}</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div></div>", unsafe_allow_html=True)
                break

# Manual refresh button
if st.button("Refresh Arbitrage List"):
    st.cache_data.clear()
    st.experimental_rerun()
