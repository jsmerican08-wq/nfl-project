import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg://localhost:5432/nfl")

pbp = pd.read_parquet("data/pbp_2025.parquet")

game_dim = (pbp[["game_id", "season", "week", "home_team", "away_team"]]
            .drop_duplicates("game_id"))

cols = ["game_id", "posteam", "qtr", "ydstogo", "score_differential", "play_type", "wp", "yardline_100"]
reg = pbp[(pbp["down"] == 4) & (pbp["season_type"] == "REG")][cols]
fourth = reg[reg["play_type"].isin(["punt", "field_goal", "run", "pass"])]

game_dim.to_sql("game_dim", engine, if_exists="replace", index=False)
fourth.to_sql("fourth_down_facts", engine, if_exists="replace", index=False)

sql = """
SELECT g.week, COUNT(*) AS plays
FROM fourth_down_facts AS f
JOIN game_dim AS g ON f.game_id = g.game_id
GROUP BY g.week
ORDER BY g.week
"""
print(pd.read_sql(sql, engine))