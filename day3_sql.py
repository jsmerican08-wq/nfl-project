import sqlite3
import pandas as pd

pbp = pd.read_parquet("data/pbp_2025.parquet")
cols = ["game_id", "posteam", "qtr", "down", "yardline_100", "ydstogo", "score_differential", "play_type", "wp"]
reg = pbp[(pbp["down"] == 4) & (pbp["season_type"] == "REG")][cols]
decisions = ["punt", "field_goal", "run", "pass"]
fourth = reg[reg["play_type"].isin(decisions)]

conn = sqlite3.connect("data/nfl.db")
fourth.to_sql("fourth_downs", conn, if_exists="replace", index=False)

def q(sql):
    print(pd.read_sql(sql, conn))
    print()
q("SELECT game_id, posteam, ydstogo, score_differential, wp FROM fourth_downs where play_type = 'pass' and qtr = 4 order by ydstogo desc limit 5;")
q("SELECT posteam, COUNT(*) AS plays, SUM(CASE WHEN play_type IN ('run','pass') THEN 1 ELSE 0 END) AS go_plays, 1.0 * SUM(CASE WHEN play_type IN ('run','pass') THEN 1 ELSE 0 END) / COUNT(*) AS go_rate FROM fourth_downs GROUP BY posteam ORDER BY go_rate DESC")
q("""
SELECT posteam,
       COUNT(*) AS short_yardage_opportunities,
       SUM(CASE WHEN play_type IN ('run', 'pass') THEN 1 ELSE 0 END) AS go_plays,
       1.0 * SUM(CASE WHEN play_type IN ('run', 'pass') THEN 1 ELSE 0 END) / COUNT(*) AS go_rate
FROM fourth_downs
WHERE ydstogo <= 1
GROUP BY posteam
ORDER BY go_rate DESC
LIMIT 5;
""")