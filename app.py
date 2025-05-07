import streamlit as st
import requests
from datetime import datetime

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Fire Bet AI – Arbitrage Finder (API-Football Edition)")

API_KEY = "1e5138cdf1msh25d26bc2da70f1dp1fe643jsnea43c578c7f8"
API_HOST = "api-football-v1.p.rapidapi.com"

def get_odds_data():
    url = "https://api-football-v1.p.rapidapi.com/v3/odds"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {"region": "eu"}  # All European odds

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return data.get("response", [])
    except Exception as e:
        st.error(f"Failed to fetch odds data: {e}")
        return []

def find_arbitrage(odds_response):
    opportunities = []
    for match in odds_response:
        try:
            bookmakers = match.get("bookmakers", [])
            best_odds = {}
            for book in bookmakers:
                for bet in book.get("bets", []):
                    if bet.get("name") != "Match Winner":
                        continue
                    for val in bet.get("values", []):
                        team = val["value"]
                        odd = float(val["odd"])
                        if team not in best_odds or odd > best_odds[team]:
                            best_odds[team] = odd

            if len(best_odds) >= 2:
                inv_sum = sum(1 / odd for odd in best_odds.values())
                if inv_sum < 1:
                    profit = round((1 - inv_sum) * 100, 2)
                    opportunities.append({
                        "teams": match["teams"],
                        "league": match["league"]["name"],
                        "time": match["fixture"]["date"],
                        "odds": best_odds,
                        "profit": profit
                    })
        except Exception as e:
            print(f"Error processing match: {e}")
    opportunities.sort(key=lambda x: x["profit"], reverse=True)
    return opportunities

# Fetch and display arbitrage opportunities
with st.spinner("Fetching odds and detecting arbitrage..."):
    odds_data = get_odds_data()
    arbitrage_opps = find_arbitrage(odds_data)

if arbitrage_opps:
    for arb in arbitrage_opps:
        st.markdown(f'''
        <div class="card">
            <div class="match">{arb["teams"]["home"]} vs {arb["teams"]["away"]}</div>
            <div class="league">{arb["league"]}</div>
            <div class="time">Kickoff: {datetime.fromisoformat(arb["time"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")}</div>
            <div class="profit">Profit: {arb["profit"]}%</div>
            <div class="odds">
        ''', unsafe_allow_html=True)
        for team, odd in arb["odds"].items():
            st.markdown(f"<span>{team}: {odd}</span><br>", unsafe_allow_html=True)
        st.markdown("</div></div><br>", unsafe_allow_html=True)
else:
    st.info("No arbitrage opportunities found.")

# Refresh button
if st.button("Refresh Arbitrage Bets"):
    st.rerun()
