# This is workspace for developing modeling fitting code before cleaning up

import pandas as pd
import pickle
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import gc

# Load in data
# Player_stats and Opp_stats files have been pulled from nflgame API via the
# nflgame_acquire.ipynb (scrape_nflgames.py)

dir_in = "../data/"
files = os.listdir(dir_in)



#player_stats_files = sorted([(int(re.sub('[^0-9]', '', f)), dir_in + f)
#                             for f in files if "player" in f], key=lambda x: x[0])
#opp_stats_files = sorted([(int(re.sub('[^0-9]', '', f)), dir_in + f)
#                          for f in files if "opp" in f], key=lambda x: x[0])

class WeeklyStats:
    def __init__(self, filepath):
        self.fpath = filepath
        self.year = int(filepath.split("_")[-1].split(".")[0])

    def read_player_data(self):
        df = pd.read_csv(self.fpath, index_col=0)
        df['team'] = df['team'].str.replace('JAX','JAC')
        df['team'] = df['team'].str.replace('LAC','SD')
        df['team'] = df['team'].str.replace('STL','LA')
        if "position_fill" in df:
            del df['position_fill']
        df['year'] = self.year
        return df

    def read_opp_data(self):
        df = pd.read_csv(self.fpath, index_col=0)
        df['year'] = self.year
        df['opp_TEAM'] = df['opp_TEAM'].str.replace('JAX','JAC')
        df['opp_OPP'] = df['opp_OPP'].str.replace('JAX','JAC')
        df['opp_TEAM'] = df['opp_TEAM'].str.replace('LAC','SD')
        df['opp_OPP'] = df['opp_OPP'].str.replace('LAC','SD')
        df['opp_TEAM'] = df['opp_TEAM'].str.replace('STL','LA')
        df['opp_OPP'] = df['opp_OPP'].str.replace('STL','LA')
        return df

player_stats_files = [WeeklyStats(os.path.join(dir_in,f)) for f in files if "player_stats_" in f]
opp_stats_files = [WeeklyStats(os.path.join(dir_in,f)) for f in files if "opp_stats_" in f]

player_dfs = {}
for pfile in player_stats_files:
    player_dfs[pfile.year] = pfile.read_player_data()


opp_dfs = {}
for ofile in opp_stats_files:
    opp_dfs[ofile.year] = ofile.read_opp_data()

new_opp_cols = ['offense', 'defense', 'opp_first_downs', 'opp_points',
       'opp_passing_yds', 'opp_penalty_cnt', 'opp_penalty_yds', 'opp_pos_time',
       'opp_punt_avg', 'opp_punt_cnt', 'opp_punt_yds', 'opp_rushing_yds',
       'opp_total_yds', 'opp_turnovers', 'week', 'year']

for year, df in opp_dfs.items():
    df.columns = new_opp_cols
    opp_dfs[year] = df

# Clean data and create target variable
data = pd.concat(player_dfs.values())
missing_positions = data[data.isnull()]
means = missing_positions.groupby(['id','full_name'], as_index=False).mean()
means = means[['id','full_name','passing_att', 'rushing_att', 'receiving_rec']]
means.columns = ['id','full_name','QB','RB','WRTE']
means = means[(means.QB != 0) | (means.RB != 0) | (means.WRTE != 0)]
means['position_fill'] = means[['QB','RB','WRTE']].idxmax(axis=1)
means = means[['id','position_fill']]
means['position_fill'] = means['position_fill'].apply(lambda x: np.nan if x == 'WRTE' else x)
