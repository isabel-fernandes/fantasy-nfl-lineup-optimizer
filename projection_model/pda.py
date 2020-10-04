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
dir_fanduel = "../data/fanduel_salaries/" 
files = os.listdir(dir_in)


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

player_stats_files = [WeeklyStats(os.path.join(dir_in,f)) for f in files if "player_stats_" in f]
opp_stats_files = [WeeklyStats(os.path.join(dir_in,f)) for f in files if "opp_stats_" in f]

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
    
    '''
    # compute 3-week and 2-week points deltas
    deltas = df.groupby(['id']).pct_change()
    deltas = deltas.add_prefix('chg_')
    deltas = pd.concat([df, deltas], axis=1)
    deltas2 = deltas.groupby(['id'])[deltas.columns].shift(1).fillna(0)
    deltas3 = deltas.groupby(['id'])[deltas.columns].shift(2).fillna(0)
    deltas2 = deltas2.add_prefix('per2_')
    deltas3 = deltas3.add_prefix('per3_')
    trend_df = pd.concat([deltas, deltas2, deltas3], axis=1)
    # average prior three deltas to get trend
    for col in stat_cols:
        name = 'trend_'+col
        trend_df[name] = trend_df[['chg_'+col,'per2_chg_'+col,'per3_chg_'+col]].mean(axis=1).fillna(0)
    return trend_df
    '''
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


