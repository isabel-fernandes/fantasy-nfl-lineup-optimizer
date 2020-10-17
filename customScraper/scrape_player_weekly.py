import csv
import requests

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
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/85.0.4183.121 Safari/537.36',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://fantasydata.com',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://fantasydata.com/nfl/fantasy-football-leaders?season=2019&seasontype=1&scope=2&subscope=1'
               '&scoringsystem=2&startweek=1&endweek=17&aggregatescope=1&range=1',
    'accept-language': 'en-US,en;q=0.9,es-US;q=0.8,es;q=0.7,ja;q=0.6,es-419;q=0.5',
}

data = {
    'sort': 'FantasyPointsPPR-desc',
    'pageSize': '2000',
    'group': '',
    'filter': '',
    'filters.position': '',
    'filters.team': '',
    'filters.teamkey': '',
    'filters.season': '',
    'filters.seasontype': '1',
    'filters.cheatsheettype': '',
    'filters.scope': '2',
    'filters.subscope': '1',
    'filters.redzonescope': '',
    'filters.scoringsystem': '2',
    'filters.leaguetype': '',
    'filters.searchtext': '',
    'filters.week': '',
    'filters.startweek': '',
    'filters.endweek': '',
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

def getRawData(week, year):
    data['filters.startweek'] = week
    data['filters.endweek'] = week
    data['filters.season'] = year

    response = requests.post('https://fantasydata.com/NFL_FantasyStats/FantasyStats_Read', headers=headers,
                             cookies=cookies, data=data)
    return response.json()['Data']


def filterData(raw_player_data):
    mainPlayerDataList = []
    for player_weekly_data in raw_player_data:
        filtered_player_dictionary = filterDictionary(player_weekly_data)
        mainPlayerDataList.append(filtered_player_dictionary)
    return mainPlayerDataList


# TODO: See if there is a way to optimize
def filterDictionary(player_weekly_data):
    # Keys we will filter for
    variable_def = ['Name', 'Team', 'Position', 'Week', 'Opponent', 'Season', 'GameStatus', 'TeamIsHome', 'HomeScore',
                    'AwayScore', 'PassingYards', 'PassingTouchdowns', 'Interceptions', 'PassingAttempts',
                    'PassingCompletions', 'RushingAttempts', 'RushingYards', 'RushingTouchdowns', 'Receptions',
                    'ReceivingTargets','ReceivingYards', 'ReceivingTouchdowns', 'Fumbles']

    # Filter Process, could be optimized I think
    filtered_stats = {definitions: player_weekly_data[definitions] for definitions in variable_def}
    if filtered_stats['TeamIsHome'] is False:
        filtered_stats['HomeScore'], filtered_stats['AwayScore'] = filtered_stats['AwayScore'], filtered_stats['HomeScore']
    del filtered_stats['TeamIsHome']

    # Combining the values from the filtered dictionary to to new Key names for CSV
    variable_def_keys = ['Name', 'Team', 'Pos', 'Wk', 'Opp', 'Year', 'Status', 'TeamScore', 'OppScore',
                         'PassYds', 'PassingTD', 'Int', 'PassingAtt', 'Cmp', 'RushingAtt', 'RushingYds',
                         'RushingTD', 'Rec', 'Tgs', 'ReceivingYds', 'ReceivingTD', 'FL']
    variable_def_values = list(filtered_stats.values())
    for index, value in enumerate(variable_def_values):
        if isinstance(value, float):
            variable_def_values[index] = int(value)
        if value == '':
            variable_def_values[index] = 0
    return dict(zip(variable_def_keys, variable_def_values))


def makeCSV(filtered_player_weekly, name):
    with open(name, 'w', encoding='utf8', newline='') as output_file:
        fc = csv.DictWriter(output_file, fieldnames=filtered_player_weekly[0].keys())
        fc.writeheader()
        fc.writerows(filtered_player_weekly)


raw_players_weekly_data = getRawData(6, 2019)
player_Weekly_Data = filterData(raw_players_weekly_data)
makeCSV(player_Weekly_Data, 'player_weekly_data.csv')
