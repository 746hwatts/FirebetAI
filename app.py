import streamlit as st
import requests
import os
from datetime import datetime

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Fire Bet AI – Arbitrage Finder")

API_KEY = "9d23c14ba9006f46fd0fe7968b490671"
API_URL = "https://api.the-odds-api.com/v4/sports"

def get_all_odds():
    sports = requests.get(f"{API_URL}?apiKey={API_KEY}").json()
    all_odds = []

    for sport in sports:
        sport_key = sport["key"]
        try:
            odds_response = requests.get(
                f"{API_URL}/{sport_key}/odds",
                params={
                    "apiKey": API_KEY,
                    "regions": "eu,uk,us,au",
                    "markets": "h2h,spreads,totals",
                    "oddsFormat": "decimal"
                }
            )
            odds_data = odds_response.json()
            if isinstance(odds_data, list):
                all_odds.extend(odds_data)
        except Exception as e:
            print(f"Error fetching odds for {sport_key}: {e}")

    return all_odds

def find_arbitrage(odds_data):
    opportunities = []
    for game in odds_data:
        try:
            teams = game["teams"]
            commence_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
            for bookmaker in game.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    outcomes = market.get("outcomes", [])
                    if len(outcomes) < 2:
                        continue

                    best_odds = {}
                    for o in outcomes:
                        name = o["name"]
                        price = o["price"]
                        if name not in best_odds or price > best_odds[name]:
                            best_odds[name] = price

                    inv_sum = sum(1 / price for price in best_odds.values())
                    if inv_sum < 1:
                        profit_margin = (1 - inv_sum) * 100
                        opportunities.append({
                            "match": teams,
                            "time": commence_time,
                            "market": market["key"],
                            "best_odds": best_odds,
                            "profit": round(profit_margin, 2)
                        })
        except Exception as e:
            print(f"Error processing game: {e}")
    # Sort by highest profit
    opportunities.sort(key=lambda x: x["profit"], reverse=True)
    return opportunities

# Load data
with st.spinner("Fetching latest odds and scanning for arbitrage..."):
    odds = get_all_odds()
    arbs = find_arbitrage(odds)

# Display results
if arbs:
    for arb in arbs:
        st.markdown(f"""
        <div class="card">
            <div class="match">{arb['match'][0]} vs {arb['match'][1]}</div>
            <div class="time">Kickoff: {arb['time']}</div>
            <div class="market">Market: {arb['market'].capitalize()}</div>
            <div class="profit">Profit: {arb['profit']}%</div>
            <div class="odds">
        """, unsafe_allow_html=True)

        for team, odd in arb["best_odds"].items():
            st.markdown(f"<span>{team}: {odd}</span><br>", unsafe_allow_html=True)

        st.markdown("</div></div><br>", unsafe_allow_html=True)
else:
    st.info("No arbitrage opportunities found.")

# Refresh button
if st.button("Refresh Arbitrage Bets"):
    st.rerun()
