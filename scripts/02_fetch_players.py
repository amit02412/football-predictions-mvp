
import os, json, requests, glob, time
from dotenv import load_dotenv
load_dotenv()
KEY = os.getenv("APIFOOTBALL_KEY")
LEAGUE = os.getenv("LEAGUE_ID", "39")
SEASON = os.getenv("SEASON", "2025")
headers = {"x-apisports-key": KEY}

fixtures_files = sorted(glob.glob("data/raw/fixtures_*.json"))
if not fixtures_files:
    raise SystemExit("No fixtures file found. Run 00_fetch_fixtures.py first.")
fixtures = json.load(open(fixtures_files[-1], encoding="utf-8"))["response"]

teams = set()
for fx in fixtures:
    teams.add(fx["teams"]["home"]["id"])
    teams.add(fx["teams"]["away"]["id"])

os.makedirs("data/raw", exist_ok=True)
resp = {}
for tid in sorted(teams):
    page = 1
    team_players = []
    while True:
        url = f"https://v3.football.api-sports.io/players?league={LEAGUE}&season={SEASON}&team={tid}&page={page}"
        r = requests.get(url, headers=headers, timeout=30).json()
        team_players += r.get("response", [])
        pager = r.get("paging", {})
        total = pager.get("total", 1)
        if page >= total:
            break
        page += 1
        time.sleep(0.8)  # לנימוס מול ה-API
    resp[str(tid)] = team_players

with open("data/raw/players.json", "w", encoding="utf-8") as f:
    json.dump(resp, f, ensure_ascii=False, indent=2)

print("Fetched players for", len(resp), "teams.")
