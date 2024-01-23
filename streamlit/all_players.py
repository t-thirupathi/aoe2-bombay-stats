import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('matches.csv')
all_players = list(set(
                    df['w1'].values.tolist() + 
                    df['w2'].values.tolist() + 
                    df['w3'].values.tolist() + 
                    df['w4'].values.tolist() + 
                    df['l1'].values.tolist() + 
                    df['l2'].values.tolist() + 
                    df['l3'].values.tolist() + 
                    df['l4'].values.tolist()
                    ))

def get_avg_rating(player):
    player_df = df[(df['w1'] == player) | (df['w2'] == player) | (df['w3'] == player) | (df['w4'] == player) |
            (df['l1'] == player) | (df['l2'] == player) | (df['l3'] == player) | (df['l4'] == player)]
    def player_rating(row, player):
        if row['w1'] == player:
            return row['w1_nr']
        if row['w2'] == player:
            return row['w2_nr']
        if row['w3'] == player:
            return row['w3_nr']
        if row['w4'] == player:
            return row['w4_nr']
        if row['l1'] == player:
            return row['l1_nr']
        if row['l2'] == player:
            return row['l2_nr']
        if row['l3'] == player:
            return row['l3_nr']
        if row['l4'] == player:
            return row['l4_nr']
    player_df['player_rating'] = player_df.apply(player_rating, player=player, axis=1)
    return player_df[player_df['date'] >= '2023-10-01']['player_rating'].mean()

player_stats = []
for player in all_players:
    player_df = df[(df['w1'] == player) | (df['w2'] == player) | (df['w3'] == player) | (df['w4'] == player) |
            (df['l1'] == player) | (df['l2'] == player) | (df['l3'] == player) | (df['l4'] == player)]
    matches = len(player_df[player_df['date'] >= '2023-10-01'].index)
    avg_rating = round(get_avg_rating(player), 2)
    stats = {'player': player, 
             'matches': matches, 
             'avg_rating': avg_rating
             }
    player_stats.append(stats)
player_stats_df = pd.DataFrame(player_stats)

st.write(player_stats_df.sort_values(by='avg_rating'))

