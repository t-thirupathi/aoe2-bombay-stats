from ast import literal_eval
import glob
import pandas as pd
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt

res = pd.read_csv('data/match_results.csv')

for col in ['w1_or', 'w2_or', 'w3_or', 'w4_or', 
            'w1_nr', 'w2_nr', 'w3_nr', 'w4_nr', 
            'l1_or', 'l2_or', 'l3_or', 'l4_or', 
            'l1_nr', 'l2_nr', 'l3_nr', 'l4_nr', 
           ]:
    res[col].fillna(0, inplace=True)
    res[col] = res[col].astype(int)
    
file_pattern = 'data/match_starts*.csv'
csv_files = glob.glob(file_pattern)
start = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)
# start = pd.read_csv('data/match_starts.csv')

start = start.drop_duplicates(subset=['match_id'])

combined = res.merge(start, on='match_id', how='inner')

def w_players(row):
    if row['team_a_won']:
        players = literal_eval(row['team_a_players'])
    else:
        players = literal_eval(row['team_b_players'])
    players = [str(i) for i in players]
    players = players + [''] * (4 - len(players))
    players = '|'.join(players)
    return players

def l_players(row):
    if row['team_a_won']:
        players = literal_eval(row['team_b_players'])
    else:
        players = literal_eval(row['team_a_players'])
    players = [str(i) for i in players]
    players = players + [''] * (4 - len(players))
    players = '|'.join(players)
    return players

combined['winners'] = combined.apply(w_players, axis=1)
combined['losers'] = combined.apply(l_players, axis=1)

combined.head()

from collections import defaultdict

player_map = defaultdict(list)

def map_players(row):
    winners = [int('0' + i) for i in row['winners'].split('|')]
    losers = [int('0' + i) for i in row['losers'].split('|')]
    w1, w2, w3, w4 = row['w1'], row['w2'], row['w3'], row['w4']
    l1, l2, l3, l4 = row['l1'], row['l2'], row['l3'], row['l4']
    for a, b in zip(winners, [w1, w2, w3, w4]):
        player_map[a].append(b)
    
    for a, b in zip(losers, [l1, l2, l3, l4]):
        player_map[a].append(b)

combined.apply(map_players, axis=1)

player_map_final = {}
for k, v in player_map.items():
    player_map[k] = Counter(v).most_common()[0][0]

print('total players', len(player_map))

def id_to_name(ids):
    x = []
    for i in ids.split('|'):
        try:
            x.append(player_map[int(i)])
        except:
            x.append('')
    return '|'.join(x)
combined['winners'] = combined['winners'].apply(id_to_name)
combined['losers'] = combined['losers'].apply(id_to_name)

combined.drop(['w1', 'w2', 'w3', 'w4', 'l1', 'l2', 'l3', 'l4', 
               'team_a_won', 'team_b_won', 
               'team_a_players', 'team_b_players'], 
              axis=1, inplace=True)

combined.head(43).tail()

c = combined.head(43)
c[['w1', 'w2', 'w3', 'w4']] = c['winners'].str.split('|', expand=True)

combined[['w1', 'w2', 'w3', 'w4']] = combined['winners'].str.split('|', expand=True)
combined[['l1', 'l2', 'l3', 'l4']] = combined['losers'].str.split('|', expand=True)
                                                                  

combined.drop(['winners', 'losers'], axis=1, inplace=True)

combined['year_month'] = combined['date'].apply(lambda x: x[:7])

combined = combined[['match_id', 'date', 'year_month', 'map', 
                     'w1', 'w2', 'w3', 'w4', 
                     'l1', 'l2', 'l3', 'l4', 
                     'w1_or', 'w2_or', 'w3_or', 'w4_or', 
                     'w1_nr', 'w2_nr', 'w3_nr', 'w4_nr', 
                     'l1_or', 'l2_or', 'l3_or', 'l4_or', 
                     'l1_nr', 'l2_nr', 'l3_nr', 'l4_nr'
                    ]]

combined

def fix_map_name(map_):
    random_civs = False
    if 'random civ' in map_.lower():
        random_civs = True
    map_name = map_.split('(')[0].split('-')[0].strip().title()
    if random_civs:
        map_name += ' (Random civs)'
    return map_name
    

def fix_map_only_name(map_):
    return map_.lower().split('(')[0].split('-')[0].strip().title()
    

combined['map'] = combined['map'].apply(fix_map_name)
combined['map_only'] = combined['map'].apply(fix_map_only_name)

combined.to_csv('tw_data/matches.csv', index=False)

print(combined.head())

