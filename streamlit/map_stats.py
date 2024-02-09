import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from dateutil.relativedelta import relativedelta
from collections import Counter

df = pd.read_csv('../data/matches.csv')
df.sort_values(by='match_id', inplace=True)

all_player_games = df['w1'].values.tolist() + \
    df['w2'].values.tolist() + \
    df['w3'].values.tolist() + \
    df['w4'].values.tolist() + \
    df['l1'].values.tolist() + \
    df['l2'].values.tolist() + \
    df['l3'].values.tolist() + \
    df['l4'].values.tolist()
player_game_count = Counter(all_player_games)

all_maps = sorted(df['map'].unique())
map_counts = df['map'].value_counts()
frequent_maps = map_counts[map_counts >= 20].index.tolist()

map_ = st.selectbox('Select a map', sorted(frequent_maps))

# Filter matches involving the given player
map_df = df[df['map'] == map_]
st.write('Total games:', len(map_df.index))

all_players = list(set(
                    map_df['w1'].values.tolist() +
                    map_df['w2'].values.tolist() +
                    map_df['w3'].values.tolist() +
                    map_df['w4'].values.tolist() +
                    map_df['l1'].values.tolist() +
                    map_df['l2'].values.tolist() +
                    map_df['l3'].values.tolist() +
                    map_df['l4'].values.tolist()
                    ))
all_players = list(filter(pd.notna, all_players))


stats = []
for player in all_players:
    won = len(map_df[
                        (map_df['w1'] == player) |
                        (map_df['w2'] == player) |
                        (map_df['w3'] == player) |
                        (map_df['w4'] == player)
                        ].index)
    lost = len(map_df[
                        (map_df['l1'] == player) |
                        (map_df['l2'] == player) |
                        (map_df['l3'] == player) |
                        (map_df['l4'] == player)
                        ].index)

    play_rate = round((won+lost) * 100 / player_game_count[player], 2)
    win_rate = round(won * 100 / (won+lost), 2)

    if won+lost > 0:
        stats.append({
            'player': player,
            'total': won+lost,
            'play_rate': play_rate,
            'won': won,
            'lost': lost,
            'win_rate': win_rate
        })
stats_df = pd.DataFrame(stats).sort_values(by='win_rate', ascending=False)
results = stats_df[stats_df['total'] >= 5].reset_index(drop=True)
results.index += 1
st.write(results)

