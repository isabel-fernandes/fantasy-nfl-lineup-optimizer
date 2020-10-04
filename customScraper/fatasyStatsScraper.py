import requests
import json
from bs4 import BeautifulSoup

startingWeek = 4
year = 2020

cookies = {
    '_ga': 'GA1.2.1311463715.1601832784',
    '_gid': 'GA1.2.892033734.1601832784',
    '_gat': '1',
    '_fbp': 'fb.1.1601832784473.1877195828',
    '_cio': '35d40c25-16af-7c1f-c67f-5d3ac5e5adfe',
    'FantasyData_CookiesAccepted': '1',
}

headers = {
    'authority': 'fantasydata.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'dnt': '1',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://fantasydata.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://fantasydata.com/nfl/fantasy-football-leaders?season=2019&seasontype=1&scope=2&subscope=1&scoringsystem=2&startweek=1&endweek=17&aggregatescope=1&range=1',
    'accept-language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,ja;q=0.6,es-419;q=0.5',
}

data = {
    'sort': 'FantasyPointsPPR-desc',
    'pageSize': '50',
    'group': '',
    'filter': '',
    'filters.position': '',
    'filters.team': '',
    'filters.teamkey': '',
    'filters.season': str(year),
    'filters.seasontype': '1',
    'filters.cheatsheettype': '',
    'filters.scope': '2',
    'filters.subscope': '1',
    'filters.redzonescope': '',
    'filters.scoringsystem': '2',
    'filters.leaguetype': '',
    'filters.searchtext': '',
    'filters.week': '',
    'filters.startweek': str(startingWeek),
    'filters.endweek': str(startingWeek + 1),
    'filters.minimumsnaps': '',
    'filters.teamaspect': '',
    'filters.stattype': '',
    'filters.exportType': '',
    'filters.desktop': '',
    'filters.dfsoperator': '',
    'filters.dfsslateid': '',
    'filters.dfsslategameid': '',
    'filters.dfsrosterslot': '',
    'filters.page': '',
    'filters.showfavs': '',
    'filters.posgroup': '',
    'filters.oddsstate': '',
    'filters.showall': '',
    'filters.aggregatescope': '1',
    'filters.rangescope': '',
    'filters.range': '1',
    'filters.type': ''
}

response = requests.post('https://fantasydata.com/NFL_FantasyStats/FantasyStats_Read',
                         headers=headers, cookies=cookies, data=data)

dataJson = response.json()['Data']

variableDef = ['Name', 'Team', 'Position', 'Week', 'Opponent', 'Season', 'GameStatus', 'TeamIsHome', 'HomeScore',
               'AwayScore',
               'PassingYards', 'PassingTouchdowns', 'Interceptions', 'PassingAttempts', 'PassingCompletions',
               'RushingAttempts',
               'RushingYards', 'Receptions', 'ReceivingTargets', 'ReceivingYards', 'ReceivingTouchdowns', 'Fumbles']
sampleDict = {'PlayerID': 18858, 'Season': 2020, 'Played': 1, 'Started': 0, 'Week': 4, 'Opponent': 'JAX',
              'TeamHasPossession': True, 'HomeOrAway': None, 'TeamIsHome': True, 'Result': '', 'HomeScore': 27,
              'AwayScore': 16, 'Quarter': '4', 'QuarterDisplay': 'Q4', 'IsGameOver': False,
              'GameDate': '/Date(1601830800000)/', 'TimeRemaining': '11:15', 'ScoreSummary': '4 27 - 16 vs. JAX',
              'PassingCompletions': 0, 'PassingAttempts': 0, 'PassingCompletionPercentage': 0, 'PassingYards': 0,
              'PassingYardsPerAttempt': 0, 'PassingTouchdowns': 0.0, 'PassingInterceptions': 0.0, 'PassingRating': 0,
              'RushingAttempts': 18.0, 'RushingYards': 104.0, 'RushingYardsPerAttempt': 5.8, 'RushingTouchdowns': 2.0,
              'Receptions': 6.0, 'ReceivingTargets': 6.0, 'ReceivingYards': 30.0, 'ReceptionPercentage': 100
    , 'ReceivingTouchdowns': 1.0, 'ReceivingLong': 14.0, 'ReceivingYardsPerTarget': 5, 'ReceivingYardsPerReception': 5,
              'Fumbles': 0.0, 'FumblesLost': 0.0, 'FieldGoalsMade': 0.0, 'FieldGoalsAttempted': 0.0,
              'FieldGoalPercentage': 0, 'FieldGoalsLongestMade': 0.0, 'ExtraPointsMade': 0.0,
              'ExtraPointsAttempted': 0.0, 'TacklesForLoss': 0.0, 'Sacks': 0.0, 'QuarterbackHits': 0.0,
              'Interceptions': 0.0, 'FumblesRecovered': 0.0, 'Safeties': 0.0, 'DefensiveTouchdowns': 0,
              'SpecialTeamsTouchdowns': 0, 'SoloTackles': 0.0, 'AssistedTackles': 0.0, 'SackYards': 0.0,
              'PassesDefended': 0.0, 'FumblesForced': 0.0, 'FantasyPoints': 31.4, 'FantasyPointsPPR': 37.4,
              'FantasyPointsFanDuel': 34.4, 'FantasyPointsYahoo': 34.4, 'FantasyPointsFantasyDraft': 40.4,
              'FantasyPointsDraftKings': 40.4
    , 'FantasyPointsHalfPointPpr': 34.4, 'FantasyPointsSixPointPassTd': 31.4, 'FantasyPointsPerGame': 31.4,
              'FantasyPointsPerGamePPR': 37.4, 'FantasyPointsPerGameFanDuel': 34.4, 'FantasyPointsPerGameYahoo': 34.4,
              'FantasyPointsPerGameDraftKings': 40.4, 'FantasyPointsPerGameHalfPointPPR': 34.4,
              'FantasyPointsPerGameSixPointPassTd': 31.4, 'FantasyPointsPerGameFantasyDraft': 40.4,
              'PlayerUrlString': '/nfl/joe-mixon-fantasy/18858', 'GameStatus': 'P',
              'GameStatusClass': 'gamestatus_green', 'PointsAllowedByDefenseSpecialTeams': None, 'TotalTackles': 0.0,
              'StatSummary': [{'Items': [{
                  'StatValue': '18', 'StatTitle': 'ATT'}, {'StatValue': '104', 'StatTitle': 'YDS'},
                  {'StatValue': '5.8', 'StatTitle': 'AVG'}, {'StatValue': '2', 'StatTitle': 'TD'}]},
                  {'Items': [{'StatValue': '6'
                                 , 'StatTitle': 'TGT'}, {'StatValue': '6', 'StatTitle': 'REC'},
                             {'StatValue': '30', 'StatTitle': 'YDS'}, {'StatValue': 'TD', 'StatTitle': None}]}],
              'Name': 'Joe Mixon', 'ShortName': 'J. Mixon',
              'FirstName': 'Joe', 'LastName': 'Mixon', 'FantasyPosition': 'RB', 'Position': 'RB',
              'TeamUrlString': '/nfl/cincinnati-bengals-depth-chart', 'Team': 'CIN', 'IsScrambled': False, 'Rank': 1,
              'StaticRank': 0, 'PositionRank': None, 'IsFavorite': False}
filteredStats = {definitions: sampleDict[definitions] for definitions in variableDef}

if(filteredStats['TeamIsHome'] == False):
    temp = filteredStats['HomeScore']
    filteredStats['HomeScore'] = filteredStats['AwayScore']
    filteredStats['AwayScore'] = temp
del filteredStats['TeamIsHome']

variableDefKeys = ['Name', 'Team', 'Pos', 'Wk', 'Opp', 'Year', 'Status', 'TeamScore', 'OppScore', 'PassYds',
                      'PassingTD',
                      'Int', 'PassingAtt', 'Cmp', 'RushingAtt', 'RushingYds', 'RushingTD', 'Rec', 'Tgs', 'ReceivingYds',
                      'ReceivingTD', 'FL']
variableDefValues = list(filteredStats.values())

weeklyStatsDict = dict(zip(variableDefKeys,variableDefValues))
weeklyStatsDict = [int(x) for x in list(weeklyStatsDict.values()) if x == type(float)]
#print(filteredStats)
print(weeklyStatsDict)
#for definition in variableDefNewName:

# print(parsedDataJson)
