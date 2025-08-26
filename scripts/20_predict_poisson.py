
import pandas as pd, numpy as np, math, json, os
from scripts.utils import poisson_pmf

df = pd.read_csv("data/processed/features_today.csv")

def adjust_lambda(lam_base, ai_att, opp_ai_def):
    # התקפה חסרה ↓, הגנה יריבה חסרה ↑
    return lam_base * (0.75 + 0.25*ai_att) * (1.00 + 0.25*(1.0 - opp_ai_def))

out_rows = []
for _, r in df.iterrows():
    lam_h = adjust_lambda(r.lam_home_base, r.ai_home_att, r.ai_away_def)
    lam_a = adjust_lambda(r.lam_away_base, r.ai_away_att, r.ai_home_def)
    # מטריצת הסתברויות 0..6
    max_g = 6
    ph = [poisson_pmf(k, lam_h) for k in range(max_g+1)]
    pa = [poisson_pmf(k, lam_a) for k in range(max_g+1)]
    matrix = np.outer(ph, pa)
    home_win = float(np.tril(matrix, -1).sum())
    draw = float(np.trace(matrix))
    away_win = float(np.triu(matrix, 1).sum())
    # ציון "סביר ביותר"
    idx = np.unravel_index(np.argmax(matrix), matrix.shape)
    pred_h, pred_a = int(idx[0]), int(idx[1])
    # O/U 2.5
    over25 = 0.0
    for i in range(max_g+1):
        for j in range(max_g+1):
            if i + j > 2:
                over25 += matrix[i,j]
    out_rows.append({
        "fixture_id": int(r.fixture_id),
        "home_id": int(r.home_id), "home_name": r.home_name,
        "away_id": int(r.away_id), "away_name": r.away_name,
        "lambda_home": round(lam_h, 3), "lambda_away": round(lam_a, 3),
        "p_home": round(home_win, 3), "p_draw": round(draw, 3), "p_away": round(away_win, 3),
        "pred_score": f"{pred_h}-{pred_a}",
        "p_over_2_5": round(over25, 3),
    })

preds = pd.DataFrame(out_rows)
os.makedirs("data/processed", exist_ok=True)
preds.to_csv("data/processed/preds_today.csv", index=False, encoding="utf-8")
print("Saved predictions for", len(preds), "fixtures.")
