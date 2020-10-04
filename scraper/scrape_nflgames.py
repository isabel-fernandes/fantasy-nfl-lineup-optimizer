import pandas as pd
import nflgame
from pprint import pprint
from collections import defaultdict
import pickle

CURR_WEEK = 14
YEARS = [2013,2014,2015]
#YEARS = [2015]
dir_out = "../data/"


games = nflgame.games(2013, 1)
game_player_stats = nflgame.combine_game_stats(games[:1])
playerstats = defaultdict(str)

game1 = games[0]

for p in game_player_stats:
    print(p.name, p.guess_position)

for p in game_player_stats:
    info = {}
    info.update(p.stats)
    try:
        #info.update(p.player.__dict__)
        info.update(p.player._asdict())
    except AttributeError:
        pass
    playerstats[p.playerid] = info
tmp = pd.DataFrame(playerstats).T.reset_index().rename(columns={"index":"id"})

def get_year(year, weeks):
    """ Get all games and players involved for a given season"""
    week_data = []
    for week in weeks:
        games = nflgame.games(year, week)
        game_player_stats = nflgame.combine_game_stats(games)
        df = get_week(game_player_stats, week)
        df['week'] = week
        week_data.append(df)
    return pd.concat(week_data)

def get_week(players, week):
    """ Get stats for each player in each game"""
    playerstats = defaultdict(str)
    for p in players:
        info = {}
        info.update(p.stats)
        try:
            #info.update(p.player.__dict__)
            info.update(p.player._asdict())
        except AttributeError:
            pass
        
        try: 
            info['team'] = p.team
            info['full_name'] = p.player.full_name
            info['birthdate'] = p.player.birthdate
            info['years_pro'] = p.player.years_pro
            info['height'] = p.player.height
            info['weight'] = p.player.weight
            info['position'] = p.player.position
            info['profile_url'] = p.player.profile_url
            info['last_name'] = p.player.last_name
            info['number'] = p.player.number
        except AttributeError:  
            print("    {} player data not available. Skipping...".format(p.name)) 
            continue 

        playerstats[p.playerid] = info
    return pd.DataFrame(playerstats).T.reset_index().rename(columns={"index":"id"})

def get_opponent_stats(team_list, year):
    """ For a given team, report opponents' stats in each game to get measures of
        the team's defensive stats"""
    dfs = []
    for team_to_check in team_list:
        print(team_to_check)
        # Get the games the target team played in the season
        try:
            games = nflgame.games(year, home=team_to_check, away=team_to_check)
        except TypeError as err:
            if err == "'NoneType' object is not iterable":
                print("caught error name!!!")
            else:
                print("didn't catch error name...")
            continue
        rows = []
        for g in games:
            row = {}
            if g.home == team_to_check:
                row['week'] = g.schedule['week']
                row['TEAM'] = team_to_check
                row['OPP'] = g.away
                row['opp_points'] = g.score_away
                #row.update(g.stats_away.__dict__)
                row.update(g.stats_away._asdict())
                row['pos_time'] = row['pos_time'].total_seconds()
            else:
                row['week'] = g.schedule['week']
                row['TEAM'] = team_to_check
                row['OPP'] = g.home
                row['opp_points'] = g.score_home
                #row.update(g.stats_home.__dict__)
                row.update(g.stats_home._asdict())
                row['pos_time'] = row['pos_time'].total_seconds()

            rows.append(row)
        dfs.append(pd.DataFrame(rows))
    return pd.concat(dfs)

TEAMS = [team[0] for team in nflgame.teams] +['STL']
TEAMS.remove('LA')
TEAMS.remove("JAX")
TEAMS.append("JAC") 
TEAMS.remove("LAC")
TEAMS.append("SD") 

weeks = list(range(1,18))

ps = []
for year in YEARS:
    print("Creating Players Stats "+str(year))
    player_stats = get_year(year, weeks).fillna(0)
    ps.append(player_stats)
    print("Creating Opponents Stats "+str(year))
    opp_stats = get_opponent_stats(TEAMS, year)
    opp_stats = opp_stats.add_prefix("opp_")
    print("Saving to File "+str(year))
    opp_stats.to_csv(dir_out+"opp_stats_"+str(year)+".csv", index=False)
    player_stats.to_csv(dir_out+"player_stats_"+str(year)+".csv", index=False)

    TEAMS_2016 = [team[0] for team in nflgame.teams]
#TEAMS_2016.remove('JAC')
#TEAMS_2016.append('JAX')
TEAMS_2016.remove('STL')
if "LAC" in TEAMS_2016: 
    TEAMS_2016.remove("LAC")
    TEAMS_2016.append("SD") 


year = 2016
print("Creating Players Stats "+str(year))
player_stats = get_year(year, weeks).fillna(0)
print("Creating Opponents Stats "+str(year))
opp_stats = get_opponent_stats(TEAMS_2016, year)
opp_stats = opp_stats.add_prefix("opp_")
opp_stats.to_csv(dir_out+"opp_stats_"+str(year)+".csv", index=False)
player_stats.to_csv(dir_out+"player_stats_"+str(year)+".csv", index=False)

TEAMS_2017 = [team[0] for team in nflgame.teams]
#TEAMS_2017.remove('JAC')
#TEAMS_2017.append('JAX')
TEAMS_2017.remove('STL')
TEAMS_2017.append('LAC')
TEAMS_2017.remove('SD')

weeks = list(range(1,CURR_WEEK))
year = 2017
print("Creating Players Stats "+str(year))
player_stats = get_year(year, weeks).fillna(0)
print("Creating Opponents Stats "+str(year))
opp_stats = get_opponent_stats(TEAMS_2017, year)
opp_stats = opp_stats.add_prefix("opp_")
opp_stats.to_csv(dir_out+"opp_stats_"+str(year)+".csv", index=False)
player_stats.to_csv(dir_out+"player_stats_"+str(year)+".csv", index=False)
