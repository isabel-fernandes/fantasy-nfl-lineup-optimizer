import requests
import pandas as pd

swid      = "{40B9D2AC-8259-40F2-8AFE-86EDEDCD922D}"
espn_s2   = "AECAPDqT2e7%2FoyaJeZNbDG%2BElxrjrSpC2pbLhJykHyreCK8ftve35a0z8qC8UMSV0xGdYK1OqJNkqVLGzgHj6p7H%2BtApSKbq%2FAm8Cy9xe6BqAQHsPHrFXahQzsyvug2XiTnqEeAr3aKCujHxypS2x5cbQ0OD4bIeidnPY%2FnpPwAamLogo5FA4AOgROMc%2FdoJ4IXB7RFMUJRHgGf6IeOgZCxyCOO88xtc2hYJMZIAAf4q0rOcn5rlX13QBb2DVh%2FQNl4%3D"
league_id = 1141426
season    = 2019

savepath = "../data/espn_projections/espn_proj_{}.csv".format(season)

slotcodes = {
    0 : 'QB', 2 : 'RB', 4 : 'WR',
    6 : 'TE', 16: 'Def', 17: 'K',
    20: 'Bench', 21: 'IR', 23: 'Flex'
}

url = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons/' + \
      str(season) + '/segments/0/leagues/' + str(league_id) + \
      '?view=mMatchup&view=mMatchupScore'

df = []
print('Week ', end='')
for week in range(1, 17):
    print(week, end=' ')

    r = requests.get(url,
                     params={'scoringPeriodId': week},
                     cookies={"SWID": swid, "espn_s2": espn_s2})
    d = r.json()

    for tm in d['teams']:
        tmid = tm['id']
        for p in tm['roster']['entries']:
            name = p['playerPoolEntry']['player']['fullName']
            slot = p['lineupSlotId']
            pos  = slotcodes[slot]

            # injured status (need try/exc bc of D/ST)
            inj = 'NA'
            try:
                inj = p['playerPoolEntry']['player']['injuryStatus']
            except:
                pass

            # projected/actual points
            proj, act = None, None
            for stat in p['playerPoolEntry']['player']['stats']:
                if stat['scoringPeriodId'] != week:
                    continue
                if stat['statSourceId'] == 0:
                    act = stat['appliedTotal']
                elif stat['statSourceId'] == 1:
                    proj = stat['appliedTotal']

            df.append([
                week, tmid, name, slot, pos, inj, proj, act
            ])
print('\nComplete.')

df = pd.DataFrame(df,
                    columns=['Week', 'Team', 'Player', 'Slot',
                             'Pos', 'Status', 'Proj', 'Actual'])

def export_data(df, savepath):
    rename_dict = {
        "Player": "Name",
        "Proj": "proj_espn_ppr",
        "Actual": "actual_espn_ppr"
    }

    status_relabel_map = {
        "QUESTIONABLE": "Q",
        "ACTIVE": 0,
        "OUT": "O",
        "SUSPENSION": "O"
    }

    df = df.rename(columns=rename_dict)
    df["Status"] = df["Status"].replace(status_relabel_map)

    keep_cols = ["Week", "Name", "Pos", "Status", "proj_espn_ppr", "actual_espn_ppr"]
    df = df[keep_cols]

    df["year"] = season

    df.to_csv(savepath, index=False)

export_data(df, savepath)
