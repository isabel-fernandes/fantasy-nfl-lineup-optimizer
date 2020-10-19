import sklearn.metrics as metrics
import sklearn.linear_model as lin
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from pprint import pprint
import matplotlib
from math import exp
from numpy import mean
from numpy import std
from sklearn.utils import shuffle
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.model_selection import GridSearchCV

class globs():
    dir_in = "../data/model_data/"

    file_train = "df_train.csv"
    file_val = "df_val.csv"
    file_test = "df_test.csv"

    grid_params = {
        "n_estimators": [10, 100, 500],
        "criterion": ["mse", "mae"],
        "bootstrap": [True, False]
    }

class Model():
    def __init__(self):
        pass

if __name__ == "__main__":
    model = Model()
