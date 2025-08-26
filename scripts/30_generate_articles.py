
import os, json, pandas as pd, datetime as dt

preds = pd.read_csv("data/processed/preds_today.csv")
today = dt.date.today().isoformat()

# Markdown per match
base_dir = f"predictions/premier-league/{today}"
os.makedirs(base_dir, exist_ok=True)

articles = []
for _, r in preds.iterrows():
    title = f"{r['home_name']} vs {r['away_name']} – Preview"
    md = f"""# {title}

**Model outlook**  
- Expected goals (λ): Home {r['lambda_home']}, Away {r['lambda_away']}
- 1X2 probabilities: **Home {r['p_home']:.0%} · Draw {r['p_draw']:.0%} · Away {r['p_away']:.0%}**
- Most likely scoreline: **{r['pred_score']}**
- Over 2.5 goals: **{r['p_over_2_5']:.0%}**

**Notes**  
- ההסתברויות משלבות סטטיסטיקות ממוצע בית/חוץ + התאמה לזמינות שחקנים (פציעות/הרחקות).
- המודל הוא MVP ומכויל יום-יום; צפו לשינויים אחרי חדשות הרכבים/אימונים.

*Generated on {today}.*
"""
    slug = f"{r['home_name'].lower().replace(' ','-')}_vs_{r['away_name'].lower().replace(' ','-')}.md"
    path = os.path.join(base_dir, slug)
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    articles.append({
        "fixture_id": int(r["fixture_id"]),
        "title": title,
        "path": path,
        "home": r["home_name"], "away": r["away_name"],
        "p_home": float(r["p_home"]), "p_draw": float(r["p_draw"]), "p_away": float(r["p_away"]),
        "pred_score": r["pred_score"],
    })

# JSON for web
web_dir = "web/data"
os.makedirs(web_dir, exist_ok=True)
with open(os.path.join(web_dir, "preds.json"), "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print("Generated", len(articles), "articles and web/data/preds.json")
