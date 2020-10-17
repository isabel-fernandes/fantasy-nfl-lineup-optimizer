"""
This code defines functions for reading raw CSV data pulled from the webscraper
and cleans it into data frame formats that can be fed into a predictinve ML mode.
The outputs from this model are:
- train_df.csv
- val_df.csv
- test_df.csv
Each dataframe will have all of the variables (columns) and samplevplayer-weeks
(rows) required to train/fit/predict/evaluate a given dataset.
"""

import pandas as pd
import pickle
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import gc

class globs():
    dir_players = "../data/player_weeks/"
    dir_opp = "../data/opp_weeks/"
    dir_salaries = "../data/fanduel_salaries/"
    dir_weather = "../data/nfl_weather/"
    dir_snapcounts = "../data/snapcounts/"
    dir_benchmark = "../data/fanduel_projections/"

    file_team_rename_map = "../meta_data/team_rename_map.csv"

class RenameMap():
    def __init__(self, filepath):
        df = pd.read_csv(filepath, index_col=0)
        self.rename_map = df.to_dict()[df.columns[0]]

class WeeklyStatsYear():
    """
    This class is holds a year's worth of weekly stats. The stats stored in This
    class store all of the variable inputs (X's) as well as the targets (y's),
    and in some cases, the bench mark (y_bench's) that are fed into the ML
    prediction model.
    """
    def __init__(self, year):
        self.year = year

    def read_player_data(self, filepath):
        self.df_player = pd.read_csv(filepath)
        team_rename_map = RenameMap(globs.file_team_rename_map).rename_map
        self.df_player["team"] = self.df_player["team"].replace(team_rename_map)
        if "position_fill" in self.df_player:
            del self.df_player["position_fill"]
        self.df_player = self.df_player.rename(columns={"name": "full_name"})
        self.df_player = self.df_player.reset_index()

    def read_opp_data(self, filepath):
        self.df_opp = pd.read_csv(filepath)
        team_rename_map = RenameMap(globs.file_team_rename_map).rename_map
        self.df_opp["opp_TEAM"] = self.df_opp["opp_TEAM"].replace(team_rename_map)
        self.df_opp["opp_OPP"] = self.df_opp["opp_OPP"].replace(team_rename_map)
        if "position_fill" in self.df_opp:
            del self.df_opp["position_fill"]
        self.df_opp["year"] = self.year
        self.df_opp = self.df_opp.reset_index()
        opp_cols_rename_dict = {
            "opp_week": "week",
            "opp_TEAM": "offense",
            "opp_OPP": "defense",
            "opp_opp_points": "opp_points",
            "opp_first_downs": "opp_first_downs",
            "opp_total_yds": "opp_total_yds",
            "opp_passing_yds": "opp_passing_yds",
            "opp_rushing_yds": "opp_rushing_yds",
            "opp_penalty_yds": "opp_penalty_yds",
            "opp_penalty_cnt": "opp_penalty_cnt",
            "opp_turnovers": "opp_turnovers",
            "opp_punt_cnt": "opp_punt_cnt",
            "opp_punt_yds": "opp_punt_yds",
            "opp_punt_avg": "opp_punt_avg",
            "opp_pos_time": "opp_pos_time",
            "year": "year"
        }
        self.df_opp = self.df_opp.rename(columns=opp_cols_rename_dict)

    def calc_target(self):
        """
        Create fantasy_points (the target variable) according to a
        standard scoring regime
        """
        self.df_player['fantasy_points'] = (self.df_player['passing_tds'] * 4) +\
        (self.df_player['passing_yds'] * 0.04) +\
        (self.df_player['passing_twoptm'] * 2) +\
        (self.df_player['passing_ints'] * -2) +\
        (self.df_player['rushing_tds'] * 6) +\
        (self.df_player['rushing_yds'] * 0.1) +\
        (self.df_player['rushing_twoptm'] * 2) +\
        (self.df_player['receiving_tds'] * 6) +\
        (self.df_player['receiving_yds'] * 0.1) +\
        (self.df_player['receiving_twoptm'] * 2) +\
        (self.df_player['kickret_tds'] * 6) +\
        (self.df_player['puntret_tds'] * 6) +\
        (self.df_player['fumbles_lost'] * -2)

    def calc_target_PPR(self):
        """
        Create fantasy_poiints (the target variable) according to a PPR scoring
        regime.
        """
        self.df_player['fantasy_points'] = (self.df_player['passing_tds'] * 4) +\
        (self.df_player['passing_yds'] * 0.04) +\
        (self.df_player['passing_twoptm'] * 2) +\
        (self.df_player['passing_ints'] * -2) +\
        (self.df_player['rushing_tds'] * 6) +\
        (self.df_player['rushing_yds'] * 0.1) +\
        (self.df_player['rushing_twoptm'] * 2) +\
        (self.df_player['receiving_tds'] * 6) +\
        (self.df_player['receiving_yds'] * 0.1) +\
        (self.df_player['receiving_twoptm'] * 2) +\
        (self.df_player['kickret_tds'] * 6) +\
        (self.df_player['puntret_tds'] * 6) +\
        (self.df_player['fumbles_lost'] * -2) +\
        (self.df_player['receiving_rec']) # Add in the 1 point per reception

    def calc_ratios(self):
        """
        Create pass/rus/reception ratios to be included in feature set for model.
        """
        self.df_player['passer_ratio'] = self.df_player['passing_cmp']/self.df_player['passing_att']
        self.df_player['PassRushRatio_Att'] = self.df_player['rushing_att'] / self.df_player['passing_att']
        self.df_player['PassRushRatio_Yds'] = self.df_player['rushing_yds'] / self.df_player['passing_yds']
        self.df_player['PassRushRatio_Tds'] = self.df_player['rushing_tds'] / self.df_player['passing_tds']
        self.df_player['RushRecRatio_AttRec'] = self.df_player['rushing_att'] / self.df_player['receiving_rec']
        self.df_player['RushRecRatio_Tds'] = self.df_player['rushing_tds'] / self.df_player['receiving_tds']
        self.df_player['RushRecRatio_Yds'] = self.df_player['rushing_yds'] / self.df_player['receiving_yds']

    def clean_positions(self):
        """
        Trim the dataset to include the four main offensive positions: QB, RB, WR, TE
        """
        # Determine position_fill for players missing positions
        missing = self.df_player[self.df_player.position.isna()]
        missing = missing.groupby(["id", "full_name"], as_index=False).mean()
        missing = missing[["id", "full_name", "passing_att", "rushing_att", "receiving_rec"]]
        missing.columns = ["id", "full_name", "QB", "RB", "WRTE"]
        missing = missing[(missing.QB!=0) | (missing.RB!=0) | (missing.WRTE!=0)]
        missing["position_fill"] = missing[["QB", "RB", "WRTE"]].idxmax(axis=1)
        missing = missing[["id", "position_fill"]]
        #missing["position_fill"] = missing["position_fill"].apply(lambda x: np.nan if x=="WRTE" else x)
        missing["position_fill"] = missing["position_fill"].apply(lambda x: "WR" if x=="WRTE" else x) # Assuming all WRTE's are WR instead of dropping 

        # Impute position based on 'position_fill'
        self.df_player = self.df_player.merge(missing, how='left', on='id')
        self.df_player['position'].fillna(self.df_player['position_fill'], inplace=True)
        #self.df_player['position_fill'] = self.df_player['full_name'].apply(lambda x: fill_positions(x)) # This is left over from non-working function in old code
        self.df_player['position'].fillna(self.df_player['position_fill'], inplace=True)

        # Trim dataset to include_positions
        include_positions = ['QB', 'TE', 'WR', 'RB']
        self.df_player['position'] = self.df_player['position'].str.replace('FB','RB')
        self.df_player = self.df_player[self.df_player['position'].isin(include_positions)]

    def calc_frac_nopos(self):
        frac = self.df_player.position.isna().sum() / len(self.df_player.position)
        print(frac)

    def read_salaries_data(self, filepath):
        self.df_salaries = pd.read_csv(filepath)

    def read_snapcounts_data(self, filepath):
        self.df_snapcounts = pd.read_csv(filepath)

    def read_benchmark_data(self, filepath):
        self.df_benchmark = pd.read_csv(filepath)

if __name__ == "__main__":
    data_2013 = WeeklyStatsYear(2018)
    data_2013.read_opp_data(os.path.join(globs.dir_opp, "opp_stats_2013.csv"))
    data_2013.read_player_data(os.path.join(globs.dir_players, "player_stats_2013.csv"))
    data_2013.calc_frac_nopos()
    data_2013.calc_target_PPR()
    data_2013.calc_ratios()
    data_2013.clean_positions()
    data_2013.calc_frac_nopos()

    data_2017 = WeeklyStatsYear(2018)
    data_2017.read_opp_data(os.path.join(globs.dir_opp, "opp_stats_2017.csv"))
    data_2017.read_player_data(os.path.join(globs.dir_players, "player_stats_2017.csv"))
    data_2017.calc_frac_nopos()
    data_2017.calc_target_PPR()
    data_2017.calc_ratios()
    data_2017.clean_positions()
    data_2017.calc_frac_nopos()

    print(data_2013.df_player.position.value_counts())
    print(data_2017.df_player.position.value_counts())
