"""Module for extracting raw match results."""

import glob
import pandas as pd
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument("--server", type=str, default="AOE2-DOTA2", help="Discord server")
args = argparser.parse_args()


FILE_PATTERN = f"data/{args.server}/match_results_raw*.csv"
csv_files = glob.glob(FILE_PATTERN)
df = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)

results = {}
for s in df["0"]:
    try:
        s = s.split("\n")
        game_id = int(s[1].split("(")[1].split(")")[0])
        team_a_won = s[3].split(" ")[1] in ("A", "1-Odd", "Alpha")
        team_b_won = s[3].split(" ")[1] in ("B", "2-Even", "Beta")

        player_count = 4

        if len(s) < 9:
            player_count = 1
        elif len(s) < 11:
            player_count = 2
        elif len(s) < 13:
            player_count = 3

        winners = []
        winners_old_rating = []
        winners_new_rating = []
        for line_no in range(4, 4 + player_count):
            winners.append(" ".join(s[line_no].split(" ")[1:-3]).strip(" |"))
            winners_old_rating.append(s[line_no].split(" ")[-3].strip("`"))
            winners_new_rating.append(s[line_no].split(" ")[-1].strip("`"))

        losers = []
        losers_old_rating = []
        losers_new_rating = []
        for line_no in range(5 + player_count, 5 + 2 * player_count):
            losers.append(" ".join(s[line_no].split(" ")[1:-3]).strip(" |"))
            losers_old_rating.append(s[line_no].split(" ")[-3].strip("`"))
            losers_new_rating.append(s[line_no].split(" ")[-1].strip("`"))

        w1 = w2 = w3 = w4 = None
        l1 = l2 = l3 = l4 = None
        w1_or = w2_or = w3_or = w4_or = None
        w1_nr = w2_nr = w3_nr = w4_nr = None
        l1_or = l2_or = l3_or = l4_or = None
        l1_nr = l2_nr = l3_nr = l4_nr = None

        if player_count == 4:
            w1, w2, w3, w4 = winners
            l1, l2, l3, l4 = losers
            w1_or, w2_or, w3_or, w4_or = winners_old_rating
            w1_nr, w2_nr, w3_nr, w4_nr = winners_new_rating
            l1_or, l2_or, l3_or, l4_or = losers_old_rating
            l1_nr, l2_nr, l3_nr, l4_nr = losers_new_rating
        elif player_count == 3:
            w1, w2, w3 = winners
            l1, l2, l3 = losers
            w1_or, w2_or, w3_or = winners_old_rating
            w1_nr, w2_nr, w3_nr = winners_new_rating
            l1_or, l2_or, l3_or = losers_old_rating
            l1_nr, l2_nr, l3_nr = losers_new_rating
        elif player_count == 2:
            w1, w2 = winners
            l1, l2 = losers
            w1_or, w2_or = winners_old_rating
            w1_nr, w2_nr = winners_new_rating
            l1_or, l2_or = losers_old_rating
            l1_nr, l2_nr = losers_new_rating
        elif player_count == 1:
            w1 = winners
            l1 = losers
            w1_or = winners_old_rating
            w1_nr = winners_new_rating
            l1_or = losers_old_rating
            l1_nr = losers_new_rating

        results[game_id] = {
            "w1": w1,
            "w2": w2,
            "w3": w3,
            "w4": w4,
            "l1": l1,
            "l2": l2,
            "l3": l3,
            "l4": l4,
            "w1_or": w1_or,
            "w2_or": w2_or,
            "w3_or": w3_or,
            "w4_or": w4_or,
            "l1_or": l1_or,
            "l2_or": l2_or,
            "l3_or": l3_or,
            "l4_or": l4_or,
            "w1_nr": w1_nr,
            "w2_nr": w2_nr,
            "w3_nr": w3_nr,
            "w4_nr": w4_nr,
            "l1_nr": l1_nr,
            "l2_nr": l2_nr,
            "l3_nr": l3_nr,
            "l4_nr": l4_nr,
            "team_a_won": team_a_won,
            "team_b_won": team_b_won,
        }
    except Exception as e:
        print(s)
        print(e)

df = pd.DataFrame(results).T.rename_axis("match_id")
df = df.drop_duplicates()

df.to_csv(f"data/{args.server}/match_results.csv", index=False)
