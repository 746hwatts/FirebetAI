import streamlit as st
import requests

API_KEY = "c67ba6d52da5d8ec46c08a9f5037cc6c"
BASE_URL = "https://api.the-odds-api.com/v4/sports"

def get_sports():
    url = f"{BASE_URL}?apiKey={API_KEY}"
    response = requests.get(url)
    return response.json()

def get_odds(sport):
    url = f"{BASE_URL}/{sport}/odds?apiKey={API_KEY}&regions=eu,uk,us,au&markets=h2h,totals&oddsFormat=decimal"
    response = requests.get(url)
    return response.json()

def find_arbitrage(events):
    arbs = []
    for event in events:
        if "bookmakers" not in event:
            continue
        for bm in event["bookmakers"]:
            markets = {m["key"]: m for m in bm["markets"]}
            if "h2h" in markets:
                odds = markets["h2h"]["outcomes"]
                if len(odds) >= 2:
                    try:
                        inv_total = sum(1 / o["price"] for o in odds)
                        if inv_total < 1:
                            profit_percent = round((1 - inv_total) * 100, 2)
                            arbs.append({
                                "teams": event["teams"],
                                "commence_time": event["commence_time"],
                                "bookmaker": bm["title"],
                                "odds": odds,
                                "profit": profit_percent
                            })
                    except:
                        continue
    return arbs

# Streamlit UI
st.title("Fire Bet AI - Arbitrage Finder")

sports = get_sports()
sport_keys = [s["key"] for s in sports]
sport_names = [s["title"] for s in sports]
selected = st.selectbox("Select a sport to scan for arbitrage:", sport_names)

if selected:
    index = sport_names.index(selected)
    sport_key = sport_keys[index]
    st.write(f"Scanning odds for: {selected}")

    data = get_odds(sport_key)
    arbs = find_arbitrage(data)

    if arbs:
        st.success(f"Found {len(arbs)} arbitrage opportunities!")
        for arb in arbs:
            st.write(f"**{arb['teams'][0]} vs {arb['teams'][1]}**")
            st.write(f"Bookmaker: {arb['bookmaker']}")
            st.write(f"Profit Potential: {arb['profit']}%")
            for o in arb['odds']:
                st.write(f"{o['name']}: {o['price']}")
            st.markdown("---")
    else:
        st.warning("No arbitrage opportunities found.")
