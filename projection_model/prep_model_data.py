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

    def read_salaries_data(self, filepath):
        self.df_salaries = pd.read_csv(filepath)

    def read_snapcounts_data(self, filepath):
        self.df_snapcounts = pd.read_csv(filepath)

    def read_benchmark_data(self, filepath):
        self.df_benchmark = pd.read_csv(filepath)

if __name__ == "__main__":
    data_2013 = WeeklyStatsYear(2013)
    data_2013.read_opp_data(os.path.join(globs.dir_opp, "opp_stats_2013.csv"))
    data_2013.read_player_data(os.path.join(globs.dir_players, "player_stats_2013.csv"))
    print(data_2013.df_opp.head())
    print(data_2013.df_player.head())
