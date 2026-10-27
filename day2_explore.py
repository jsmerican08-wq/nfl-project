import os
import nflreadpy as nfl
import pandas as pd

os.makedirs("data", exist_ok=True)
path = "data/pbp_2025.parquet"

if os.path.exists(path):
	pbp = pd.read_parquet(path)
else:
	pbp = nfl.load_pbp(2025).to_pandas()
	pbp.to_parquet(path)
print(pbp.shape)
print(pbp["play_type"].value_counts())
print(pbp["down"].value_counts())
fourth = pbp[pbp["down"] == 4]
reg = pbp[(pbp["down"] == 4) & (pbp["season_type"] == "REG")]
print(len(fourth), len(reg))
print(reg["play_type"].value_counts())
cols = ["game_id", "posteam", "qtr", "yardline_100", "ydstogo",
        "score_differential", "play_type", "wp"]
f = reg[cols]
decisions = ["punt", "field_goal", "run", "pass"]
f = f[f["play_type"].isin(decisions)]
print(f.groupby("posteam").size().sort_values(ascending=False).head())
print(f.groupby("play_type")["ydstogo"].mean())
punts = f[f["play_type"] == "punt"].groupby("posteam").size().rename("punts").reset_index()
gos = f[f["play_type"].isin(["run", "pass"])].groupby("posteam").size().rename("go_for_it").reset_index()
summary = punts.merge(gos, on="posteam", how="outer").fillna(0)
print(summary.head())
one_yard = f[f["ydstogo"] == 1]
print(f"Fourth downs with one yard to go: {len(one_yard)}")
fourdownfourquarter = f[f["qtr"] == 4]
print(f"Fourth downs in the fourth quarter: {len(fourdownfourquarter)}")
less = f[f["ydstogo"] <= 3]
print(f"Fourth downs with three or fewer yards to go: {len(less)}")
fields = f[f["play_type"] == "field_goal"].groupby("posteam").size().rename("field_goals").reset_index()
print(fields.groupby("posteam").size().sort_values(ascending=False).head())
print(f.groupby("play_type")["yardline_100"].mean())
short = f[f["ydstogo"] <= 2]
print(short["play_type"].value_counts())
print(short["play_type"].value_counts(normalize=True))
summary = summary.merge(fields, on="posteam", how="outer").fillna(0)
print(summary)
summary["go_rate"] = summary["go_for_it"] / (summary["punts"] + summary["go_for_it"] + summary["field_goals"])
print(summary.sort_values("go_rate", ascending=False).head())
print(summary.sort_values("go_rate", ascending=False).tail())
short_punts = short[short["play_type"] == "punt"].groupby("posteam").size().rename("short_punts").reset_index()
short_gos = short[short["play_type"].isin(["run", "pass"])].groupby("posteam").size().rename("short_go_for_it").reset_index()
short_summary = short_punts.merge(short_gos, on="posteam", how="outer").fillna(0)
short_fields = short[short["play_type"] == "field_goal"].groupby("posteam").size().rename("short_field_goals").reset_index()
short_summary = short_summary.merge(short_fields, on="posteam", how="outer").fillna(0)
short_summary["short_go_rate"] = short_summary["short_go_for_it"] / (short_summary["short_punts"] + short_summary["short_go_for_it"] + short_summary["short_field_goals"])
print(short_summary.sort_values("short_go_rate", ascending=False).head())
print(short_summary.sort_values("short_go_rate", ascending=False).tail())