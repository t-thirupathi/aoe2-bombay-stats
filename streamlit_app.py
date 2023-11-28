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
print(all_players)

player = st.selectbox('Select a player', ['Sephiroth'] + all_players)

def player_rating(player):
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
    return player_df.sort_values(by='date')

player_df = player_rating(player)
#st.write(sns.lineplot(data=player_df, x='date', y='player_rating'))
st.line_chart(data=player_df, x='date', y='player_rating')


# skeleton column of all months
all_months = ('2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-06', 
              '2022-07', '2022-08', '2022-09', '2022-10', '2022-11', '2022-12', 
              '2023-01', '2023-02', '2023-03', '2023-04', '2023-05', '2023-06', 
              '2023-07', '2023-08', '2023-09', '2023-10', '2023-11')
all_months_df = pd.DataFrame(all_months, columns=['year_month'])

player_matches = df[(df['w1'] == player) | (df['w2'] == player)  | (df['w3'] == player) | (df['w4'] == player) |
    (df['l1'] == player) | (df['l2'] == player)  | (df['l3'] == player) | (df['l4'] == player)]
matches_by_month = player_matches.groupby(['year_month'])['match_id'].count().sort_index().rename('matches played')
matches_by_month = all_months_df.merge(matches_by_month.reset_index(), how='left').\
    fillna(0).set_index('year_month')['matches played'].astype(int)

st.bar_chart(matches_by_month)

def player_map_stats(player):
    won_games = df[(df['w1'] == player) | (df['w2'] == player)  | (df['w3'] == player) | (df['w4'] == player)].\
            groupby('map')['match_id'].count().sort_values(ascending=False).reset_index()
    lost_games = df[(df['l1'] == player) | (df['l2'] == player)  | (df['l3'] == player) | (df['l4'] == player)].\
            groupby('map')['match_id'].count().sort_values(ascending=False).reset_index()

    results = won_games.merge(lost_games, on='map').rename(columns={'match_id_x': 'won', 'match_id_y': 'lost'})
    results['total'] = results['won'] + results['lost']
    results = results[['map', 'total', 'won', 'lost']]
    results['win_rate'] = round(results['won'] / results['total'] * 100, 2)
    print(results[['total', 'won', 'lost']].sum(), round(results['won'].sum() / results['total'].sum() * 100, 2))
    return results[results['total'] >= 10].sort_values(by='win_rate', ascending=False).reset_index(drop=True)

st.write(player_map_stats(player))


def teammate_stats(df, player):
    # Filter matches involving the given player
    won_df = df[(df['w1'] == player) | (df['w2'] == player) | (df['w3'] == player) | (df['w4'] == player)]
    lost_df = df[(df['l1'] == player) | (df['l2'] == player) | (df['l3'] == player) | (df['l4'] == player)]

    teammate_stats = []
    for teammate in all_players:
        if teammate == player:
            continue
            
        won = len(won_df[
                            (won_df['w1'] == teammate) | 
                            (won_df['w2'] == teammate) | 
                            (won_df['w3'] == teammate) | 
                            (won_df['w4'] == teammate)
                            ].index)
        lost = len(lost_df[
                            (lost_df['l1'] == teammate) | 
                            (lost_df['l2'] == teammate) | 
                            (lost_df['l3'] == teammate) | 
                            (lost_df['l4'] == teammate)
                            ].index)
        if won+lost > 0:
            teammate_stats.append({
                'teammate': teammate, 
                'total': won+lost, 
                'won': won, 
                'lost': lost, 
                'win_rate': round(won*100/(won+lost), 2)
            })
    stats_df = pd.DataFrame(teammate_stats).sort_values(by='win_rate', ascending=False)
    return stats_df[stats_df['total'] >= 10].reset_index(drop=True)

def opponent_stats(df, player):
    # Filter matches involving the given player
    won_df = df[(df['w1'] == player) | (df['w2'] == player) | (df['w3'] == player) | (df['w4'] == player)]
    lost_df = df[(df['l1'] == player) | (df['l2'] == player) | (df['l3'] == player) | (df['l4'] == player)]

    opponent_stats = []
    for opponent in all_players:
        if opponent == player:
            continue

        won = len(won_df[
                            (won_df['l1'] == opponent) |
                            (won_df['l2'] == opponent) |
                            (won_df['l3'] == opponent) |
                            (won_df['l4'] == opponent)
                            ].index)
        lost = len(lost_df[
                            (lost_df['w1'] == opponent) |
                            (lost_df['w2'] == opponent) |
                            (lost_df['w3'] == opponent) |
                            (lost_df['w4'] == opponent)
                            ].index)
        if won+lost > 0:
            opponent_stats.append({
                'opponent': opponent,
                'total': won+lost,
                'won': won,
                'lost': lost,
                'win_rate': round(won*100/(won+lost), 2)
            })
    stats_df = pd.DataFrame(opponent_stats).sort_values(by='win_rate', ascending=False)
    return stats_df[stats_df['total'] >= 10].reset_index(drop=True)


st.write(teammate_stats(df, player))
st.write(opponent_stats(df, player))

