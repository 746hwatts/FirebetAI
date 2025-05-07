import streamlit as st
import requests
import os
from datetime import datetime
from PIL import Image

st.set_page_config(page_title="Fire Bet AI – Arbitrage Finder", layout="wide")

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Fire Bet AI – Arbitrage Finder")

# Set your Odds API key
API_KEY = "9d23c14ba9006f46fd0fe7968b490671"
SPORT = "soccer_epl"
REGION = "uk"
MARKETS = "h2h"

def fetch_odds():
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/?regions={REGION}&markets={MARKETS}&apiKey={API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("Failed to fetch odds from the API.")
        return []
    return res.json()

def find_arbitrage(odds_data):
    arbitrage_opps = []
    for game in odds_data:
        bookmakers = game.get("bookmakers", [])
        best_odds = {}
        for book in bookmakers:
            for market in book["markets"]:
                for outcome in market["outcomes"]:
                    name = outcome["name"]
                    if name not in best_odds or outcome["price"] > best_odds[name]["price"]:
                        best_odds[name] = {
                            "price": outcome["price"],
                            "bookmaker": book["title"]
                        }
        if len(best_odds) >= 2:
            implied_prob = sum(1 / v["price"] for v in best_odds.values())
            if implied_prob < 1:
                arbitrage_opps.append({
                    "match": game["teams"],
                    "commence_time": game["commence_time"],
                    "implied_prob": round(implied_prob, 3),
                    "bookmakers": best_odds
                })
    return arbitrage_opps

if st.button("Refresh Arbitrage Bets"):
    odds = fetch_odds()
    arbs = find_arbitrage(odds)
    if not arbs:
        st.info("No arbitrage opportunities found.")
    else:
        for arb in arbs:
            st.markdown(f"<div class='arb-card'><div class='arb-header'>{1 - arb['implied_prob']:.2%} at {arb['implied_prob']} — {arb['commence_time']}</div><div class='arb-body'>", unsafe_allow_html=True)
            for team, data in arb["bookmakers"].items():
                logo_path = f"static/{data['bookmaker'].lower().replace(' ', '_')}.png"
                st.markdown(f"""
                    <div class="bookie-column">
                        <img src="{logo_path}" class="bookie-logo" />
                        <div class="team-name">{team}</div>
                        <div class="team-odds">at {data['price']}</div>
                        <div class="bookie-name">{data['bookmaker']}</div>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
