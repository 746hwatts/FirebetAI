import streamlit as st
import requests
from datetime import datetime

# Load custom CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Odds API key
API_KEY = "c67ba6d52da5d8ec46c08a9f5037cc6c"
API_URL = "https://api.the-odds-api.com/v4/sports/?regions=eu&markets=h2h,draw_no_bet,spreads,totals&oddsFormat=decimal&apiKey=" + API_KEY

# Bookmaker logos mapping
BOOKMAKER_LOGOS = {
    "coral": "coral.png",
    "ladbrokes_uk": "ladbrokes_uk.png",
    "livescorebet": "livescorebet.png",
    "mrgreen": "mrgreen.png",
    "skybet": "skybet.png",
    "virginbet": "virginbet.png",
    "grosvenor": "grosvenor.png",
    "leovegas": "leovegas.png",
    "matchbook": "matchbook.png",
    "paddypower": "paddypower.png",
    "unibet_uk": "unibet_uk.png",
    "williamhill": "williamhill.png",
    "betfair": "betfair.png",
    "casumo": "casumo.png"
}

# Header
st.title("Fire Bet AI – Arbitrage Finder")

# Refresh button
if st.button("Refresh"):
    st.experimental_rerun()

# Load data
@st.cache_data(ttl=300)
def get_odds_data():
    response = requests.get(API_URL)
    if response.status_code != 200:
        return []
    sports = response.json()
    arbitrage_data = []

    for sport in sports:
        sport_key = sport["key"]
        odds_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?regions=eu&markets=h2h&oddsFormat=decimal&apiKey={API_KEY}"
        odds_resp = requests.get(odds_url)
        if odds_resp.status_code != 200:
            continue
        events = odds_resp.json()
        for event in events:
            outcomes = []
            for bookmaker in event.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    if market["key"] == "h2h":
                        for i, outcome in enumerate(market["outcomes"]):
                            if len(outcomes) <= i:
                                outcomes.append([])
                            outcomes[i].append({
                                "team": outcome["name"],
                                "odds": outcome["price"],
                                "bookmaker": bookmaker["key"]
                            })

            if len(outcomes) >= 2:
                try:
                    o1 = max(outcomes[0], key=lambda x: x["odds"])
                    o2 = max(outcomes[1], key=lambda x: x["odds"])
                    if len(outcomes) == 3:
                        o3 = max(outcomes[2], key=lambda x: x["odds"])
                        total_prob = sum([1/o1["odds"], 1/o2["odds"], 1/o3["odds"]])
                        if total_prob < 1:
                            arbitrage_data.append({
                                "match": event["home_team"] + " vs " + event["away_team"],
                                "profit_margin": f"{round((1 - total_prob) * 100, 2)}%",
                                "implied_prob": round(total_prob, 3),
                                "time": "soon",
                                "bookmakers": [o1, o2, o3]
                            })
                except:
                    continue
    return arbitrage_data

arbs = get_odds_data()

# Show arbitrage opportunities
if arbs:
    for arb in arbs:
        st.markdown(f'''
            <div class="arb-card">
                <div class="arb-header">{arb['profit_margin']} at {arb['implied_prob']} — {arb['time']}</div>
                <div class="arb-body">
        ''', unsafe_allow_html=True)

        for bookie in arb["bookmakers"]:
            logo = BOOKMAKER_LOGOS.get(bookie["bookmaker"], "")
            st.markdown(f'''
                <div class="bookie-column">
                    <img src="app/static/{logo}" class="bookie-logo" />
                    <div class="team-name">{bookie['team']}</div>
                    <div class="team-odds">{round(100/bookie['odds'], 2)}% at {bookie['odds']}</div>
                </div>
            ''', unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)
else:
    st.warning("No arbitrage opportunities found at this time.")
