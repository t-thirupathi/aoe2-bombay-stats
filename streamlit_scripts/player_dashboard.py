from collections import Counter
from datetime import datetime
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dateutil.relativedelta import relativedelta

script_dir = os.path.dirname(os.path.abspath(__file__))

server = st.selectbox(
    "Select Server",
    [
        "AOE2-DOTA2",
        "AOE Bombay",
    ],
)

server_data_dirs = {"AOE Bombay": "../data/", "AOE2-DOTA2": "../tw_data"}
data_dir = os.path.join(script_dir, server_data_dirs[server])
df = pd.read_csv(data_dir + "/matches.csv")
df.sort_values(by="match_id", inplace=True)
all_player_games = (
    df["w1"].values.tolist()
    + df["w2"].values.tolist()
    + df["w3"].values.tolist()
    + df["w4"].values.tolist()
    + df["l1"].values.tolist()
    + df["l2"].values.tolist()
    + df["l3"].values.tolist()
    + df["l4"].values.tolist()
)

player_game_count = Counter(all_player_games)

all_players = list(
    set(
        df["w1"].values.tolist()
        + df["w2"].values.tolist()
        + df["w3"].values.tolist()
        + df["w4"].values.tolist()
        + df["l1"].values.tolist()
        + df["l2"].values.tolist()
        + df["l3"].values.tolist()
        + df["l4"].values.tolist()
    )
)

player = st.selectbox("Select a player", ["Thiru"] + all_players)

# Filter matches involving the given player
player_df = df[
    (df["w1"] == player)
    | (df["w2"] == player)
    | (df["w3"] == player)
    | (df["w4"] == player)
    | (df["l1"] == player)
    | (df["l2"] == player)
    | (df["l3"] == player)
    | (df["l4"] == player)
]

player_df["won"] = (
    (player_df["w1"] == player)
    | (player_df["w2"] == player)
    | (player_df["w3"] == player)
    | (player_df["w4"] == player)
)


def get_player_rating(row, player):
    if row["w1"] == player:
        return row["w1_nr"]
    if row["w2"] == player:
        return row["w2_nr"]
    if row["w3"] == player:
        return row["w3_nr"]
    if row["w4"] == player:
        return row["w4_nr"]
    if row["l1"] == player:
        return row["l1_nr"]
    if row["l2"] == player:
        return row["l2_nr"]
    if row["l3"] == player:
        return row["l3_nr"]
    if row["l4"] == player:
        return row["l4_nr"]


player_df["player_rating"] = player_df.apply(get_player_rating, player=player, axis=1)

date_skeleton = pd.DataFrame(
    pd.date_range(min(player_df["date"]), max(player_df["date"]), freq="d").astype(
        "str"
    ),
    columns=["date"],
)
plot = sns.lineplot(
    data=date_skeleton.merge(player_df, on="date", how="left"),
    x="date",
    y="player_rating",
)
for ind, label in enumerate(plot.get_xticklabels()):
    if ind % 28 == 0:  # every 28th label is kept
        label.set_visible(True)
    else:
        label.set_visible(False)
plt.xticks(rotation=90)
st.pyplot(plot.get_figure())
# st.line_chart(data=player_df, x='date', y='player_rating')


def player_stats(df):
    matches = len(df.index)
    if matches == 0:
        return pd.DataFrame()

    won = len(df[df["won"]].index)
    lost = matches - won
    win_rate = round((won / matches) * 100, 2)
    avg_rating = round(df["player_rating"].mean(), 0)
    min_rating = round(df["player_rating"].min(), 0)
    max_rating = round(df["player_rating"].max(), 0)

    stats = {
        "Played": matches,
        "Won": won,
        "Lost": lost,
        "Win rate": win_rate,
        "Min rating": min_rating,
        "Max rating": max_rating,
        "Avg rating": avg_rating,
    }

    return pd.DataFrame(stats, index=[0])


st.write("Overall")
st.write(player_stats(player_df))

st.write("Last 2 months")
today = datetime.today()
two_months_ago = (today - relativedelta(months=2)).strftime("%Y-%m-%d")
st.write(player_stats(player_df[(player_df["date"] >= two_months_ago)]))


# skeleton column of all months
all_months = (
    "2022-01",
    "2022-02",
    "2022-03",
    "2022-04",
    "2022-05",
    "2022-06",
    "2022-07",
    "2022-08",
    "2022-09",
    "2022-10",
    "2022-11",
    "2022-12",
    "2023-01",
    "2023-02",
    "2023-03",
    "2023-04",
    "2023-05",
    "2023-06",
    "2023-07",
    "2023-08",
    "2023-09",
    "2023-10",
    "2023-11",
    "2023-12",
    "2024-01",
    "2024-02",
    "2024-03",
    "2024-04",
    "2024-05",
    "2024-06",
    "2024-07",
    "2024-08",
    "2024-09",
    "2024-10",
    "2024-11",
    "2024-12",
)
all_months = df["year_month"].unique()
all_months_df = pd.DataFrame(all_months, columns=["year_month"])

player_matches = df[
    (df["w1"] == player)
    | (df["w2"] == player)
    | (df["w3"] == player)
    | (df["w4"] == player)
    | (df["l1"] == player)
    | (df["l2"] == player)
    | (df["l3"] == player)
    | (df["l4"] == player)
]
matches_by_month = (
    player_matches.groupby(["year_month"])["match_id"]
    .count()
    .sort_index()
    .rename("matches played")
)
matches_by_month = (
    all_months_df.merge(matches_by_month.reset_index(), how="left")
    .fillna(0)
    .set_index("year_month")["matches played"]
    .astype(int)
)

st.bar_chart(matches_by_month)


def player_map_stats(player, min_games=5):
    won_games = (
        player_df[player_df["won"]]
        .groupby("map")["match_id"]
        .count()
        .sort_values(ascending=False)
        .reset_index()
    )
    lost_games = (
        player_df[~player_df["won"]]
        .groupby("map")["match_id"]
        .count()
        .sort_values(ascending=False)
        .reset_index()
    )

    results = won_games.merge(lost_games, on="map").rename(
        columns={"match_id_x": "won", "match_id_y": "lost"}
    )
    results["total"] = results["won"] + results["lost"]
    results["play_rate"] = round(results["total"] * 100 / player_game_count[player], 2)
    results = results[["map", "total", "play_rate", "won", "lost"]]
    results["win_rate"] = round(results["won"] / results["total"] * 100, 2)
    print(
        results[["total", "won", "lost"]].sum(),
        round(results["won"].sum() / results["total"].sum() * 100, 2),
    )
    results = (
        results[results["total"] >= min_games]
        .sort_values(by="win_rate", ascending=False)
        .reset_index(drop=True)
    )
    results.index += 1
    return results


def teammate_stats(player, min_games=5):
    won_df = player_df[player_df["won"]]
    lost_df = player_df[~player_df["won"]]

    stats = []
    for other_player in all_players:
        if other_player == player:
            continue

        won = len(
            won_df[
                (won_df["w1"] == other_player)
                | (won_df["w2"] == other_player)
                | (won_df["w3"] == other_player)
                | (won_df["w4"] == other_player)
            ].index
        )
        lost = len(
            lost_df[
                (lost_df["l1"] == other_player)
                | (lost_df["l2"] == other_player)
                | (lost_df["l3"] == other_player)
                | (lost_df["l4"] == other_player)
            ].index
        )
        if won + lost > 0:
            stats.append(
                {
                    "teammate": other_player,
                    "total": won + lost,
                    "won": won,
                    "lost": lost,
                    "win_rate": round(won * 100 / (won + lost), 2),
                }
            )
    stats_df = pd.DataFrame(stats).sort_values(by="win_rate", ascending=False)
    results = stats_df[stats_df["total"] >= min_games].reset_index(drop=True)
    results.index += 1
    return results


def opponent_stats(player, min_games=5):
    won_df = player_df[player_df["won"]]
    lost_df = player_df[~player_df["won"]]

    stats = []
    for other_player in all_players:
        if other_player == player:
            continue

        won = len(
            won_df[
                (won_df["l1"] == other_player)
                | (won_df["l2"] == other_player)
                | (won_df["l3"] == other_player)
                | (won_df["l4"] == other_player)
            ].index
        )
        lost = len(
            lost_df[
                (lost_df["w1"] == other_player)
                | (lost_df["w2"] == other_player)
                | (lost_df["w3"] == other_player)
                | (lost_df["w4"] == other_player)
            ].index
        )
        if won + lost > 0:
            stats.append(
                {
                    "opponent": other_player,
                    "total": won + lost,
                    "won": won,
                    "lost": lost,
                    "win_rate": round(won * 100 / (won + lost), 2),
                }
            )
    stats_df = pd.DataFrame(stats).sort_values(by="win_rate", ascending=False)
    results = stats_df[stats_df["total"] >= min_games].reset_index(drop=True)
    results.index += 1
    return results


min_games = st.number_input("Minimum games", value=5)

if server != "AOE2-DOTA2":
    st.write("Map stats")
    st.dataframe(player_map_stats(player, min_games))

st.write("Teammate stats")
st.write(teammate_stats(player, min_games))
st.write("Opponent stats")
st.write(opponent_stats(player, min_games))

st.write("Recent matches")
st.write(player_df.sort_values(by="match_id", ascending=False).head())
