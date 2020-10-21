import pandas as pd
import os
import operator
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
from sklearn.model_selection import KFold, TimeSeriesSplit
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
            "n_estimators": [50,100,200],
            "learning_rate": [0.001,0.005,0.02,0.1,0.5]
        },
        "RandForest": {
            "n_estimators": [50,100,200],
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
        self.df_train = pd.read_csv(file_train).dropna().sort_values(by=["year","target_week"])
        self.df_val = pd.read_csv(file_val).dropna().sort_values(by=["year","target_week"])
        self.df_test = pd.read_csv(file_test).dropna().sort_values(by=["year","target_week"])

        #self.df_train = self.df_train.drop("year", axis=1)
        #self.df_val = self.df_val.drop("year", axis=1)
        #self.df_test = self.df_test.drop("year", axis=1)

        self.features = list(self.df_test)
        self.features.remove(globs.RESPONSE_VAR)
        self.features.remove(globs.BENCHMARK)
        self.features.remove(globs.SPARE_POS)


    def prep_data(self):
        ss = StandardScaler()
        #self.X_fit_train = self.df_train.loc[self.df_train.target_week <= globs.CURR_WEEK, self.features]
        #self.y_fit_train = self.df_train.loc[self.df_train.target_week <= globs.CURR_WEEK, globs.RESPONSE_VAR]
        #self.X_fit_test = self.df_train.loc[self.df_train.target_week > globs.CURR_WEEK, self.features]
        #self.y_fit_test = self.df_train.loc[self.df_train.target_week > globs.CURR_WEEK, globs.RESPONSE_VAR]
        #self.X_fit_train = ss.fit_transform(self.X_fit_train)
        #self.X_fit_test = ss.fit_transform(self.X_fit_test)

        self.X_train = self.df_train.loc[:,self.features]
        self.y_train = self.df_train.loc[:,globs.RESPONSE_VAR]
        self.X_train = ss.fit_transform(self.X_train)

        self.X_val = self.df_val.loc[:,self.features]
        self.y_val = self.df_val.loc[:,globs.RESPONSE_VAR]
        self.X_val = ss.fit_transform(self.X_val)

        self.X_test = self.df_test.loc[:,self.features]
        self.y_test = self.df_test.loc[:,globs.RESPONSE_VAR]
        self.X_test = ss.fit_transform(self.X_test)

    def search_models(self):
        self.searches = {}
        for model in globs.models.keys():
            regressor = globs.models[model]
            search = GridSearchCV(
                estimator = regressor,
                param_grid = globs.grid_params[model],
                scoring="neg_mean_squared_error",
                cv=TimeSeriesSplit(n_splits=5),
                n_jobs=1
            )
            search.fit(self.X_train, self.y_train)
            best_params = search.best_params_
            best_result = search.best_score_
            best_rmse = (-search.best_score_)**(0.5)
            print("{} Best RMSE: {:.3f}, Params: {}".format(model, best_rmse, best_params))
            self.searches[model] = search

    def select_model(self):
        models = {}
        for model, search in self.searches.items():
            y_pred = search.predict(self.X_val)
            mse = metrics.mean_squared_error(self.y_val, y_pred)
            rmse = mse**(0.5)
            print("{} Val RMSE: {:.3f}".format(model, rmse))
            models[model] = rmse
        best_model_class = min(models.items(), key=operator.itemgetter(1))[0] # Lowest RMSE is best model
        self.best_model = self.searches[best_model_class]
        self.best_model_info = {
            "class": best_model_class,
            "params": self.searches[best_model_class].best_params_
        }

    def test_model(self):
        # Fit selected model on Train and Val Combined Data
        df = pd.concat([self.df_train, self.df_val], axis=0)
        X_fit = df.loc[:,self.features]
        y_fit = df.loc[:,globs.RESPONSE_VAR]
        self.best_model.fit(X_fit, y_fit)

        X_test = self.df_test.loc[:,self.features]
        y_test = self.df_test.loc[:,globs.RESPONSE_VAR]
        y_bench = self.df_test.loc[:,globs.BENCHMARK]
        y_pred = self.best_model.predict(X_test)
        mse = metrics.mean_squared_error(y_test, y_pred)
        rmse = mse**(0.5)
        print("{} Test RMSE: {:.3f}".format(self.best_model_info["class"], rmse))
        mse_bench = metrics.mean_squared_error(y_test, y_bench)
        rmse_bench = mse_bench**(0.5)
        print("Benchmark RMSE: {:.3f}".format(rmse_bench))

if __name__ == "__main__":
    modelrun = ModelRun()
    modelrun.read_data(
        os.path.join(globs.dir_in, globs.file_train),
        os.path.join(globs.dir_in, globs.file_val),
        os.path.join(globs.dir_in, globs.file_test)
    )
    modelrun.prep_data()
    modelrun.search_models()
    modelrun.select_model()
    modelrun.test_model()
