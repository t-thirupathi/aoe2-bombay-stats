import pandas as pd
import os
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--server", type=str, default="AOE2-DOTA2", help="Discord server")
args = argparser.parse_args()

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "new_data", args.server)

# === Load and clean CSVs ===
matches = pd.read_csv(os.path.join(data_dir, "qc_matches.csv"))
player_matches = pd.read_csv(os.path.join(data_dir, "qc_player_matches.csv"))
players = pd.read_csv(os.path.join(data_dir, "qc_players.csv"))
# ratings = clean_csv(pd.read_csv(os.path.join(data_dir, "qc_rating_history.csv")), ["match_id", "at", "user_id", "rating_before", "rating_change", "deviation_before", "deviation_change", "reason"])

matches = matches.dropna(subset=["match_id", "winner_team"])
matches["match_id"] = matches["match_id"].astype(int)
matches["winner_team"] = matches["winner_team"].astype(int)

player_matches = player_matches.dropna()
player_matches[["match_id", "user_id", "team"]] = player_matches[["match_id", "user_id", "team"]].astype(int)

players["user_id"] = players["user_id"].astype(int)
players["rating"] = pd.to_numeric(players["rating"], errors="coerce").fillna(0).astype(int)
players.set_index("user_id", inplace=True)

# === Player info lookup ===
def get_player_info(uid):
    try:
        row = players.loc[uid]
        return row["nick"], row["rating"]
    except KeyError:
        # Player not found in the players DataFrame
        return None, None

# === Generate output ===
output_rows = []
skipped_matches = []

for _, match in matches.iterrows():
    match_id = match["match_id"]
    print(f"Processing match {match_id}...")
    date =  match["at"].split(" ")[0]
    year_month = "-".join(date.split("-")[:2])

    map_name = match["maps"] if pd.notnull(match["maps"]) and match["maps"] else "Unknown"
    winner_team = match["winner_team"]

    match_players = player_matches[player_matches["match_id"] == match_id]
    # if pmatch.shape[0] != 8:
    #     skipped_matches.append((match_id, "not 8 players"))
    #     continue

    teams = match_players.groupby("team")["user_id"].apply(list).to_dict()
    print(teams)
    # if not all(t in teams for t in [0, 1]) or len(teams[0]) != 4 or len(teams[1]) != 4:
    if not all(t in teams for t in [0, 1]):
        skipped_matches.append((match_id, "missing or malformed teams"))
        continue

    winners = teams[winner_team]
    losers = teams[1 - winner_team]
    while len(winners) != 4:
        winners.append(None)
    while len(losers) != 4:
        losers.append(None)

    w_nicks, w_ratings = list(zip(*[get_player_info(uid) for uid in winners]))
    l_nicks, l_ratings = list(zip(*[get_player_info(uid) for uid in losers]))
        
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
