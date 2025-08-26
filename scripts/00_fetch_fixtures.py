
import os, requests, datetime, json
from dotenv import load_dotenv
load_dotenv()
KEY = os.getenv("APIFOOTBALL_KEY")
LEAGUE = os.getenv("LEAGUE_ID", "39")
SEASON = os.getenv("SEASON", "2025")

headers = {"x-apisports-key": KEY}
today = datetime.date.today().isoformat()
# טווח יום אחד קדימה כדי לתפוס משחקים שעוברים חצות ב-UTC
url = f"https://v3.football.api-sports.io/fixtures?league={LEAGUE}&season={SEASON}&from={today}&to={today}"
resp = requests.get(url, headers=headers, timeout=30).json()

os.makedirs("data/raw", exist_ok=True)
with open(f"data/raw/fixtures_{today}.json", "w", encoding="utf-8") as f:
    json.dump(resp, f, ensure_ascii=False, indent=2)

print("Fetched fixtures:", len(resp.get("response", [])))
