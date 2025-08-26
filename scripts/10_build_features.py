
import os, json, glob, pandas as pd, numpy as np
from scripts.utils import safe_get

# load raw
fixtures_files = sorted(glob.glob("data/raw/fixtures_*.json"))
if not fixtures_files:
    raise SystemExit("No fixtures file found.")
fixtures = json.load(open(fixtures_files[-1], encoding="utf-8"))["response"]

teamstats = json.load(open("data/raw/teamstats.json", encoding="utf-8"))
players = json.load(open("data/raw/players.json", encoding="utf-8"))
injuries = json.load(open("data/raw/injuries.json", encoding="utf-8"))

rows = []
for fx in fixtures:
    fid = fx["fixture"]["id"]
    home = fx["teams"]["home"]["id"]; away = fx["teams"]["away"]["id"]
    home_name = fx["teams"]["home"]["name"]; away_name = fx["teams"]["away"]["name"]
    # Team stats (averages per match)
    h_stats = teamstats.get(str(home), {}).get("response", {})
    a_stats = teamstats.get(str(away), {}).get("response", {})

    def avg(d, side):
        # goals.for.average.home/away and goals.against.average.home/away
        gf = float(safe_get(d, ["goals","for","average",side], 1.2) or 1.2)
        ga = float(safe_get(d, ["goals","against","average",side], 1.2) or 1.2)
        return gf, ga

    gf_h_home, ga_h_home = avg(h_stats, "home")
    gf_a_away, ga_a_away = avg(a_stats, "away")

    # Base lambdas (geometric mean x home advantage)
    HFA = 1.10
    lam_home_base = HFA * np.sqrt(max(gf_h_home,1e-6) * max(ga_a_away,1e-6))
    lam_away_base = np.sqrt(max(gf_a_away,1e-6) * max(ga_h_home,1e-6))

    # Availability Index (attack/defense)
    inj_home_ids = { p.get("player",{}).get("id") for p in injuries.get(str(home),[]) }
    inj_away_ids = { p.get("player",{}).get("id") for p in injuries.get(str(away),[]) }

    def build_ai(team_id, inj_ids):
        plist = players.get(str(team_id), [])
        records = []
        for r in plist:
            pl = r.get("player",{}); st = (r.get("statistics") or [{}])[0]
            pos = (st.get("games") or {}).get("position")
            minutes = (st.get("games") or {}).get("minutes") or 0
            goals = (st.get("goals") or {}).get("total") or 0
            assists = (st.get("goals") or {}).get("assists") or 0
            tackles = (st.get("tackles") or {}).get("total") or 0
            inter = (st.get("tackles") or {}).get("interceptions") or 0
            duels = (st.get("duels") or {}).get("won") or 0
            pid = pl.get("id")
            available = (pid not in inj_ids)
            # Ratings
            att_rating = 0.0
            def_rating = 0.0
            if minutes and minutes > 0:
                per90 = 90.0 / minutes
                att_rating = (goals + 0.7*(assists or 0)) * per90 if pos in ("F","M") else 0.1*per90
                def_rating = ((tackles or 0) + (inter or 0) + 0.5*(duels or 0)) * per90 if pos in ("D","G") else 0.1*per90
            records.append({"pos":pos,"att":att_rating,"def":def_rating,"available":available})

        def ai_for(kind, positions):
            rel = [r for r in records if r["pos"] in positions]
            if not rel:
                return 1.0
            rel = sorted(rel, key=lambda x: x[kind], reverse=True)
            top = rel[:6]  # טופ 6 לשקלול
            cap = sum(r[kind] for r in top) or 1.0
            avail = sum(r[kind] for r in top if r["available"])
            return max(0.0, min(1.0, avail / cap))
        return ai_for("att", ("F","M")), ai_for("def", ("D","G"))

    ai_h_att, ai_h_def = build_ai(home, inj_home_ids)
    ai_a_att, ai_a_def = build_ai(away, inj_away_ids)

    rows.append({
        "fixture_id": fid,
        "home_id": home, "home_name": home_name,
        "away_id": away, "away_name": away_name,
        "lam_home_base": round(lam_home_base, 4),
        "lam_away_base": round(lam_away_base, 4),
        "ai_home_att": round(ai_h_att, 3), "ai_home_def": round(ai_h_def, 3),
        "ai_away_att": round(ai_a_att, 3), "ai_away_def": round(ai_a_def, 3),
    })

df = pd.DataFrame(rows)
os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/features_today.csv", index=False, encoding="utf-8")
print("Built features for", len(df), "fixtures.")
