
import os, json, requests, glob
from dotenv import load_dotenv
load_dotenv()
KEY = os.getenv("APIFOOTBALL_KEY")
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

inj_all = {}
for tid in sorted(teams):
    url = f"https://v3.football.api-sports.io/injuries?team={tid}&season={SEASON}"
    r = requests.get(url, headers=headers, timeout=30).json()
    inj_all[str(tid)] = r.get("response", [])

with open("data/raw/injuries.json", "w", encoding="utf-8") as f:
    json.dump(inj_all, f, ensure_ascii=False, indent=2)

print("Fetched injuries per team:", len(inj_all))
