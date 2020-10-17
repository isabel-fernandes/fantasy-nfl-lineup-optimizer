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

class WeeklyStatsYear():
    """
    This class is holds a year's worth of weekly stats. The stats stored in This
    class store all of the variable inputs (X's) as well as the targets (y's),
    and in some cases, the bench mark (y_bench's) that are fed into the ML
    prediction model.
    """
    def __init__(self, year):
        self.year = year
    
