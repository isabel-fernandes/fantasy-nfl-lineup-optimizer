import pandas as pd
import os
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

    RESPONSE_VAR = "target"
    BENCHMARK = "benchmark"
    SPARE_POS = "TE" # This feature is redundant to [QB, RB, WR]
    CURR_WEEK = 13

    grid_params = {
        "GradBoost": {
            "n_estimators": [10,50],
            "learning_rate": [0.1,0.5]
        },
        "RandForest": {
            "n_estimators": [10, 20, 50],
            "criterion": ["mse"],
            "bootstrap": [False, True]
        }
    }

    models = {
        "GradBoost": GradientBoostingRegressor(),
        "RandForest": RandomForestRegressor()
    }


class ModelRun():
    def __init__(self):
        pass

    def read_data(self, file_train, file_val, file_test):
        self.df_train = pd.read_csv(file_train).dropna()
        self.df_val = pd.read_csv(file_val).dropna()
        self.df_test = pd.read_csv(file_test).dropna()

        self.features = list(self.df_test)
        self.features.remove(globs.RESPONSE_VAR)
        self.features.remove(globs.BENCHMARK)
        self.features.remove(globs.SPARE_POS)


    def prep_data(self):
        ss = StandardScaler()
        self.X_fit_train = self.df_train.loc[self.df_train.target_week <= globs.CURR_WEEK, self.features]
        self.y_fit_train = self.df_train.loc[self.df_train.target_week <= globs.CURR_WEEK, globs.RESPONSE_VAR]
        self.X_fit_test = self.df_train.loc[self.df_train.target_week > globs.CURR_WEEK, self.features]
        self.y_fit_test = self.df_train.loc[self.df_train.target_week > globs.CURR_WEEK, globs.RESPONSE_VAR]
        self.X_fit_train = ss.fit_transform(self.X_fit_train)
        self.X_fit_test = ss.fit_transform(self.X_fit_test)

        self.X = self.df_train.loc[:,self.features]
        self.y = self.df_train.loc[:,globs.RESPONSE_VAR]
        self.X = ss.fit_transform(self.X)

    def run_search(self):
        for model in globs.models.keys():
            regressor = globs.models[model]
            #all_accuracies = cross_val_score(estimator=regressor, X=self.X_fit_train
            gd_sr = GridSearchCV(
                estimator = regressor,
                param_grid = globs.grid_params[model],
                scoring="neg_mean_squared_error",
                cv=5,
                n_jobs=1
            )
            gd_sr.fit(self.X_fit_train, self.y_fit_train)
            best_params = gd_sr.best_params_
            print(best_params)
            best_result = gd_sr.best_score_
            best_rmse = (-gd_sr.best_score_)**(0.5)
            print("{} Best RMSE: {}".format(model, best_rmse)) 

    def run_cross_val(self):
        cv_inner = KFold(n_splits=3, shuffle=True)
        model = globs.models["RandForest"]
        space = globs.grid_params["RandForest"]
        search = GridSearchCV(model, space, scoring="accuracy", n_jobs=1, cv=cv_inner, refit=True)
        cv_outer = KFold(n_splits=10, shuffle=True)
        scores = cross_val_score(search, self.X, self.y, scoring="accuracy", cv=cv_outer, n_jobs=1)
        print("Accuracy: {} ({})".format(mean(scores), std(scores)))
        # Iterage over all model classes
        #for model in globs.models.keys():


if __name__ == "__main__":
    modelrun = ModelRun()
    modelrun.read_data(
        os.path.join(globs.dir_in, globs.file_train),
        os.path.join(globs.dir_in, globs.file_val),
        os.path.join(globs.dir_in, globs.file_test)
    )
    modelrun.prep_data()
    #modelrun.run_cross_val()
    modelrun.run_search()
