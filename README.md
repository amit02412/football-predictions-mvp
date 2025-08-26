
# Football Predictions MVP (Premier League 2025/26)

MVP שמביא פיקסצ'רים, סטטיסטיקות, פציעות, מחשב תחזית Poisson עם התאמות זמינות שחקנים, ומייצר כתבות + דף סטטי.

## מה בפנים
- **API**: API-FOOTBALL (league=39, season=2025).
- **Scripts**: משיכה, פיצ'רים, תחזיות, כתבות.
- **GitHub Actions**: ריצה כל שעה + עדכון לילה, דוחף נתונים לרפו.
- **Web (Static)**: טבלת משחקים והסתברויות ב-`web/index.html`.

> הערה: ייתכן שתצטרך להתאים מעט שמות שדות ספציפיים מה-API אם שונו מאז.

## התקנה מקומית
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# ערוך את .env והכנס APIFOOTBALL_KEY אמיתי + ודא שה-SEASON נכון (2025 לעונת 2025/26)
python scripts/00_fetch_fixtures.py
python scripts/01_fetch_teamstats.py
python scripts/02_fetch_players.py
python scripts/03_fetch_injuries.py
python scripts/10_build_features.py
python scripts/20_predict_poisson.py
python scripts/30_generate_articles.py
```

## GitHub Actions
1. פתח רפו חדש בגיטהאב והעלה את הקבצים.
2. Settings → Secrets and variables → Actions → **New repository secret**: `APIFOOTBALL_KEY`.
3. מצליחים? ה-Action ירוץ אוטומטית ויעדכן `data/` + `predictions/` + `web/data/preds.json`.
4. הפעל GitHub Pages על תיקיית `/web` (Settings → Pages → Branch: `main` / `/root`, Folder: `/web`).

## קבצי נתונים
- `data/raw/*.json` – גולמי מה-API.
- `data/processed/features_today.csv` – פיצ'רים למשחקי היום.
- `data/processed/preds_today.csv` – תחזיות.
- `web/data/preds.json` – סיכום לתצוגה בדף.

