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
### `PredictiveModel` class
#### Attributes:
- `X_vars`: list of predictor variables
- `y_var`: name of target variable
- `b_var`: name of benchmark variable
- `df`: full dataset containing all players/years/weeks rows and all predictor/target/benchmard/meta columns.
- `df_train`: training data subset for fitting model with cross-validation
- `df_val`: validation data subset for selecting model class
- `df_test`: test data subset for evaluating model performance against benchmark
#### Methods:
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

## Lineup Optimizer

## Display dashboard
