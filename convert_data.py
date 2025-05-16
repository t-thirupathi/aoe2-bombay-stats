import pandas as pd
import os
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--server", type=str, default="AOE2-DOTA2", help="Discord server")
args = argparser.parse_args()

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "exported_data", args.server)

matches = pd.read_csv(os.path.join(data_dir, "qc_matches.csv"))
player_matches = pd.read_csv(os.path.join(data_dir, "qc_player_matches.csv"))
players = pd.read_csv(os.path.join(data_dir, "qc_players.csv"))
ratings = pd.read_csv(os.path.join(data_dir, "qc_rating_history.csv"))

matches = matches.dropna(subset=["match_id", "winner_team"])
matches["match_id"] = matches["match_id"].astype(int)
matches["winner_team"] = matches["winner_team"].astype(int)

player_matches = player_matches.dropna()
player_matches[["match_id", "user_id", "team"]] = player_matches[["match_id", "user_id", "team"]].astype(int)

players["user_id"] = players["user_id"].astype(int)
players["rating"] = pd.to_numeric(players["rating"], errors="coerce").fillna(0).astype(int)
players.set_index("user_id", inplace=True)
player_nick = players['nick'].to_dict()
print(player_nick)

# === Generate output ===
output_rows = []
skipped_matches = []

def get_player_info(user_id, match_id):
    try:
        nick = player_nick[user_id]
    except KeyError:
        # Player not found in the players DataFrame
        skipped_matches.append((match_id, "Player not found"))
        return "Unknown", 0, 0

    row = ratings[(ratings["match_id"] == match_id) & (ratings["user_id"] == user_id)].iloc[0]
    return nick, row["rating_before"], row["rating_change"]

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

    list(zip(*[get_player_info(user_id, match_id) for user_id in winners]))
    w_nicks, w_old_ratings, w_rating_changes = list(zip(*[get_player_info(user_id, match_id) for user_id in winners]))
    l_nicks, l_old_ratings, l_rating_changes = list(zip(*[get_player_info(user_id, match_id) for user_id in losers]))
    w_new_ratings = [i+j for i,j in zip(w_old_ratings, w_rating_changes)]
    l_new_ratings = [i+j for i,j in zip(l_old_ratings, l_rating_changes)]
    row = [
        match_id, date, year_month, map_name,
        *w_nicks, *l_nicks,
        *w_old_ratings, *l_old_ratings,  # original ratings
        *w_new_ratings, *l_new_ratings,  # new ratings (default = same)
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
