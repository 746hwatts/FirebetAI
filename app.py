import streamlit as st
import requests
import pandas as pd

API_KEY = "c67ba6d52da5d8ec46c08a9f5037cc6c"
REGIONS = "uk,us,eu,au"
MARKETS = "h2h,totals"
ODDS_FORMAT = "decimal"
API_URL = "https://api.the-odds-api.com/v4/sports"

def fetch_sports():
    response = requests.get(f"{API_URL}?apiKey={API_KEY}")
    return response.json()

def fetch_odds(sport_key):
    url = f"{API_URL}/{sport_key}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": REGIONS,
        "markets": MARKETS,
        "oddsFormat": ODDS_FORMAT
    }
    response = requests.get(url, params=params)
    return response.json()

def detect_arbitrage(events):
    opportunities = []
    for event in events:
        for bookmaker in event.get("bookmakers", []):
            outcomes = {}
            for market in bookmaker.get("markets", []):
                for outcome in market.get("outcomes", []):
                    name = outcome["name"]
                    price = outcome["price"]
                    if name not in outcomes or price > outcomes[name][1]:
                        outcomes[name] = (bookmaker["title"], price)
            if len(outcomes) >= 2:
                inv_sum = sum(1/odds[1] for odds in outcomes.values())
                if inv_sum < 1:
                    profit = (1 - inv_sum) * 100
                    opportunities.append({
                        "Match": event["home_team"] + " vs " + event["away_team"],
                        "Market": market["key"] if "key" in market else "Unknown",
                        "Bookmakers": ", ".join(k[0] for k in outcomes.values()),
                        "Odds": ", ".join(f"{v[1]:.2f}" for v in outcomes.values()),
                        "Profit Margin (%)": round(profit, 2)
                    })
    return opportunities

st.set_page_config(page_title="Fire Bet AI", layout="wide")
st.title("Fire Bet AI - Arbitrage Opportunities Scanner")

with st.spinner("Fetching live arbitrage data..."):
    sports = fetch_sports()
    all_opportunities = []

    for sport in sports[:5]:  # Limit to 5 sports for performance
        events = fetch_odds(sport["key"])
        opportunities = detect_arbitrage(events)
        all_opportunities.extend(opportunities)

if all_opportunities:
    df = pd.DataFrame(all_opportunities)
    st.success(f"Found {len(df)} arbitrage opportunities.")
    st.dataframe(df)
else:
    st.warning("No arbitrage opportunities found at this time.")
