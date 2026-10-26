import nflreadpy as nfl

pbp = nfl.load_pbp(2025).to_pandas()
print(pbp.shape)
print(pbp[["posteam", "down", "ydstogo", "play_type"]].head())