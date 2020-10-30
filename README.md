# Fantasy NFL Lineup Optimizer

This project provides optimized fantasty football lineups for Daily Fantasy Sports (DFS) Leagues such as Draft Kings or Fan Duel. Historical data is pulled from fantasydata.com to train a weekly fantasy projection model. These projections along with historical DFS salaries and scores are used to determine an optimal lineup of players for the coming week of NFL games. This information is then displayed via dashboard.

## Project Components

- Data Scraper
- Exploratory Analysis
- Projection Model
- Lineup Optimizer
- Display Dashboard

## Data Scraper

### Sources
- https://fantasydata.com/nfl/fantasy-football-leaders
- http://rotoguru1.com/cgi-bin/fyday.pl

### FanDuel Salaries
Found a existing project with a scraper for pulling weekly salary data (https://github.com/rjh336/ffb_metis) <br>
Sample: `data/fanduel_salaries/fd_salaries_2019.csv`
- Note that this sample csv does not exactly match with the definitions outlined in the variable definitions table below. Please follow the variable definitions when preparing the actual webscraper outputs.

#### Variable Definitions
| Parameter             | Descriptionn                  | Data Type | Notes              |
|-----------------------|-------------------------------|-----------|--------------------|
| Week                  | Week of season.               | Int       | 1-17               |
| Year                  | Starting year of the season   | Int       |                    |
| Name                  | First and Last name of player | String    | "Patrick Mahomes"  |
| Team                  | Team abbreviation             | String    | GB, CAR, NYG, ...  |
| Pos                   | Position of Player            | String    | QB, RB, WR, TE     |
| Opp                   | Opponent team's abbreviation  | String    | GB, CAR, NYG, ...  |
| fd_points             | FanDuel points scored         | Float     |                    |
| fg_salary             | FanDuel salary                | Int       |                    |

### Weekly Player Stat Requirements
If a stat (such as passing stats) is not applicable to a particular player, then the value will be 0, not empty. <br>
Sample: `data/weekly_players/sample_weekly.csv`
- Note that this sample csv does not exacly match with the definitions outlined in the variable definitions table below. Please follow the variable definitions when preparing the actual web-scraper outputs.

#### Variable Definitions
| Parameter             | Descriptionn                  | Data Type | Notes              |
|-----------------------|-------------------------------|-----------|--------------------|
| Name                  | First and Last name of player | String    | "Patrick Mahomes"  |
| Team                  | Team abbreviation             | String    | GB, CAR, NYG, ...  |
| Pos                   | Position of Player            | String    | QB, RB, WR, TE     |
| Wk                    | Week of season                | Int       | 1-17               |
| Opp                   | Opponent team's abbreviation  | String    | GB, CAR, NYG, ...  |
| Year                  | Starting year of the season   | Int       |                    |
| Status                | Injury Status of Player       | String    | Q, O, IR, ,<-n/a   |
| TeamScore             | Player's team's score in game | Int       |                    |
| OppScore              | Opponent team's score in game | Int       |                    |
| PassingYds            | Passing yards                 | Int       |                    |
| PassingTD             | Passing touchdowns            | Int       |                    |
| Int                   | Interceptions                 | Int       |                    |
| PassingAtt            | Passing Attempts              | Int       |                    |
| Cmp                   | Completions                   | Int       |                    |
| RushingAtt            | Rushing attempts              | Int       |                    |
| RushingYds            | Rushing yards                 | Int       |                    |
| RushingTD             | Rushing touchdowns            | Int       |                    |
| Rec                   | Receptions                    | Int       |                    |
| Tgt                   | Targets                       | Int       |                    |
| ReceivingYds          | Receiving yards               | Int       |                    |
| ReceivingTD           | Receiving touchdowns          | Int       |                    |
| FL                    | Fumbles                       | Int       |                    |

## Exploratory Analysis
- Generate and explore features that are correlated with fantasy score
- Generate a weekly predictive model of score for each postion. Let's do a combined model for QB, RB, WR

## Projection model

### `prep_model_data.py`
#### `WeeklyStatsYear` class
- Attributes:
    - `X_vars`: list of predictor variables
    - `y_var`: name of target variable
    - `b_var`: name of benchmark variable
    - `df`: full dataset containing all players/years/weeks rows and all predictor/target/benchmard/meta columns.
    - `df_train`: training data subset for fitting model with cross-validation
    - `df_val`: validation data subset for selecting model class
    - `df_test`: test data subset for evaluating model performance against benchmark
- Methods:
    - `read_player_data()`
    - `read_opp_data()`
    - `calc_target()`
    - `create_nfl_features()`: wrapper for all of the featurzing helper functions
        - `get_cumul_stats_time_weighted()`
        - `get_cumul_mean_stats()`
        - `get_trend()`
        - `defensive_ptsallow()`
        - `weekly_player_weights()`
    - `clean_salaries()`
    - `read_salaries_data()`
    - `merge_salaries()`
    - `add_year()`: This is included in pda.py because 'Year column got lost when I called create_nfl_features() on each dataframe, so I
    am adding it back.' This method might not be necessary, but I am keeping it for now and might remove once I have a working code and
    determine it is not needed.
    - `read_snapcounts_data()`
    - `merge_snapcounts()`
    - `read_weather_data()`
    - `merge_weather()`

### `learn_model.py`
Runs a training trains model with cross-validation for hyperparameter selection,
validation with model class selection, and test for final model performance evaluation.
#### Model Classes:
The following model classes were tested with the corresponding hyperparameter
explored through grid search.
- Gradient Boosting Regressor
    - `n_estimators`: `[100, 200, 500]`
    - `learning_rate`: `[0.01,0.02,0.05]`
- Random Forest Regressor
    -  `n_estimators`: `[100,200,500]`
    - `criterion`: `"mse"`
    - `bootstrap`: `[True, False]`
#### Train, Val, Test Split
The model training, validation, and testing was carried out on NFL season 2013-2019.
- `search_models()`
    - Initial training with cross-validation was carried out on seasons 2013-2017. Cross-validation
    was carried using a time-series split on seasons 2013-2017 with 5 splits, scored on
    minimizing the mean squared error.
- `select_model()`
    - After cross-validation selects the optimal hyperparameters for each model
    class, a final validation is carried out on the with scoring predictions on
    the 2018 season. The model class is selected for the model with the highest
    RMSE on the 2018 validation dataset. For this analysis, Gradient Boosting
    Regressor was selected.
- `test_model()`
    - Evaluates the performance of model data on the test data in 2019 season.
    Model class with the cross-validation selected parameters is fit to all
    seasons 2013-2018, and tested on the 2019 season player scores. These predictions
    are compared against a benchmark of ESPN.com scoring projections. At the moment,
    ESPN scoring projections are out-scoring our model with an RMSEs of 8 and 6,
    respectively. It is likely that our model is out-performed by the ESPN
    projections because the model is fit on the entire set of players, while
    the ESPN projections dataset only contains the top 100 players in the league.
    In order to improve performance of our model, training and validation should
    be carried out on a subset of players that reflects those used in the
    benchmarked comparison.

## Lineup Optimizer
The lineup optimizer is still a work-in-progress. However, the plan is to carry
out an optimization on the predicted scores to select optimal player lineups
for daily fantasy sports leagues. The optimization problem will be formulated as
a Markov Decision Process as follows:
### States
- Projection
- Salary
- Injury
- Team
- Postion
- Week
### Actions
- Lineup Selection
### Reward
- Money Earned

Because of the large state and action space, an explicit representation of the
environment is not possible. Therefore, the optimal policy will be learned using
a version of reinforcement learning. Probably Q-learning, similar to previous 
work carried out by [1].

## Display dashboard
