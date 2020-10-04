import pandas as pd
import numpy as np
import os

# Define Inputs and Outputs
dir_in = "../raw_data/weekly/"

dir_out = "../data/"
file_out = "sample_weekly.csv"

# Define Functions
def import_week(filepath):
    # TODO: eventually would like to make this object-oriented
    # assumes filepath of: [dir_in]/week{}.csv

    # Read data
    df = pd.read_csv(filepath)

    # Add Week Feature to Dataframe
    wk = int(filepath.split("week")[-1].split(".")[0])
    df["Week"] = wk

    return df

def import_season(dir_in):
    for file_in in os.listdir(dir_in):
        df_wk = import_week(os.path.join(dir_in, file_in))

        if "df_ssn" not in locals():
            df_ssn = df_wk.copy()
        else:
            df_ssn = pd.concat([df_ssn, df_wk], axis=0)

    return df_ssn

def import_all_seasons(dir_in):
    for year  in os.listdir(dir_in):
        df_ssn = import_season(os.path.join(dir_in, year))
        df_ssn["Year"] = int(year)

        if "df_all" not in locals():
            df_all = df_ssn.copy()
        else:
            df_all = pd.concat([df_all, df_ssn], axis=0)

    return df_all

def export_data(filepath):
    df.to_csv(filepath, index=False)

    return


# Run Code
df = import_all_seasons(dir_in)

export_data(os.path.join(dir_out, file_out))
