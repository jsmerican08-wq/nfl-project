import sqlite3
import pandas as pd

pbp = pd.read_parquet("data/pbp_2025.parquet")

game_dim = (pbp[["game_id", "season", "week", "home_team", "away_team"]]
            .drop_duplicates("game_id"))

cols = ["game_id", "posteam", "qtr", "ydstogo", "score_differential", "play_type", "wp", "yardline_100"]
reg = pbp[(pbp["down"] == 4) & (pbp["season_type"] == "REG")][cols]
fourth = reg[reg["play_type"].isin(["punt", "field_goal", "run", "pass"])]

conn = sqlite3.connect("data/nfl.db")
game_dim.to_sql("game_dim", conn, if_exists="replace", index=False)
fourth.to_sql("fourth_down_facts", conn, if_exists="replace", index=False)

def q(sql):
    print(pd.read_sql(sql, conn))
    print()

q("""
SELECT f.posteam, f.play_type, g.week, g.home_team
FROM fourth_down_facts AS f
JOIN game_dim AS g ON f.game_id = g.game_id
LIMIT 10
""")
q("""
SELECT g.week, COUNT(*) AS plays, COUNT(CASE WHEN f.play_type = 'run' or f.play_type = 'pass' THEN 1 END) AS go_count
FROM fourth_down_facts AS f
JOIN game_dim AS g ON f.game_id = g.game_id
GROUP BY g.week
ORDER BY g.week
""")
q("""
SELECT CASE WHEN f.posteam = g.home_team THEN 'home' ELSE 'away' END AS team_type,
       ROUND(1.0 * COUNT(CASE WHEN f.play_type IN ('run', 'pass') THEN 1 END) / COUNT(*), 3) AS go_rate
FROM fourth_down_facts AS f
JOIN game_dim AS g ON f.game_id = g.game_id
GROUP BY team_type
""")
q("""
SELECT f.qtr AS q,
       ROUND(1.0 * COUNT(CASE WHEN f.play_type IN ('run', 'pass') THEN 1 END) / COUNT(*), 3) AS go_rate
FROM fourth_down_facts AS f
JOIN game_dim AS g ON f.game_id = g.game_id
GROUP BY f.qtr
""")
q("""
SELECT CASE WHEN f.yardline_100 < 20 THEN 'endzone' ELSE 'far' END AS closeness,
       ROUND(1.0 * COUNT(CASE WHEN f.play_type IN ('run', 'pass') THEN 1 END) / COUNT(*), 3) AS go_rate
FROM fourth_down_facts AS f
JOIN game_dim AS g ON f.game_id = g.game_id
GROUP BY closeness
""")