import streamlit as st
import requests
from datetime import datetime

API_KEY = "c67ba6d52da5d8ec46c08a9f5037cc6c"
SPORTS_URL = f"https://api.the-odds-api.com/v4/sports/upcoming/odds?apiKey={API_KEY}&regions=uk&markets=h2h&oddsFormat=decimal"

# Load CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Fire Bet AI – Arbitrage Finder")

# Refresh button
if st.button("Refresh Arbitrage Opportunities"):
    st.experimental_rerun()

def calculate_implied_prob(odds):
    return round(1 / odds, 4)

def calculate_arbitrage(odds_list):
    total_inverse = sum([1/o for o in odds_list if o])
    return total_inverse, total_inverse < 1

def fetch_odds():
    try:
        response = requests.get(SPORTS_URL)
        data = response.json()
        opportunities = []

        for match in data:
            if len(match["bookmakers"]) < 2:
                continue

            best_odds = {}
            for bookmaker in match["bookmakers"]:
                for outcome in bookmaker["markets"][0]["outcomes"]:
                    name = outcome["name"]
                    if name not in best_odds or outcome["price"] > best_odds[name]["odds"]:
                        best_odds[name] = {
                            "odds": outcome["price"],
                            "bookmaker": bookmaker["key"],
                            "logo": f"static/{bookmaker['key']}.png"
                        }

            if len(best_odds) >= 2:
                odds_vals = [item["odds"] for item in best_odds.values()]
                total_prob, is_arb = calculate_arbitrage(odds_vals)
                if is_arb:
                    opportunity = {
                        "match": match["teams"],
                        "time": match["commence_time"],
                        "implied_prob": total_prob,
                        "profit_margin": round((1 - total_prob) * 100, 2),
                        "bookmakers": []
                    }
                    for name, details in best_odds.items():
                        opportunity["bookmakers"].append({
                            "team": name,
                            "odds": details["odds"],
                            "prob": f"{round(100 / details['odds'], 2)}%",
                            "logo": details["logo"],
                            "bookie": details["bookmaker"]
                        })
                    opportunities.append(opportunity)
        return opportunities
    except Exception as e:
        st.error("Failed to fetch or parse API data.")
        return []

arbs = fetch_odds()

# Display arbitrage cards
for arb in arbs:
    match_time = datetime.fromisoformat(arb["time"].replace("Z", "+00:00"))
    hours = int((match_time - datetime.utcnow()).total_seconds() // 3600)

    st.markdown(f"""
        <div class='arb-card'>
            <div class='arb-header'>{arb["profit_margin"]}% at {arb["implied_prob"]} {hours}h</div>
            <div class='arb-body'>
    """, unsafe_allow_html=True)

    for b in arb["bookmakers"]:
        st.markdown(f"""
                <div class='bookie-column'>
                    <img src='{b["logo"]}' class='bookie-logo' />
                    <div class='team-name'>{b["team"]}</div>
                    <div class='team-odds'>{b["prob"]} at {b["odds"]}</div>
                </div>
        """, unsafe_allow_html=True)

    st.markdown("""
            </div>
        </div>
    """, unsafe_allow_html=True)
