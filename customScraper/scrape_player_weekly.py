import requests
import csv

# variables that control the date
startingWeek =2
year = 2020

# List of dictionaries that will be turned into a csv
mainPlayerDataList = []

# requests made to get data
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
    'pageSize': '900',
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

# List of Player data unfiltered
dataJson = response.json()['Data']

def filterDictionary(playerDictionary):
    # Keys we will filter for
    variableDef = ['Name', 'Team', 'Position', 'Week', 'Opponent', 'Season', 'GameStatus', 'TeamIsHome', 'HomeScore',
                   'AwayScore', 'PassingYards', 'PassingTouchdowns', 'Interceptions', 'PassingAttempts',
                   'PassingCompletions', 'RushingAttempts', 'RushingYards', 'Receptions', 'ReceivingTargets',
                   'ReceivingYards', 'ReceivingTouchdowns', 'Fumbles']

    # Filter Process, could be optimized I think
    filteredStats = {definitions: playerDictionary[definitions] for definitions in variableDef}
    if filteredStats['TeamIsHome'] is False:
        temp = filteredStats['HomeScore']
        filteredStats['HomeScore'] = filteredStats['AwayScore']
        filteredStats['AwayScore'] = temp
    del filteredStats['TeamIsHome']

    # Combining the values from the filtered dictionary to to new Key names for CSV
    variableDefKeys = ['Name', 'Team', 'Pos', 'Wk', 'Opp', 'Year', 'Status', 'TeamScore', 'OppScore', 'PassYds',
                       'PassingTD', 'Int', 'PassingAtt', 'Cmp', 'RushingAtt', 'RushingYds', 'RushingTD', 'Rec', 'Tgs',
                       'ReceivingYds', 'ReceivingTD', 'FL']
    variableDefValues = list(filteredStats.values())
    for index, value in enumerate(variableDefValues):
        if isinstance(value, float):
            variableDefValues[index] = int(value)
        if value == '':
            variableDefValues[index] = 0
    weeklyPlayerStatsDict = dict(zip(variableDefKeys, variableDefValues))

    return weeklyPlayerStatsDict

for dictionary in dataJson:
    filteredPlayerDictionary = filterDictionary(dictionary)
    mainPlayerDataList.append(filteredPlayerDictionary)

# to csv
keys = mainPlayerDataList[0].keys()
with open('player_weekly_data.csv', 'w', encoding='utf8', newline='') as output_file:
    fc = csv.DictWriter(output_file, fieldnames=mainPlayerDataList[0].keys())
    fc.writeheader()
    fc.writerows(mainPlayerDataList)