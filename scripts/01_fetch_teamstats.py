
import os, json, requests, glob
from dotenv import load_dotenv
load_dotenv()
KEY = os.getenv("APIFOOTBALL_KEY")
LEAGUE = os.getenv("LEAGUE_ID", "39")
SEASON = os.getenv("SEASON", "2025")
headers = {"x-apisports-key": KEY}

# קח את קובץ הפיקסצ'רס האחרון
fixtures_files = sorted(glob.glob("data/raw/fixtures_*.json"))
if not fixtures_files:
    raise SystemExit("No fixtures file found. Run 00_fetch_fixtures.py first.")
fixtures = json.load(open(fixtures_files[-1], encoding="utf-8"))["response"]

teams = set()
for fx in fixtures:
    teams.add(fx["teams"]["home"]["id"])
    teams.add(fx["teams"]["away"]["id"])

os.makedirs("data/raw", exist_ok=True)

all_stats = {}
for tid in sorted(teams):
    url = f"https://v3.football.api-sports.io/teams/statistics?league={LEAGUE}&season={SEASON}&team={tid}"
    r = requests.get(url, headers=headers, timeout=30).json()
    all_stats[str(tid)] = r

with open("data/raw/teamstats.json", "w", encoding="utf-8") as f:
    json.dump(all_stats, f, ensure_ascii=False, indent=2)

print("Fetched team statistics for", len(all_stats), "teams.")
