import streamlit as st
import requests

API_KEY = "9d23c14ba9006f46fd0fe7968b490671"
API_URL = "https://api.the-odds-api.com/v4/sports"

# Load custom CSS
def load_css(file_name="style.css"):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Arbitrage detection
def find_arbitrage(events):
    arbitrage_opps = []
    for game in events:
        try:
            teams = game["teams"]
            bookmakers = game["bookmakers"]
            best_odds = {}
            best_books = {}

            for bookmaker in bookmakers:
                for market in bookmaker["markets"]:
                    if market["key"] == "h2h":
                        for outcome in market["outcomes"]:
                            team = outcome["name"]
                            price = outcome["price"]
                            if team not in best_odds or price > best_odds[team]:
                                best_odds[team] = price
                                best_books[team] = bookmaker["title"]

            if len(best_odds) == 2:
                inv_sum = sum(1 / odd for odd in best_odds.values())
                if inv_sum < 1:
                    profit_percent = round((1 - inv_sum) * 100, 2)
                    arbitrage_opps.append({
                        "match": teams,
                        "odds": best_odds,
                        "bookmakers": best_books,
                        "profit": profit_percent
                    })

        except KeyError:
            continue
    return arbitrage_opps

# Fetch odds for all sports
def fetch_all_odds():
    sports_res = requests.get(f"{API_URL}?apiKey={API_KEY}")
    if sports_res.status_code != 200:
        st.error("Failed to fetch sports list.")
        return []

    sports = sports_res.json()
    all_events = []
    for sport in sports:
        sport_key = sport["key"]
        odds_res = requests.get(
            f"{API_URL}/{sport_key}/odds",
            params={
                "apiKey": API_KEY,
                "regions": "eu",
                "markets": "h2h",
                "oddsFormat": "decimal"
            }
        )
        if odds_res.status_code == 200:
            all_events.extend(odds_res.json())
    return all_events

# Main app
st.set_page_config(page_title="Fire Bet AI – Arbitrage Finder")
load_css()
st.title("Fire Bet AI – Arbitrage Finder")

if st.button("Refresh Arbitrage Bets"):
    with st.spinner("Scanning all sports and leagues..."):
        odds = fetch_all_odds()
        arbs = find_arbitrage(odds)

        if arbs:
            for arb in arbs:
                st.markdown(f"""
                <div class="arb-card">
                    <strong>Match:</strong> {arb['match'][0]} vs {arb['match'][1]}<br>
                    <strong>Profit:</strong> {arb['profit']}%<br>
                    <strong>{arb['match'][0]}:</strong> {arb['odds'][arb['match'][0]]} @ {arb['bookmakers'][arb['match'][0]]}<br>
                    <strong>{arb['match'][1]}:</strong> {arb['odds'][arb['match'][1]]} @ {arb['bookmakers'][arb['match'][1]]}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No arbitrage opportunities found.")

# Auto-run on page load
if "ran_on_load" not in st.session_state:
    st.session_state.ran_on_load = True
    st.experimental_rerun()
