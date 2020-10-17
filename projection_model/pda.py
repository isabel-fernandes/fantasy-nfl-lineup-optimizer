# This is workspace for developing modeling fitting code before cleaning up

import pandas as pd
import pickle
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import gc

# Load in data
# Player_stats and Opp_stats files have been pulled from nflgame API via the
# nflgame_acquire.ipynb (scrape_nflgames.py)

dir_in = "../data/"
dir_players = "../data/player_weeks/"
dir_opps = "../data/opp_weeks/"
dir_fanduel = "../data/fanduel_salaries/"
dir_nflweather = "../data/nfl_weather/"
files = os.listdir(dir_in)

class PredictiveModel(object):
    def __init__(self):
        self.years = []
        self.X_vars = []
        self.y_var = "fd_points"
        self.b_var = "fd_proj"


class WeeklyStats:
    def __init__(self, filepath):
        self.fpath = filepath
        self.year = int(filepath.split("_")[-1].split(".")[0])

    def read_player_data(self):
        df = pd.read_csv(self.fpath, index_col=0)
        df['team'] = df['team'].str.replace('JAX','JAC')
        df['team'] = df['team'].str.replace('LAC','SD')
        df['team'] = df['team'].str.replace('STL','LA')
        if "position_fill" in df:
            del df['position_fill']
        df['year'] = self.year
        df = df.rename(columns={"name": "full_name"})
        df = df.reset_index()
        return df

    def read_opp_data(self):
        df = pd.read_csv(self.fpath, index_col=0)
        df['year'] = self.year
        df['opp_TEAM'] = df['opp_TEAM'].str.replace('JAX','JAC')
        df['opp_OPP'] = df['opp_OPP'].str.replace('JAX','JAC')
        df['opp_TEAM'] = df['opp_TEAM'].str.replace('LAC','SD')
        df['opp_OPP'] = df['opp_OPP'].str.replace('LAC','SD')
        df['opp_TEAM'] = df['opp_TEAM'].str.replace('STL','LA')
        df['opp_OPP'] = df['opp_OPP'].str.replace('STL','LA')
        df = df.reset_index()
        return df

player_stats_files = [WeeklyStats(os.path.join(dir_players,f)) for f in os.listdir(dir_players)]
opp_stats_files = [WeeklyStats(os.path.join(dir_opps,f)) for f in os.listdir(dir_opps)]

player_dfs = {}
for pfile in player_stats_files:
    player_dfs[pfile.year] = pfile.read_player_data()


opp_dfs = {}
for ofile in opp_stats_files:
    opp_dfs[ofile.year] = ofile.read_opp_data()

#new_opp_cols = ['offense', 'defense', 'opp_first_downs', 'opp_points',
#       'opp_passing_yds', 'opp_penalty_cnt', 'opp_penalty_yds', 'opp_pos_time',
#       'opp_punt_avg', 'opp_punt_cnt', 'opp_punt_yds', 'opp_rushing_yds',
#       'opp_total_yds', 'opp_turnovers', 'week', 'year']

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

for year, df in opp_dfs.items():
    #df.columns = new_opp_cols
    df = df.rename(columns=opp_cols_rename_dict)
    opp_dfs[year] = df

# Clean data and create target variable
data = pd.concat(player_dfs.values())
missing_positions = data[data.isnull()]
means = missing_positions.groupby(['id','full_name'], as_index=False).mean()
means = means[['id','full_name','passing_att', 'rushing_att', 'receiving_rec']]
means.columns = ['id','full_name','QB','RB','WRTE']
means = means[(means.QB != 0) | (means.RB != 0) | (means.WRTE != 0)]
means['position_fill'] = means[['QB','RB','WRTE']].idxmax(axis=1)
means = means[['id','position_fill']]
means['position_fill'] = means['position_fill'].apply(lambda x: np.nan if x == 'WRTE' else x)


# Modeule not included in the git repo
#from data.missing_plyrs import missing_WRTE

def fill_positions(name):
    """Fill missing positions for players who are retired. The nflgame players.json
    will not update these positions, nor are the positions available by scraping each
    player's nfl.com profile url."""

    '''
    try:
        pos = missing_WRTE[name]
        return pos
    except KeyError:
        return ''
    '''
    return ""

def clean(player_stats, year, imputed):
    """Create fantasy_points (the target variable) according to a standard scoring regime.
       Create pass/rush/reception ratios to be included in feature set for model.
       Trim the dataset to include the four main offensive positions: QB, RB, WR, TE."""

    player_stats['fantasy_points'] = (player_stats['passing_tds'] * 4) +\
    (player_stats['passing_yds'] * 0.04) +\
    (player_stats['passing_twoptm'] * 2) +\
    (player_stats['passing_ints'] * -2) +\
    (player_stats['rushing_tds'] * 6) +\
    (player_stats['rushing_yds'] * 0.1) +\
    (player_stats['rushing_twoptm'] * 2) +\
    (player_stats['receiving_tds'] * 6) +\
    (player_stats['receiving_yds'] * 0.1) +\
    (player_stats['receiving_twoptm'] * 2) +\
    (player_stats['kickret_tds'] * 6) +\
    (player_stats['puntret_tds'] * 6) +\
    (player_stats['fumbles_lost'] * -2)

    player_stats['passer_ratio'] = player_stats['passing_cmp']/player_stats['passing_att']
    player_stats['PassRushRatio_Att'] = player_stats['rushing_att'] / player_stats['passing_att']
    player_stats['PassRushRatio_Yds'] = player_stats['rushing_yds'] / player_stats['passing_yds']
    player_stats['PassRushRatio_Tds'] = player_stats['rushing_tds'] / player_stats['passing_tds']
    player_stats['RushRecRatio_AttRec'] = player_stats['rushing_att'] / player_stats['receiving_rec']
    player_stats['RushRecRatio_Tds'] = player_stats['rushing_tds'] / player_stats['receiving_tds']
    player_stats['RushRecRatio_Yds'] = player_stats['rushing_yds'] / player_stats['receiving_yds']

    player_stats = player_stats.merge(imputed, how='left', on='id')
    player_stats['position'].fillna(player_stats['position_fill'], inplace=True)
    player_stats['position_fill'] = player_stats['full_name'].apply(lambda x: fill_positions(x))
    player_stats['position'].fillna(player_stats['position_fill'], inplace=True)

    include_positions = ['QB', 'TE', 'WR', 'RB']
    player_stats['position'] = player_stats['position'].str.replace('FB','RB')
    player_stats = player_stats[player_stats['position'].isin(include_positions)]
    return player_stats

# Create dictionary with keys as year of the NFL season and values
# as a dataframe containing game summary stats for all players in that season
player_dfs = {year:clean(df, year, means) for year, df in player_dfs.items()}

for year in range(2013,2018):
    print(player_dfs[year].shape)

# Feature Engineering
# These are the game summary stats relevant to QB, RB, WR, and TE positions.

stat_cols = ['fumbles_lost', 'fumbles_rcv', 'fumbles_tot','fumbles_trcv', 'fumbles_yds',
       'passing_att', 'passing_cmp', 'passing_ints', 'passing_tds', 'passer_ratio',
       'passing_twopta', 'passing_twoptm', 'passing_yds',
       'puntret_tds','puntret_avg', 'puntret_lng', 'puntret_lngtd', 'puntret_ret',
       'receiving_lng', 'receiving_lngtd','receiving_rec', 'receiving_tds', 'receiving_twopta',
       'receiving_twoptm', 'receiving_yds', 'rushing_att', 'rushing_lng',
       'rushing_lngtd', 'rushing_tds', 'rushing_twopta', 'rushing_twoptm',
       'rushing_yds','fantasy_points',
        'PassRushRatio_Att','PassRushRatio_Yds','PassRushRatio_Tds','RushRecRatio_AttRec',
        'RushRecRatio_Tds','RushRecRatio_Yds']

def trim_sort(df):
    df = df.sort_values(['id','week'])
    df = df[stat_cols+['id','week','team','position','full_name']]
    return df

def get_trend(df_in):
    """Compute a three-week trend for each game statistic, for each player."""
    # Drop non-ID identifier columns
    drop_cols = ["team", "position", "full_name"]
    groupby_cols = ["id"]
    df = df_in[[c for c in df_in if c not in drop_cols]]

    # compute 3-week and 2-week points deltas
    deltas = df.groupby(groupby_cols).pct_change()
    deltas = deltas.add_prefix('chg_')
    deltas = pd.concat([df, deltas], axis=1)
    deltas2 = deltas.groupby(groupby_cols)[deltas.columns].shift(1).fillna(0)
    deltas3 = deltas.groupby(groupby_cols)[deltas.columns].shift(2).fillna(0)
    deltas2 = deltas2.add_prefix('per2_')
    deltas3 = deltas3.add_prefix('per3_')
    trend_df = pd.concat([deltas, deltas2, deltas3], axis=1)
    # average prior three deltas to get trend
    for col in stat_cols:
        name = 'trend_'+col
        trend_df[name] = trend_df[['chg_'+col,'per2_chg_'+col,'per3_chg_'+col]].mean(axis=1).fillna(0)
    return trend_df

def get_cumul_mean_stats(df, weeks):

    """Create a rolling mean for each statistic by player, by week."""

    weeks_stats_mean = []
    for week in weeks:
        tmp = df[df.week <= week]
        tmp = tmp.groupby(['id'])[stat_cols].mean().reset_index()
        tmp = tmp.add_suffix('_mean')
        tmp['week'] = week
        weeks_stats_mean.append(tmp)
    cumavg_stats = pd.concat(weeks_stats_mean)
    cumavg_stats = cumavg_stats.rename(columns={'id_mean':'id'})
    return cumavg_stats

def get_cumul_stats_time_weighted(df, weeks):

    """Create a rolling time-wegihted mean for each statistic by player, by week."""

    weeks_stats_mean_wgt = []
    for week in weeks:
        tmp1 = df[df.week <= week]
        mult = lambda x: np.asarray(x) * np.asarray(tmp1.week)
        tmp = tmp1[['id']+stat_cols].set_index('id').apply(mult).reset_index()
        tmp = tmp.groupby(['id'])[stat_cols].mean().reset_index()
        tmp = tmp.add_suffix('_wgtmean')
        tmp['week'] = week
        weeks_stats_mean_wgt.append(tmp)
    cumavg_stats_wgt = pd.concat(weeks_stats_mean_wgt)
    cumavg_stats_wgt = cumavg_stats_wgt.rename(columns={'id_wgtmean':'id'})
    return cumavg_stats_wgt

def defensive_ptsallow(matchups, weeks, weighted=False):

    """ Compute the mean weekly points given up by each defense to each position.
        Parameters:
                    matchups: dataframe of matchups between offensive player, and
                              defensive opponent.
                    weeks:    list of weeks in the season.
                    weighted: boolean. If true, compute weekly points allowed according
                              to player-weighted fantasy points.
    """

    agg_col = 'fantasy_points'
    output_name = 'defensive_matchup_allowed'
    if weighted:
        agg_col = 'weighted_fantasy_points'
        output_name = 'defensive_matchup_allowed_wgt'
    # compute weekly cumulative mean points allowed by each defense
    defense_ranks_dfs = []
    for week in weeks:
        matchweek = matchups[matchups.week <= week]
        # weekly sum of pts allowed by a given defense to each position
        weekly_sums = matchweek.groupby(['week','defense','position'])[agg_col].sum().reset_index()
        # season-to-date mean of weekly sums for each position
        defense_pts_allowed = weekly_sums.groupby(['defense','position'])[agg_col].mean().reset_index()
        defense_pts_allowed = defense_pts_allowed.rename(columns={agg_col:output_name})
        defense_pts_allowed['week'] = week
        defense_ranks_dfs.append(defense_pts_allowed)
    defense_ranks = pd.concat(defense_ranks_dfs)
    return defense_ranks

def weekly_player_weights(matchups, weeks):

    """Calculate season-to-date (STD) weekly fantasy points rankings by position."""

    player_weights = []
    for week in weeks:
        mask = (matchups.week <= week)
        # each player's mean fantasy points STD
        std_mean = matchups[mask][['id','team','position','fantasy_points','defense']]
        std_mean = std_mean.groupby(['position','id'], as_index=False).mean()

        # each player's weight in a given week with respect to their position.
        # This is the STD mean max-normalized for the current week.
        week_max_position = std_mean.groupby('position', as_index=False).max()
        week_max_position = week_max_position[['position','fantasy_points']]
        week_max_position.columns = ['position','fp_max']
        weekly_weights = std_mean.merge(week_max_position,how='left',on='position')
        weekly_weights['player_weight'] = weekly_weights['fantasy_points'] / weekly_weights['fp_max']
        weekly_weights['week'] = week
        player_weights.append(weekly_weights)
    player_weights = pd.concat(player_weights)
    return player_weights[['id','week','position','player_weight']]

def create_nfl_features(player_stats_orig, opp_stats_orig):

    """Wrapper function that calls all helpers to create custom player and team
       defense stats. This function will return a new dataframe that has merged
       all of the custom stats described in the helper functions for each player.

       Parameters:
                   player_stats_orig: game summary actuals for each player weekly
                   opp_stats_orig:    matchups for each game (can substitute with
                                      a schedule with player_id, offense, defense, week)"""

    player_stats_trimmed = trim_sort(player_stats_orig)
    weeks = sorted(player_stats_trimmed.week.unique().tolist())

    # create offensive player stats
    trend_df         = get_trend(player_stats_trimmed)
    cumavg_stats     = get_cumul_mean_stats(player_stats_trimmed, weeks)
    cumavg_stats_wgt = get_cumul_stats_time_weighted(player_stats_trimmed, weeks)

    # create matchups and defensive opponent stats
    matchup_cols = ['id', 'week', 'team','position', 'full_name', 'offense', 'defense','fantasy_points']
    sched             = opp_stats_orig[['offense','defense','week']]
    matchups          = player_stats_trimmed.merge(sched, how='left',
                                                   left_on=['week','team'],
                                                   right_on=['week','offense'])[matchup_cols]
    defense_ranks     = defensive_ptsallow(matchups, weeks)
    player_weights    = weekly_player_weights(matchups, weeks)
    player_weights['inverse'] = 1/player_weights.player_weight
    matchups_wgts     = matchups.merge(player_weights, how='left', on=['id','week','position'])
    matchups_wgts['weighted_fantasy_points'] = matchups_wgts['fantasy_points'] * matchups_wgts['inverse']
    defense_ranks_wgt = defensive_ptsallow(matchups_wgts, weeks, weighted=True)

    ## merge features

    # shift target variable, week, and defensive opponent
    matchups['target_defense'] = matchups.sort_values(['id','week']).groupby('id')['defense'].shift(-1)
    matchups['target'] = matchups.sort_values(['id','week']).groupby('id')['fantasy_points'].shift(-1)
    matchups['target_week'] = matchups.sort_values(['id','week']).groupby('id')['week'].shift(-1)

    # drop week 1
    matchups.dropna(inplace=True)

#     # fill in zeros for players with missing historical stats
#     matchups.fillna(0, inplace=True)

    # merge player weights to player performances
    matchups = matchups.merge(player_weights, on=['id','week','position'])

    # merge defense rankings to player performances
    defense_ranks_all = defense_ranks.merge(defense_ranks_wgt, on=['defense', 'position', 'week'])
    defense_ranks_all = defense_ranks_all.rename(columns={'defense':'target_defense'})
    matchups = matchups.merge(defense_ranks_all, how='left', on=['target_defense','position','week']).dropna()

    # merge trend, average, and weighted avg stats to player performances
    avgs = cumavg_stats.merge(cumavg_stats_wgt,how='inner',on=['id','week'])
    matchups = matchups.merge(avgs, how='left', on=['id','week'])
    trend_cols = ['id','week']+[col for col in trend_df if col not in matchups.columns]
    td = trend_df[trend_cols]
    matchups = matchups.merge(td, how='inner', on=['id','week'])
    for col in trend_df.columns:
        matchups[col].fillna(0, inplace=True)

    # create extra player attributes and merge to make model-ready df
    attribs = ['id','birthdate','years_pro','height','weight','position','profile_url','last_name','number']
    #player_attributes = player_stats_orig[attribs]
    player_attributes = player_stats_orig[[c for c in player_stats_orig if c in attribs]]
    player_attributes.drop_duplicates(['id'],inplace=True)
    player_attributes['birthdate'] = pd.to_datetime(player_attributes['birthdate'])
    player_attributes['age'] = player_attributes['birthdate'].apply(lambda x: (datetime.today() - x).days/365)
    position_dummies = pd.get_dummies(player_attributes['position'])
    player_attributes = pd.concat([position_dummies, player_attributes], axis=1).drop(['position'],axis=1)

    # final cleaning
    model_df = player_attributes.merge(matchups, how='right',on='id')
    model_df.replace([-np.inf,np.inf], 0, inplace=True)
    return model_df



nfl_dfs = {year:create_nfl_features(df, opp_dfs[year]) for year, df in player_dfs.items()}

# Merge FanDuel Salaries
path = dir_fanduel
files = os.listdir(path)
fanduel_dfs = {}
for fn in files:
    yr = int(re.sub('[^0-9]', '', fn))
    fanduel_dfs[yr] = pd.read_csv(path+fn)

def clean_salaries(df, year):
    positions = ['QB', 'RB', 'WR', 'TE']
    df['FirstName'] = df['FirstName'].str.strip()
    df['LastName'] = df['LastName'].str.strip()
    df['full_name'] = df['LastName']+' '+df['FirstName']
    df = df[df.Pos.isin(positions)].fillna(0)[['Week','Team','full_name','fd_points','fd_salary']]
    df.columns = ['week','team','full_name','fd_points','fd_salary']
    df['week'] = pd.to_numeric(df['week'])
    df['fd_points'] = pd.to_numeric(df['fd_points'])
    df['fd_salary'] = pd.to_numeric(df['fd_salary'])
    df['team'] = df['team'].str.upper()
    df['team'] = df['team'].str.replace('KAN','KC')
    df['team'] = df['team'].str.replace('GNB','GB')
    df['team'] = df['team'].str.replace('LAR','LA')
    df['team'] = df['team'].str.replace('STL','LA')
    df['team'] = df['team'].str.replace('TAM','TB')
    df['team'] = df['team'].str.replace('SFO','SF')
    df['team'] = df['team'].str.replace('NOR','NO')
    df['team'] = df['team'].str.replace('NWE','NE')
    df['team'] = df['team'].str.replace('SDG','SD')
    df['team'] = df['team'].str.replace('LAC','SD')
    return df

def merge_salaries(players, salaries):
    new_players = {}
    for year in players.keys():
        players_year = players[year]
        salaries_year = clean_salaries(salaries[year], year)
        players_teams = set(players_year.team)
        salaries_teams = set(salaries_year.team)
        # check that there are no team naming conflicts
        print(year, salaries_teams ^ players_teams)
        salary_merge = players_year.merge(salaries_year,how='left',on=['week','full_name','team'])
        new_players[year] = salary_merge.fillna(0)
    return new_players

nfl_fanduel_dfs = merge_salaries(nfl_dfs, fanduel_dfs)

# Year column got lost when I called create_nfl_features() on
# each dataframe, so I am adding it back

def add_year(df, yr):
    df['year'] = yr
    return df

for year in nfl_fanduel_dfs.keys():
    df_year = nfl_fanduel_dfs[year]
    nfl_fanduel_dfs[year] = add_year(df_year, year)


# TODO: The scraper for snap counts is not include in the git repo!!!
# Merge Snap Counts
# Snapcounts are the number of times a player is on the field for a ply.
# Football outsiders has a historical database of weekly snap counts for each player.

def merge_snap_counts(dfs):
    path = './data/FO_data/SnapCounts/'
    SC_files = os.listdir(path)

    SC_dfs = []
    for fn in SC_files:
        week = int(fn[:2])
        year = int(fn[3:7])
        df = pd.read_csv(path+fn)
        df['week'] = week
        df['year'] = year
        SC_dfs.append(df)
    sc = pd.concat(SC_dfs)

    sc['number'] = pd.to_numeric(sc.Player.str.replace('[^0-9]',''))
    sc['last_name'] = sc.Player.str.replace('[A-Za-z\s]+\.','')
    sc['last_name'] = sc.last_name.str.replace('[^A-Za-z\s]','').str.strip()
    sc['started'] = sc['Started'].apply(lambda x: 1 if x=='YES' else 0)
    sc['offensive_snap_pct'] = pd.to_numeric(sc['Off Snap Pct'].str.replace('[^0-9]',''),
                                             downcast='float')
    sc['offensive_snap_tot'] = sc['Off Snaps']
    sc['position'] = sc.Position.str.replace('FB','RB').str.strip()
    sc['team'] = sc['Team'].str.replace('LARM/STL','LA')
    sc['team'] = sc['team'].str.replace('LAR','LA')
    sc['team'] = sc['team'].str.replace('LAC','SD').str.strip()

    sc = sc[sc.position.isin(['QB','RB','WR','TE'])]
    sc = sc[['number','last_name','started','offensive_snap_pct',
             'offensive_snap_tot','position','team','week','year']]
    new_dfs = {}
    for year, df in dfs.items():
        merge_df = df.merge(sc, on=['last_name','team','week','year','position'])
        new_dfs[year] = merge_df
    return new_dfs

# ***** For now just making snapcount merged df a COPY
nfl_fd_sc_dfs = nfl_fanduel_dfs.copy()

# Merge gameday weather forecasts
def merge_weather(dfs):
    #from data.nfl_teams import team_dict # TODO: convert this to a meta data file
    team_dict = {
        "Cardinals": "ARI",
        "Falcons": "ATL",
        "Ravens": "BAL",
        "Bills": "BUF",
        "Panthers": "CAR",
        "Bears": "CHI",
        "Bengals": "CIN",
        "Browns": "CLE",
        "Cowboys": "DAL",
        "Broncos": "DEN",
        "Lions": "DET",
        "Packers": "GB",
        "Texans": "HOU",
        "Colts": "IND",
        "Jaguars": "JAX",
        "Chiefs": "KC",
        "Dolphins": "MIA",
        "Vikings": "MIN",
        "Patriots": "NE",
        "Saints": "NO",
        "Giants": "NYG",
        "Jets": "NYJ",
        "Raiders": "OAK",
        "Eagles": "PHI",
        "Steelers": "PIT",
        "Chargers": "SD",
        "49ers": "SF",
        "Seahawks": "SEA",
        "Rams": "LA",
        "Buccaneers": "TB",
        "Titans": "TEN",
        "Redskins": "WAS"
    }
    path = dir_nflweather
    weather_files = os.listdir(path)
    weather_dfs = []
    for fn in weather_files:
        week = re.findall('_[0-9]+\.',fn)
        week = re.sub('[^0-9]','',str(week))
        year = fn[:4]
        df = pd.read_csv(path+fn)
        df['week'] = int(week)
        df['year'] = int(year)
        weather_dfs.append(df)
    weather = pd.concat(weather_dfs)

    weather['team1'] = weather['team1'].apply(lambda x: team_dict[x])
    weather['team2'] = weather['team2'].apply(lambda x: team_dict[x])

    weather['wind_conditions'] = pd.to_numeric(weather['wind_conditions'].str.replace('[^0-9]',''))
    weather['indoor_outdoor'] = weather['weather_forecast'].apply(lambda x: 1 if 'DOME' in x else 0)

    weather1 = weather[['team1','wind_conditions','indoor_outdoor','week','year']]
    weather1.columns = ['team','wind_conditions','indoor_outdoor','week','year']
    weather2 = weather[['team2','wind_conditions','indoor_outdoor','week','year']]
    weather2.columns = ['team','wind_conditions','indoor_outdoor','week','year']
    weather = pd.concat([weather1,weather2])

    new_dfs = {}
    for year, df in dfs.items():
        merge_df = df.merge(weather,on=['team','week','year'])
        new_dfs[year] = merge_df
    return new_dfs
nfl_fd_sc_weather_dfs = merge_weather(nfl_fd_sc_dfs)

# Train and Test Datasets
# Train and validate on 2013-2016
# Test on 2017
for year in range(2013,2018):
    print(nfl_fd_sc_weather_dfs[year].shape)


max_year = max(list(nfl_fd_sc_weather_dfs.keys()))
holdout = nfl_fd_sc_weather_dfs[2017]
model_dfs = [nfl_fd_sc_weather_dfs[yr] for yr in nfl_fd_sc_weather_dfs.keys() if yr != max_year]
model_df = pd.concat(model_dfs)

model_df.isnull().values.any()
holdout.isnull().values.any()

print(model_df.shape)
print(holdout.shape)

# Convert target to rank
model_df = model_df.sort_values(['year','position','week','target'], ascending=False).reset_index(drop=True)
model_df['target_rank'] = model_df.groupby(['year','position','week'])['target'].\
                                    rank(method="dense", ascending=False)


holdout.sort_values(['year','position','week','target'], ascending=False, inplace=True)
holdout['target_rank'] = holdout.groupby(['year','position','week'])['target'].\
                                    rank(method="dense", ascending=False)

model_df['target_rank'].hist(bins=40)


# Merge with ESPN Benchmarks
# TODO: This data/scraper was not included in the git repo
'''
proj = pd.read_json("./data/espn_projections.json")

clean_team_pos = proj['team'].str.replace('[^a-zA-Z\s]', '').str.upper().str.split(expand=True)
proj.drop(['team','position'],axis=1,inplace=True)
clean_team_pos.columns= ['team', 'position']

proj = pd.concat([proj, clean_team_pos], axis=1)

proj['team'] = proj['team'].str.replace('LAR','LA')
proj['team'] = proj['team'].str.replace('WSH','WAS')
proj['team'] = proj['team'].str.replace('LAC','SD')
proj['team'] = proj['team'].str.replace('JAX','JAC')

proj = proj[['name','position','team','week','proj_pts']]

proj.columns = ['full_name','position','team','target_week','proj_pts']
proj = proj[proj.proj_pts != '--']
proj['proj_pts'] = pd.to_numeric(proj['proj_pts'])
proj = proj[~proj.proj_pts.isnull()]
proj['full_name'] = proj.full_name.str.replace('Jr.','').str.strip()
proj['full_name'] = proj.full_name.str.replace('Sr.','').str.strip()
proj['full_name'] = proj.full_name.str.replace('III','').str.strip()
proj['full_name'] = proj.full_name.str.replace('II','').str.strip()
convert_names = {'Joshua Bellamy':'Josh Bellamy',
                 'TJ Jones':'T.J. Jones',
                 'Will Fuller V':'Will Fuller',
                 'Matthew Dayes':'Matt Dayes'}
proj['full_name'] = proj.full_name.replace(convert_names)

# merge ESPN projections to holdout set
merge_cols = ['full_name','position','team','target_week']
holdout = holdout.merge(proj, how='left', on=merge_cols)
holdout.dropna(inplace=True)

# create a rank for ESPN projections
holdout.sort_values(['year','position','week','proj_pts'], ascending=False, inplace=True)
holdout['espn_rank'] = holdout.groupby(['year','position','week'])['proj_pts'].\
                                    rank(method="dense", ascending=False)

print(holdout.shape)

'''

# Trim Outliers
# trim players who scored zero in a given week because they
# are skewing the distribution for my target variable.

thresh = 0

tmp = model_df[model_df.target > thresh]
print(model_df.shape)
print(tmp.shape)
tmp.target.hist(bins=40)

tmp = holdout[holdout.target > thresh]
print(holdout.shape)
print(tmp.shape)
tmp.target.hist(bins=40)

# TODO: NEED TO ADD IN ESPN PROJECTIONS FOR THIS CODE TO WORK
'''
tmp = holdout[holdout.proj_pts > thresh]
print(holdout.shape)
print(tmp.shape)
tmp.proj_pts.hist(bins=40)
'''

model_df_trimmed = model_df[model_df.target > thresh].reset_index(drop=True)

# TODO: NEED TO ADD IN ESPN PROJECTIONS FOR THIS CODE TO WORK
#holdout_trimmed = holdout[(holdout.target > thresh) &
#                          (holdout.proj_pts > thresh)].reset_index(drop=True)
holdout_trimmed = holdout[(holdout.target > thresh)].reset_index(drop=True)

# Player stat interactions
'''
The following merges serve the purpose to inform a given player of what type
of offense their team employs. For instance, merging the mean QB pass/rush
attempts ratio to that QB's WR gives an idea of how often the QB runs versus
throwing, thus affecting the possible targets thrown to that WR.
'''
numeric_df_columns = model_df_trimmed.select_dtypes(include=['float32','int32','int64','float64','uint8']).columns
fumble_features = [c for c in numeric_df_columns if "fumble" in c and "per" not in c]

passing_features = ['passing_att_mean','passing_cmp_mean','passing_ints_mean','passing_yds_mean',
                    'passing_tds_mean','passer_ratio','PassRushRatio_Att_mean','PassRushRatio_Yds_mean',
                    'PassRushRatio_Tds_mean']

rushing_features = ['rushing_yds_mean','rushing_att_mean','rushing_tds_mean',
                    'RushRecRatio_AttRec_mean','RushRecRatio_Tds_mean','RushRecRatio_Yds_mean']

receiving_features = ['receiving_rec_mean','receiving_tds_mean','receiving_yds_mean']

# TODO: Need to create scraper for offensive snap pct, tot, and starts
#sharedfeats = ['full_name','team','years_pro','age','weight','height','player_weight','year','week','target',
#               'target_rank','fantasy_points_mean','target_week','defensive_matchup_allowed','offensive_snap_pct',
#               'offensive_snap_tot','fd_salary','started','wind_conditions','indoor_outdoor']+fumble_features
sharedfeats = ['full_name','team','years_pro','age','weight','height','player_weight','year','week','target',
               'target_rank','fantasy_points_mean','target_week','defensive_matchup_allowed',
               'fd_salary','wind_conditions','indoor_outdoor']+fumble_features


QB_features = sharedfeats+passing_features+rushing_features
RB_features = sharedfeats+rushing_features+receiving_features
WR_features = sharedfeats+receiving_features
TE_features = sharedfeats+receiving_features


QB_df = model_df_trimmed[model_df_trimmed.position == 'QB'][QB_features].reset_index().drop('index',axis=1)
QB_stats = QB_df.groupby(['year','week','team']).mean()[passing_features].reset_index().add_prefix('QBMEAN')
QB_stats=QB_stats.rename(columns={'QBMEANyear':'year', 'QBMEANweek':'week', 'QBMEANteam':'team'})
QB_merge_stats = ['QBMEANPassRushRatio_Att','QBMEANPassRushRatio_Yds','QBMEANPassRushRatio_Tds']

RB_df = model_df_trimmed[model_df_trimmed.position == 'RB'][RB_features].reset_index().drop('index',axis=1)
RB_stats = RB_df.groupby(['year','week','team']).mean()[rushing_features].reset_index().add_prefix('RBMEAN')
RB_stats=RB_stats.rename(columns={'RBMEANyear':'year', 'RBMEANweek':'week', 'RBMEANteam':'team'})

WR_df = model_df_trimmed[model_df_trimmed.position == 'WR'][WR_features].reset_index().drop('index',axis=1)
WR_stats = WR_df.groupby(['year','week','team']).mean()[receiving_features].reset_index().add_prefix('WRMEAN')
WR_stats=WR_stats.rename(columns={'WRMEANyear':'year', 'WRMEANweek':'week', 'WRMEANteam':'team'})

TE_df = model_df_trimmed[model_df_trimmed.position == 'TE'][TE_features].reset_index().drop('index',axis=1)
TE_stats = TE_df.groupby(['year','week','team']).mean()[receiving_features].reset_index().add_prefix('TEMEAN')
TE_stats=TE_stats.rename(columns={'TEMEANyear':'year', 'TEMEANweek':'week', 'TEMEANteam':'team'})

print("QB:", QB_df.shape)
print("RB:", RB_df.shape)
print("WR:", WR_df.shape)
print("TE:", TE_df.shape)

QB_df = QB_df.merge(RB_stats, how='inner', on=['year','week','team'])

RB_df = RB_df.merge(QB_stats, how='inner', on=['year','week','team'])

WR_df = WR_df.merge(QB_stats, how='inner', on=['year','week','team'])
WR_df = WR_df.merge(RB_stats, how='inner', on=['year','week','team'])

TE_df = TE_df.merge(QB_stats, how='inner', on=['year','week','team'])
TE_df = TE_df.merge(RB_stats, how='inner', on=['year','week','team'])

print("QB:", QB_df.shape)
print("RB:", RB_df.shape)
print("WR:", WR_df.shape)
print("TE:", TE_df.shape)

# holdout
# TODO: Datascrape ESPN scores during test year
#QB_features = QB_features+['espn_rank','proj_pts']
#RB_features = RB_features+['espn_rank','proj_pts']
#WR_features = WR_features+['espn_rank','proj_pts']
#TE_features = TE_features+['espn_rank','proj_pts']

QB_df_holdout = holdout_trimmed[holdout_trimmed.position == 'QB'][QB_features].reset_index().drop('index',axis=1)
QB_stats = QB_df_holdout.groupby(['year','week','team']).mean()[passing_features].reset_index().add_prefix('QBMEAN')
QB_stats=QB_stats.rename(columns={'QBMEANyear':'year', 'QBMEANweek':'week', 'QBMEANteam':'team'})
QB_merge_stats = ['QBMEANPassRushRatio_Att','QBMEANPassRushRatio_Yds','QBMEANPassRushRatio_Tds']

RB_df_holdout = holdout_trimmed[holdout_trimmed.position == 'RB'][RB_features].reset_index().drop('index',axis=1)
RB_stats = RB_df_holdout.groupby(['year','week','team']).mean()[rushing_features].reset_index().add_prefix('RBMEAN')
RB_stats=RB_stats.rename(columns={'RBMEANyear':'year', 'RBMEANweek':'week', 'RBMEANteam':'team'})

WR_df_holdout = holdout_trimmed[holdout_trimmed.position == 'WR'][WR_features].reset_index().drop('index',axis=1)
WR_stats = WR_df_holdout.groupby(['year','week','team']).mean()[receiving_features].reset_index().add_prefix('WRMEAN')
WR_stats=WR_stats.rename(columns={'WRMEANyear':'year', 'WRMEANweek':'week', 'WRMEANteam':'team'})

TE_df_holdout = holdout_trimmed[holdout_trimmed.position == 'TE'][TE_features].reset_index().drop('index',axis=1)
TE_stats = TE_df_holdout.groupby(['year','week','team']).mean()[receiving_features].reset_index().add_prefix('TEMEAN')
TE_stats=TE_stats.rename(columns={'TEMEANyear':'year', 'TEMEANweek':'week', 'TEMEANteam':'team'})

print("QB:", QB_df_holdout.shape)
print("RB:", RB_df_holdout.shape)
print("WR:", WR_df_holdout.shape)
print("TE:", TE_df_holdout.shape)

QB_df_holdout = QB_df_holdout.merge(RB_stats, how='inner', on=['year','week','team'])

RB_df_holdout = RB_df_holdout.merge(QB_stats, how='inner', on=['year','week','team'])

WR_df_holdout = WR_df_holdout.merge(RB_stats, how='inner', on=['year','week','team'])
WR_df_holdout = WR_df_holdout.merge(QB_stats, how='inner', on=['year','week','team'])

TE_df_holdout = TE_df_holdout.merge(QB_stats, how='inner', on=['year','week','team'])
TE_df_holdout = TE_df_holdout.merge(RB_stats, how='inner', on=['year','week','team'])

print("QB:", QB_df_holdout.shape)
print("RB:", RB_df_holdout.shape)
print("WR:", WR_df_holdout.shape)
print("TE:", TE_df_holdout.shape)


# Interactions by position
from sklearn.preprocessing import PolynomialFeatures
create_interactions = [('QB',QB_df), ('RB',RB_df), ('WR',WR_df), ('TE',TE_df)]
interactions_positions = {}
for pos, data in create_interactions:
    numerics = data.select_dtypes(include=['float32','int32','int64','float64','uint8']).columns.tolist()
    data = data[numerics]
    poly = PolynomialFeatures(2, interaction_only=True, include_bias=True)
    interactions_arr = poly.fit_transform(data)
    interactions_names = poly.get_feature_names(data.columns)
    interactions = pd.DataFrame(interactions_arr, columns=interactions_names)
    interactions_positions[pos] = interactions

def explore_interaction_corrs(pos, interactions):
    target_col = interactions['target']
    nontarget_interactions = interactions[[c for c in interactions.columns if "target" not in c]]
    explore = pd.concat([target_col, nontarget_interactions], axis=1)
    corr_interactions = explore.corr()
    return corr_interactions[['target']].sort_values('target',ascending=False).reset_index()

QB_inters = explore_interaction_corrs('QB', interactions_positions['QB'])
RB_inters = explore_interaction_corrs('RB', interactions_positions['RB'])
WR_inters = explore_interaction_corrs('WR', interactions_positions['WR'])
TE_inters = explore_interaction_corrs('TE', interactions_positions['TE'])

# QB_inters.to_csv('data/interactions_QB.csv')
# RB_inters.to_csv('data/interactions_RB.csv')
# WR_inters.to_csv('data/interactions_WR.csv')
# TE_inters.to_csv('data/interactions_TE.csv')

# QB_inters = pd.read_csv('data/interactions_QB.csv')
# RB_inters = pd.read_csv('data/interactions_RB.csv')
# WR_inters = pd.read_csv('data/interactions_WR.csv')
# TE_inters = pd.read_csv('data/interactions_TE.csv')


QB_inters.sort_values('target',ascending=True).head()
RB_inters.sort_values('target',ascending=True).head()
TE_inters.sort_values('target',ascending=False).head(8)

# Compute Interactions
QB_df.reset_index(inplace=True,drop=True)
RB_df.reset_index(inplace=True,drop=True)
WR_df.reset_index(inplace=True,drop=True)
TE_df.reset_index(inplace=True,drop=True)


QB_df['chg_fumbles_yds trend_fumbles_tot'] = QB_df['trend_fumbles_tot']*QB_df['chg_fumbles_yds']
QB_df['age player_weight'] = QB_df['age']*QB_df['player_weight']
# TODO: nead snaps data scraper for these features
#RB_df['player_weight offensive_snap_pct'] = RB_df['player_weight']*RB_df['offensive_snap_pct']
#RB_df['fantasy_points_mean offensive_snap_tot'] = RB_df['offensive_snap_tot']*RB_df['fantasy_points_mean']
#RB_df['offensive_snap_tot chg_fumbles_tot'] = RB_df['offensive_snap_tot']*RB_df['chg_fumbles_tot']
WR_df['chg_fumbles_tot receiving_yds_mean'] = WR_df['chg_fumbles_tot']*WR_df['receiving_yds_mean']
WR_df['age receiving_yds_mean'] = WR_df['age']*WR_df['receiving_yds_mean']
TE_df['trend_fumbles_tot RBMEANRushRecRatio_AttRec_mean'] = TE_df['trend_fumbles_tot']*TE_df['RBMEANRushRecRatio_AttRec_mean']
TE_df['age receiving_yds_mean'] = TE_df['age']*TE_df['receiving_yds_mean']

QB_df_holdout.reset_index(inplace=True,drop=True)
RB_df_holdout.reset_index(inplace=True,drop=True)
WR_df_holdout.reset_index(inplace=True,drop=True)
TE_df_holdout.reset_index(inplace=True,drop=True)

QB_df_holdout['chg_fumbles_yds trend_fumbles_tot'] = QB_df_holdout['trend_fumbles_tot']*QB_df_holdout['chg_fumbles_yds']
QB_df_holdout['age player_weight'] = QB_df_holdout['age']*QB_df_holdout['player_weight']
# TODO: nead snaps data scraper for these features
#RB_df_holdout['player_weight offensive_snap_pct'] = RB_df_holdout['player_weight']*RB_df_holdout['offensive_snap_pct']
#RB_df_holdout['fantasy_points_mean offensive_snap_tot'] = RB_df_holdout['offensive_snap_tot']*RB_df_holdout['fantasy_points_mean']
#RB_df_holdout['offensive_snap_tot chg_fumbles_tot'] = RB_df_holdout['offensive_snap_tot']*RB_df_holdout['chg_fumbles_tot']
WR_df_holdout['chg_fumbles_tot receiving_yds_mean'] = WR_df_holdout['chg_fumbles_tot']*WR_df_holdout['receiving_yds_mean']
WR_df_holdout['age receiving_yds_mean'] = WR_df_holdout['age']*WR_df_holdout['receiving_yds_mean']
TE_df_holdout['trend_fumbles_tot RBMEANRushRecRatio_AttRec_mean'] = TE_df_holdout['trend_fumbles_tot']*TE_df_holdout['RBMEANRushRecRatio_AttRec_mean']
TE_df_holdout['age receiving_yds_mean'] = TE_df_holdout['age']*TE_df_holdout['receiving_yds_mean']

# Memory Management
del player_dfs
del opp_dfs
del nfl_dfs
del fanduel_dfs
del nfl_fanduel_dfs
del nfl_fd_sc_dfs
del nfl_fd_sc_weather_dfs
del QB_inters
del RB_inters
del WR_inters
del TE_inters
del interactions_positions
gc.collect()

# Regression Model
import sklearn.metrics as metrics
import sklearn.linear_model as lin
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from pprint import pprint
import matplotlib
from math import exp
from sklearn.utils import shuffle

RESPONSE_VAR = 'target'
# TODO: Need to pull project points data and incorporate
#BENCHMARK = 'proj_pts'
BENCHMARK = "target"
CURR_WEEK = 14

def regression_tts(input_df, week, response):

    """Run a regression for each position (QB,RB,WR,TE),
       Train on first 14 weeks of each season 2013-2016,
       Test on last 3 weeks of each season 2013-2016"""

    features = input_df.select_dtypes(include=['float32','int32','int64','float64','uint8']).columns.tolist()
    features.remove('year')
    features.remove('target')
    features.remove('target_rank')
    features.remove('target_week')

    est = GradientBoostingRegressor(n_estimators=30, learning_rate=0.1)
#     est = lin.LassoCV()

    df_train = input_df[input_df.target_week <= week]
#     df_train.sort_values('fantasy_points_mean',ascending=True,inplace=True)
    df_test = input_df[input_df.target_week > week]

    X_train = df_train[features]
    y_train = df_train[response]
    X_test = df_test[features]
    y_test = df_test[response]

    ss = StandardScaler()
    X_train = ss.fit_transform(X_train)
    X_test = ss.fit_transform(X_test)

#     sw = np.linspace(.01,1,X_train.shape[0])
    est.fit(X_train, y_train)

    y_pred = est.predict(X_train)
    train_results = (metrics.mean_squared_error(y_train, y_pred))**(0.5)
#     train_results = metrics.r2_score(y_train, y_pred)

    y_pred = est.predict(X_test)
    test_results = (metrics.mean_squared_error(y_test, y_pred))**(0.5)
#     test_results = metrics.r2_score(y_test, y_pred)

    df_test = df_test.reset_index()[['target_week','fantasy_points_mean',response]]
    df_test['MODEL_PRED'] = pd.Series(y_pred)
    df_test['RESIDUALS'] = df_test['MODEL_PRED'] - df_test[response]

    coefs = None
    if 'sklearn.linear_model' in est.__module__:
        coef_ranks = list(zip(abs(est.coef_), est.coef_, features))
        coefs = sorted(coef_ranks, key=lambda x: x[0], reverse=True)
    else:
        coef_ranks = list(zip(est.feature_importances_, features))
        coefs = sorted(coef_ranks, key=lambda x: x[0], reverse=True)

    return test_results, train_results, est, coefs, df_test

coefs_all = {}
ests_positions = {}
resids_positions = []

for pos, data in [('QB',QB_df),('RB',RB_df),('WR',WR_df),('TE',TE_df)]:
    print(pos)
    results_test, results_train, est, coefs, resids = regression_tts(data, CURR_WEEK, RESPONSE_VAR)

    print('train results:',results_train)
    print('test  results:',results_test)
    coefs_all[pos] = coefs
    ests_positions[pos] = est
    resids['position'] = pos
    resids_positions.append(resids)

for pos in coefs_all.keys():
    print(pos)
    pprint(coefs_all[pos][:4])

QB_coefs_plot = [x[0] for x in coefs_all['QB']][:3]
RB_coefs_plot = [x[0] for x in coefs_all['RB']][:3]
WR_coefs_plot = [x[0] for x in coefs_all['WR']][:3]
TE_coefs_plot = [x[0] for x in coefs_all['TE']][:3]

font = {'size'   : 18}
matplotlib.rc('font', **font)
fig, (ax1,ax2,ax3,ax4) = plt.subplots(1,4,figsize=(23,5), sharey=True)

for ax, title, pos_coefs in [(ax1,'QB',QB_coefs_plot), (ax2,'RB',RB_coefs_plot),
                      (ax3,'WR',WR_coefs_plot), (ax4,'TE',TE_coefs_plot)]:
    ax.bar(range(len(WR_coefs_plot)),WR_coefs_plot)
    ax.set_title(title)
    ax.axes.xaxis.set_ticklabels([])

# Model Output
#from sklearn.ensemble.partial_dependence import plot_partial_dependence
from sklearn.inspection import plot_partial_dependence
font = {'size'   : 16}
matplotlib.rc('font', **font)

features = RB_df.select_dtypes(include=['float32','int32','int64','float64','uint8']).columns.tolist()
features.remove('year')
features.remove('target')
features.remove('target_rank')
features.remove('target_week')

fp_mean = features.index('fantasy_points_mean')
fd_sal = features.index('fd_salary')
pr = features.index('receiving_rec_mean')
pw = features.index('player_weight')
dpa = features.index('defensive_matchup_allowed')
# TODO: include once available
#snaps = features.index('offensive_snap_tot')
X_train = RB_df[features]
#X_train = X_train[X_train.week < CURR_WEEK].as_matrix()
X_train = X_train[X_train.week < CURR_WEEK].values

# TODO: add back in offensive snaps when available
#features_idx = [fp_mean, fd_sal, dpa, pr, snaps, pw]
features_idx = [fp_mean, fd_sal, dpa, pr, pw]
fig = plot_partial_dependence(ests_positions['RB'], X_train, features_idx,\
                                   feature_names=features,\
                                   n_jobs=-1, grid_resolution=50) #, figsize=(20,10))
#fig.subtitle('Partial dependence for RBs')
plt.suptitle("partial dependence for RBs")
plt.subplots_adjust(top=0.9)

model_results = pd.concat(resids_positions)
model_results = model_results.sort_values('MODEL_PRED').reset_index()
model_results_QB = resids_positions[0].sort_values('MODEL_PRED').reset_index()
model_results_RB = resids_positions[1].sort_values('MODEL_PRED').reset_index()
model_results_WR = resids_positions[2].sort_values('MODEL_PRED').reset_index()
model_results_TE = resids_positions[3].sort_values('MODEL_PRED').reset_index()


plt.figure(figsize=(10,5))
plt.scatter(model_results.MODEL_PRED, model_results.RESIDUALS, s=3)
plt.ylabel('Residual')
plt.xlabel('Predicted Fantasy Points')

plt.figure(figsize=(10,5))
plt.scatter(model_results_QB.MODEL_PRED, model_results_QB.RESIDUALS, s=3)

plt.figure(figsize=(10,5))
plt.scatter(model_results_RB.MODEL_PRED, model_results_RB.RESIDUALS, s=3)

plt.figure(figsize=(10,5))
plt.scatter(model_results_WR.MODEL_PRED, model_results_WR.RESIDUALS, s=3)

plt.figure(figsize=(10,5))
plt.scatter(model_results_TE.MODEL_PRED, model_results_TE.RESIDUALS, s=3)


font = {'size'   : 20}
matplotlib.rc('font', **font)
plt.figure(figsize=(10,6))
model_results.RESIDUALS.hist(bins=50)
plt.xlabel("Residual Value")
plt.ylabel("Number of Observations")
print(model_results.RESIDUALS.mean())
print(model_results.RESIDUALS.median())

# weeks = sorted(model_df.target_week.unique().tolist())
# weeks.remove(1.0)
# weeks.remove(2.0)
weeks_predict = list(range(2,CURR_WEEK))

def weekly_regression_predict(input_df, weeks, est, response, espn_response):

    features = input_df.select_dtypes(include=['float32','int32','int64','float64','uint8']).columns.tolist()
    features.remove('year')
    features.remove('target')
    features.remove('target_rank')
    # TEST: removing target_week incase this is the reason for error
    if 'target_week' in features:
        features.remove('target_week')
    # TODO: Uncomment these lines once projections and espn ranks available
    #features.remove('proj_pts')
    #features.remove('espn_rank')

    week_nums = []
    scores = []
    bmk_scores = []
    predictions = []

    for week in weeks:
        week_nums.append(week)

        df_cv = input_df[input_df.target_week == week]
        X = df_cv[features]
        y = df_cv[response]
        y_benchmark = df_cv[espn_response]
#         X.sort_values('fantasy_points_mean',ascending=True,inplace=True)
        ss = StandardScaler()
        X = ss.fit_transform(X)

        y_pred = est.predict(X)

#         score = metrics.r2_score(y, y_pred)
#         score = (metrics.mean_squared_error(y, y_pred))**(0.5)
        score = metrics.mean_absolute_error(y, y_pred)
        scores.append(score)

#         bmk_score = metrics.r2_score(y, y_benchmark)
#         bmk_score = (metrics.mean_squared_error(y, y_benchmark))**(0.5)
        bmk_score = metrics.mean_absolute_error(y, y_benchmark)
        bmk_scores.append(bmk_score)

        predicts = df_cv.reset_index()[['full_name','target_week', response, espn_response]]
        predicts['PREDICTION'] = pd.Series(y_pred)
        if len(predicts[response].shape) == 2:
            predicts["ERROR"] = predicts["PREDICTION"] - predicts[response].iloc[:,0]
            predicts["ESPN_ERROR"] = predicts[espn_response].iloc[:,0] - predicts[response].iloc[:,0]
        else:
            predicts['ERROR'] = predicts['PREDICTION'] - predicts[response]
            predicts['ESPN_ERROR'] = predicts[espn_response] - predicts[response]
        predictions.append(predicts)

    return week_nums, scores, bmk_scores, pd.concat(predictions)


prediction_dfs = {}

f, (ax2, ax3, ax4, ax5) = plt.subplots(4,figsize=(12,30), sharex=True)
for pos, data, ax in [('QB',QB_df_holdout,ax2),
                      ('RB',RB_df_holdout,ax3),
                      ('WR',WR_df_holdout,ax4),
                      ('TE',TE_df_holdout,ax5)]:

    weeks, scores, bmk_scores, predictions = weekly_regression_predict(data, weeks_predict,
                                                                       ests_positions[pos],
                                                                       response=RESPONSE_VAR,
                                                                       espn_response=BENCHMARK)
    predictions['position'] = pos
    prediction_dfs[pos] = predictions

    ax.plot(weeks, scores, label="Linear Model RMSE", linewidth=4)
    ax.plot(weeks, bmk_scores, label="ESPN RMSE", linewidth=4)
    ax.set_xticks(weeks)
    ax.set_ylabel("RMSE")
    ax.set_title(pos)
    ax.legend()

holdout_results = pd.concat(list(prediction_dfs.values()))


weeks_all = []
all_scores = []
all_bmk_scores = []
for week in weeks_predict:
    weeks_all.append(week)
    weeks_results = holdout_results[holdout_results.target_week == week]
    if len(weeks_results[RESPONSE_VAR].shape) == 2:
        y = weeks_results[RESPONSE_VAR].iloc[:,0]
    else:
        y = weeks_results[RESPONSE_VAR]
    y_pred = weeks_results['PREDICTION']
    if len(weeks_results[BENCHMARK].shape) == 2:
        y_bmk = weeks_results[BENCHMARK].iloc[:,0]
    else:
        y_bmk = weeks_results[BENCHMARK]
#     score = metrics.r2_score(y, y_pred)
#     bmk_score = metrics.r2_score(y, y_bmk)
    score = (metrics.mean_squared_error(y, y_pred))**(0.5)
    bmk_score = (metrics.mean_squared_error(y, y_bmk))**(0.5)
    all_scores.append(score)
    all_bmk_scores.append(bmk_score)

print(np.mean(all_scores))
print(np.mean(all_bmk_scores))
plt.figure(figsize=(20,12))
plt.plot(weeks_all, all_scores, label="Linear Model", linewidth=4)
plt.plot(weeks_all, all_bmk_scores, label="ESPN", linewidth=4)
plt.xticks(weeks_all)
# plt.ylabel("RMSE")
# plt.xlabel("Week")
# plt.title("Holdout error for all positions (2017 season)")
plt.legend()

position_q = 'RB'
name = 'LeSean McCoy'
holdout_results[(holdout_results.position == position_q) &
                (holdout_results.full_name == name)]


holdout_results['abs_error'] = holdout_results.ERROR.apply(lambda x: np.abs(x))
holdout_results['spread'] = np.abs(holdout_results['ERROR'] - holdout_results['ESPN_ERROR'])

holdout_results.sort_values('spread', ascending=False).head(20)
