import pandas as pd
import os
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--server", type=str, default="AOE2-DOTA2", help="Discord server")
args = argparser.parse_args()

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "new_data", args.server)
print(f"Data directory: {data_dir}")
# === Helper: Clean CSV ===
def clean_csv(df, expected_columns):
    # df = df[df[df.columns[0]] != df.columns[0]]  # remove duplicate headers
    # df.columns = expected_columns
    return df

# === Load and clean CSVs ===
matches = clean_csv(pd.read_csv(os.path.join(data_dir, "qc_matches.csv")), ["match_id", "at", "queue", "winner_team", "maps"])
player_matches = clean_csv(pd.read_csv(os.path.join(data_dir, "qc_player_matches.csv")), ["match_id", "user_id", "team"])
players = clean_csv(pd.read_csv(os.path.join(data_dir, "qc_players.csv")), ["user_id", "nick", "is_hidden", "rating", "deviation", "wins", "losses", "draws", "streak"])
# ratings = clean_csv(pd.read_csv(os.path.join(data_dir, "qc_rating_history.csv")), ["match_id", "at", "user_id", "rating_before", "rating_change", "deviation_before", "deviation_change", "reason"])

# === Convert column types ===
matches = matches.dropna(subset=["match_id", "winner_team"])
matches["match_id"] = matches["match_id"].astype(int)
matches["winner_team"] = matches["winner_team"].astype(int)

player_matches = player_matches.dropna()
player_matches[["match_id", "user_id", "team"]] = player_matches[["match_id", "user_id", "team"]].astype(int)

players["user_id"] = players["user_id"].astype(int)
players["rating"] = pd.to_numeric(players["rating"], errors="coerce").fillna(0).astype(int)
players["nick"] = players["nick"].fillna("")

# === Player info lookup ===
def get_player_info(uid):
    row = players[players["user_id"] == uid]
    if row.empty:
        return f"user_{uid}", 0
    return row["nick"].values[0], row["rating"].values[0]

# === Generate output ===
output_rows = []
skipped_matches = []

for _, match in matches.iterrows():
    match_id = match["match_id"]
    at = match["at"]

    try:
        date = at.split(" ")[0]
        year_month = "-".join(date.split("-")[:2])
    except:
        skipped_matches.append((match_id, "bad date"))
        continue

    map_name = match["maps"] if pd.notnull(match["maps"]) and match["maps"] else "Unknown"
    winner_team = match["winner_team"]

    pmatch = player_matches[player_matches["match_id"] == match_id]
    if pmatch.shape[0] != 8:
        skipped_matches.append((match_id, "not 8 players"))
        continue

    teams = pmatch.groupby("team")["user_id"].apply(list).to_dict()
    if not all(t in teams for t in [0, 1]) or len(teams[0]) != 4 or len(teams[1]) != 4:
        skipped_matches.append((match_id, "missing or malformed teams"))
        continue

    winners = teams[winner_team]
    losers = teams[1 - winner_team]

    try:
        w_nicks, w_ratings = zip(*[get_player_info(uid) for uid in winners])
        l_nicks, l_ratings = zip(*[get_player_info(uid) for uid in losers])
    except:
        skipped_matches.append((match_id, "player info missing"))
        continue

    row = [
        match_id, date, year_month, map_name,
        *w_nicks, *l_nicks,
        *w_ratings, *l_ratings,  # original ratings
        *w_ratings, *l_ratings,  # new ratings (default = same)
        map_name
    ]
    output_rows.append(row)

# === Save Output ===
columns = [
    "match_id", "date", "year_month", "map",
    "w1", "w2", "w3", "w4",
    "l1", "l2", "l3", "l4",
    "w1_or", "w2_or", "w3_or", "w4_or",
    "l1_or", "l2_or", "l3_or", "l4_or",
    "w1_nr", "w2_nr", "w3_nr", "w4_nr",
    "l1_nr", "l2_nr", "l3_nr", "l4_nr",
    "map_only"
]

df_out = pd.DataFrame(output_rows, columns=columns)
df_out.to_csv(os.path.join(data_dir, "matches.csv"), index=False)

# === Summary ===
if skipped_matches:
    print(f"⚠️ Skipped {len(skipped_matches)} matches:")
    for mid, reason in skipped_matches:
        print(f"  - Match {mid} skipped due to: {reason}")
print(f"✅ Exported {len(df_out)} matches.")
