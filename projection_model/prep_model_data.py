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
    dir_players = "./data/player_weeks/"
    dir_opp = "./data/opp_weeks/"
    dir_salaries = "./data/fanduel_salaries/"
    dir_weather = "./data/nfl_weather/"
    dir_snapcounts = "./data/snapcounts/"
    dir_benchmark = "./data/fanduel_projections/"

    file_team_rename_map = "./meta_data/team_rename_map.csv"

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

    def read_player_data(filepath):
        self.df_player = pd.read_csv(filepath)

    def read_opp_data(filepath):
        self.df_opp = pd.read_csv(filepath)

    def read_salaries_data(filepath):
        self.df_salaries = pd.read_csv(filepath)

    def read_snapcounts_data(filepath):
        self.df_snapcounts = pd.read_csv(filepath)

    def read_benchmark_data(filepath):
        self.df_benchmark = pd.read_csv(filepath)
